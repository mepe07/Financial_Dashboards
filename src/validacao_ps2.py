import os
import doctest
from datetime import datetime
from decimal import Decimal, InvalidOperation 
from pathlib import Path
from collections import defaultdict

# ==============================================================================
# 1. FUNÇÕES AUXILIARES DE NIF/IBAN
# ==============================================================================

DIGITOS_CONTROLO = 8 
DIGITOS_NIF = 9

def calcular_digito_controlo(digitos: str) -> str:
    """Calcula o digito de controlo de um NIF."""
    if not digitos.isdigit():
        raise ValueError("Nem todos os caracteres são digitos")
    
    soma = (
        int(digitos[0]) * 9
        + int(digitos[1]) * 8
        + int(digitos[2]) * 7
        + int(digitos[3]) * 6
        + int(digitos[4]) * 5
        + int(digitos[5]) * 4
        + int(digitos[6]) * 3
        + int(digitos[7]) * 2
    )
    resto = soma % 11
    if resto == 0 or resto == 1:
        return "0"
    return str(11 - resto)

def valida_nif(nif: str) -> bool:
    """Retorna True se o NIF for válido, False caso contrário."""
    nif = str(nif).strip()
    if not nif.isdigit() or len(nif) != DIGITOS_NIF:
        return False
    return nif[-1] == calcular_digito_controlo(nif[:DIGITOS_CONTROLO])

def valida_iban(iban: str) -> bool:
    """Valida um IBAN usando o algoritmo Modulo 97-10 (PT50)."""
    CODIGO_PAIS_PT = 'PT'
    COMPRIMENTO_PT = 25
    
    iban = str(iban).strip().replace(' ', '').upper()
    
    if len(iban) != COMPRIMENTO_PT or iban[:2] != CODIGO_PAIS_PT:
        return False

    iban_reorganizado = iban[4:] + iban[:4]
    
    def letra_para_digito(char):
        if 'A' <= char <= 'Z':
            return str(ord(char) - ord('A') + 10)
        return char
        
    iban_digitalizado = "".join(letra_para_digito(c) for c in iban_reorganizado)
    
    try:
        numero_completo = int(iban_digitalizado)
        return (numero_completo % 97) == 1
    except ValueError:
        return False

# ==============================================================================
# 2. FUNÇÃO DE LEITURA (Adiciona o campo 'Origem')
# ==============================================================================

def ler_ficheiro_ps2(caminho_completo):
    """
    Lê um ficheiro .ps2 e converte numa lista de dicionários.
    ADICIONA O CAMPO 'Origem' COM O NOME DO FICHEIRO.
    """
    lista_dados = []
    
    if not os.path.exists(caminho_completo):
        raise FileNotFoundError(f"Ficheiro não encontrado: {caminho_completo}")
    
    # Extrai apenas o nome do ficheiro (ex: 'processamento_01.ps2') para usar como ID
    nome_ficheiro = os.path.basename(caminho_completo)

    with open(caminho_completo, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.rstrip('\n')
            if not linha: continue 
            
            dados_linha = {}
            # --- NOVIDADE: Identificador de Origem ---
            dados_linha["Origem"] = nome_ficheiro
            
            tipo_registo = linha[0]
            dados_linha["Tipo Registo"] = tipo_registo

            if tipo_registo == "1":
                dados_linha.update ({
                    "Data" : linha[1:9],
                    "Entidade" : linha[9:39].strip(),
                    "NIF entidade" : linha[39:48],
                    "Valor total" : linha[48:62],
                    "Qtd Transações" : linha[62:].strip()
                })

            elif tipo_registo == "2":
                parte_iban = linha[11:32]
                iban_completo = "PT50" + parte_iban

                dados_linha.update ({
                    "Tipo operação" : linha[1:8],
                    "Nº operação" : linha[8:11],
                    "IBAN" : iban_completo, 
                    "NIF Cliente" : linha[32:41],
                    "Valor" : linha[41:55],
                    "Descrição" : linha[55:].strip()
                })

            elif tipo_registo == "9":
                dados_linha.update ({
                    "Valor total" : linha[1:15],
                    "Qtd Transações" : linha[15:].strip()
                })

            lista_dados.append(dados_linha)
            
    return lista_dados

# ==============================================================================
# 3. FUNÇÃO PRINCIPAL DE VALIDAÇÃO (Suporta múltiplos ficheiros via 'Origem')
# ==============================================================================

def validar_dados(lista_dados_geral: list) -> int:
    """
    Recebe uma lista de dados (que pode conter vários ficheiros misturados).
    Agrupa por 'Origem' e valida cada grupo independentemente.
    """
    
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    # 1. AGRUPAR DADOS POR 'ORIGEM'
    # Cria um dicionário onde a chave é o nome do ficheiro e o valor é a lista das suas linhas
    dados_por_ficheiro = defaultdict(list)
    
    for linha in lista_dados_geral:
        # Se não tiver origem, assume "Desconhecido"
        origem = linha.get("Origem", "Ficheiro_Desconhecido")
        dados_por_ficheiro[origem].append(linha)
    
    todos_validos = True
    
    print(f"\n🚀 A iniciar validação de {len(dados_por_ficheiro)} origem(ns) distinta(s)...")

    # 2. ITERAR SOBRE CADA FICHEIRO ENCONTRADO
    for nome_ficheiro, lista_dados in dados_por_ficheiro.items():
        
        print(f"\n" + "="*60)
        print(f"📄 FICHEIRO: {nome_ficheiro}")
        print("="*60)
        
        ficheiro_atual_valido = True
        
        # --- PRÉ-PROCESSAMENTO (Específico para este ficheiro) ---
        contadores_tipo = {'1': 0, '2': 0, '9': 0}
        soma_real_valor = Decimal(0)
        
        mes_base = None 
        ano_base = None
        valor_total_header = None
        qtd_header = None

        for linha in lista_dados:
            tipo = linha.get("Tipo Registo")
            if tipo in contadores_tipo:
                contadores_tipo[tipo] += 1
            
            if tipo == '1':
                data_str = linha.get("Data", "")
                if len(data_str) >= 6 and data_str[:6].isdigit():
                    ano_base = data_str[:4]
                    mes_base = data_str[4:6]
                try:
                    valor_total_header = Decimal(linha.get("Valor total"))
                    qtd_header = int(linha.get("Qtd Transações"))
                except: pass 

            if tipo == '2':
                try:
                    soma_real_valor += Decimal(linha.get("Valor"))
                except: pass

        # --- VALIDAÇÃO ESTRUTURAL (Regras reiniciadas para este ficheiro) ---
        # AQUI GARANTIMOS QUE CADA 'Origem' TEM O SEU PRÓPRIO TIPO 1 E TIPO 9
        
        if contadores_tipo['1'] != 1:
            print(f"❌ ERRO ESTRUTURAL: Encontrados {contadores_tipo['1']} cabeçalhos (Tipo 1). Esperado: 1.")
            ficheiro_atual_valido = False
        
        if contadores_tipo['9'] != 1:
            print(f"❌ ERRO ESTRUTURAL: Encontrados {contadores_tipo['9']} rodapés (Tipo 9). Esperado: 1.")
            ficheiro_atual_valido = False

        if contadores_tipo['2'] < 1:
            print(f"❌ ERRO ESTRUTURAL: Ficheiro sem transações (Tipo 2).")
            ficheiro_atual_valido = False
        
        # Se estrutura falhar, não valida linhas detalhadas para não poluir o log
        if not ficheiro_atual_valido:
            todos_validos = False
            print(f"⚠️ Validação interrompida para '{nome_ficheiro}' devido a erros estruturais.")
            continue # Passa para o próximo ficheiro

        # --- VALIDAÇÃO DE CONTEÚDO (LINHA A LINHA) ---
        contador_ops = 0 
        desc_base = None 

        for i, linha in enumerate(lista_dados):
            num_linha = i + 1
            tipo = linha.get("Tipo Registo")
            
            # >>>> TIPO 1
            if tipo == "1":
                if not valida_nif(linha.get("NIF entidade")):
                    print(f"  ❌ Linha {num_linha} (T1): NIF Entidade inválido.")
                    ficheiro_atual_valido = False
                
                val_str = str(linha.get("Valor total"))
                if len(val_str) != 14:
                    print(f"  ❌ Linha {num_linha} (T1): Tamanho valor incorreto ({len(val_str)}).")
                    ficheiro_atual_valido = False
                
                # Validação Cruzada
                if valor_total_header is not None and valor_total_header != soma_real_valor:
                    print(f"  ❌ Linha {num_linha} (T1): Valor Total ({valor_total_header}) difere da soma real ({soma_real_valor}).")
                    ficheiro_atual_valido = False

            # >>>> TIPO 2
            elif tipo == '2':
                contador_ops += 1
                
                # Sequência
                num_op = linha.get("Nº operação")
                esperado = str(contador_ops).zfill(3)
                if num_op != esperado:
                    print(f"  ❌ Linha {num_linha} (T2): Nº Op incorreto ({num_op}). Esperado: {esperado}.")
                    ficheiro_atual_valido = False

                # NIF e IBAN
                if not valida_iban(linha.get("IBAN")):
                    print(f"  ❌ Linha {num_linha} (T2): IBAN inválido.")
                    ficheiro_atual_valido = False
                
                if not valida_nif(linha.get("NIF Cliente")):
                    print(f"  ❌ Linha {num_linha} (T2): NIF Cliente inválido.")
                    ficheiro_atual_valido = False

                # Descrição
                desc = linha.get("Descrição", "").strip()
                if contador_ops == 1:
                    desc_base = desc
                elif desc != desc_base:
                    print(f"  ❌ Linha {num_linha} (T2): Descrição difere das anteriores.")
                    ficheiro_atual_valido = False

            # >>>> TIPO 9
            elif tipo == '9':
                try:
                    val_footer = Decimal(linha.get("Valor total"))
                    qtd_footer = int(linha.get("Qtd Transações"))
                    
                    if val_footer != soma_real_valor:
                        print(f"  ❌ Linha {num_linha} (T9): Valor Rodapé difere da soma.")
                        ficheiro_atual_valido = False
                    
                    if qtd_footer != contadores_tipo['2']:
                        print(f"  ❌ Linha {num_linha} (T9): Qtd Rodapé difere da contagem.")
                        ficheiro_atual_valido = False
                except:
                    print(f"  ❌ Linha {num_linha} (T9): Erro de formato no rodapé.")
                    ficheiro_atual_valido = False

        if ficheiro_atual_valido:
            print(f"✅ STATUS: VÁLIDO")
        else:
            print(f"❌ STATUS: INVÁLIDO")
            todos_validos = False

    # --- RESULTADO GLOBAL ---
    print("\n" + "="*60)
    if todos_validos:
        print("🎉 TODOS OS FICHEIROS FORAM APROVADOS.")
        return 1
    else:
        print("⚠️ ALGUNS FICHEIROS CONTÊM ERROS.")
        return 0

# ==============================================================================
# 4. EXECUÇÃO
# ==============================================================================

if __name__ == "__main__":
    
    # 1. Localizar a pasta 'data'
    raiz_projeto = Path(__file__).parent.parent 
    pasta_data = raiz_projeto / 'data'
    if not pasta_data.exists(): pasta_data = Path(__file__).parent / 'data'

    if not pasta_data.exists():
        print("❌ Pasta 'data' não encontrada.")
    else:
        # 2. Ler TUDO para uma única lista gigante (simulando o seu cenário)
        lista_gigante_misturada = []
        ficheiros = [f for f in os.listdir(pasta_data) if f.endswith('.ps2')]
        
        for f in ficheiros:
            # A função de leitura agora adiciona "Origem": "nome_do_ficheiro"
            dados = ler_ficheiro_ps2(pasta_data / f)
            lista_gigante_misturada.extend(dados)
            
        print(f"📥 Total de linhas lidas (misturadas): {len(lista_gigante_misturada)}")
        
        # 3. Validar a lista gigante
        # A função validar_dados agora é inteligente e separa por "Origem"
        validar_dados(lista_gigante_misturada)