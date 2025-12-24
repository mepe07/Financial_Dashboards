from decimal import Decimal
from collections import defaultdict
import sys
import os

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
    if not nif: return False
    nif = str(nif).strip()
    if not nif.isdigit() or len(nif) != DIGITOS_NIF:
        return False
    return nif[-1] == calcular_digito_controlo(nif[:DIGITOS_CONTROLO])

def valida_iban(iban: str) -> bool:
    """Valida um IBAN usando o algoritmo Modulo 97-10 (PT50)."""
    if not iban: return False
    
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
# 2. FUNÇÃO PRINCIPAL DE VALIDAÇÃO
# ==============================================================================

def validar_dados(lista_dados_geral: list) -> list:
    """
    Recebe uma lista de dados (lista de dicionários vinda do modulo de leitura).
    Agrupa por 'Origem' e valida.
    
    Returns:
        list: Uma lista com os nomes dos ficheiros inválidos.
    """
    
    lista_ficheiros_invalidos = []

    # 1. AGRUPAR DADOS POR 'ORIGEM'
    dados_por_ficheiro = defaultdict(list)
    
    for linha in lista_dados_geral:
        # Usa o campo 'Origem' que foi adicionado na leitura
        origem = linha.get("Origem", "Desconhecido")
        dados_por_ficheiro[origem].append(linha)
    
    # 2. ITERAR SOBRE CADA FICHEIRO ENCONTRADO
    for nome_ficheiro, lista_dados in dados_por_ficheiro.items():
        
        ficheiro_atual_valido = True
        
        # --- PRÉ-PROCESSAMENTO ---
        contadores_tipo = {'1': 0, '2': 0, '9': 0}
        soma_real_valor = Decimal(0)
        valor_total_header = None
        
        for linha in lista_dados:
            tipo = linha.get("Tipo Registo")
            if tipo in contadores_tipo:
                contadores_tipo[tipo] += 1
            
            if tipo == '1':
                try:
                    valor_total_header = Decimal(linha.get("Valor total"))
                except: pass 

            if tipo == '2':
                try:
                    soma_real_valor += Decimal(linha.get("Valor"))
                except: pass

        # --- VALIDAÇÃO ESTRUTURAL ---
        # Tem de ter exatamente 1 cabeçalho, 1 rodapé e pelo menos 1 transação
        if contadores_tipo['1'] != 1:
            ficheiro_atual_valido = False
        
        if contadores_tipo['9'] != 1:
            ficheiro_atual_valido = False

        if contadores_tipo['2'] < 1:
            ficheiro_atual_valido = False
        
        # Se estrutura falhar, marca logo como inválido e passa para o próximo
        if not ficheiro_atual_valido:
            lista_ficheiros_invalidos.append(nome_ficheiro)
            continue 

        # --- VALIDAÇÃO DE CONTEÚDO (LINHA A LINHA) ---
        contador_ops = 0 
        desc_base = None 

        for i, linha in enumerate(lista_dados):
            tipo = linha.get("Tipo Registo")
            
            # >>>> TIPO 1 (Cabeçalho)
            if tipo == "1":
                if not valida_nif(linha.get("NIF entidade")):
                    ficheiro_atual_valido = False
                
                val_str = str(linha.get("Valor total"))
                if len(val_str) != 14:
                    ficheiro_atual_valido = False
                
                if valor_total_header is not None and valor_total_header != soma_real_valor:
                    ficheiro_atual_valido = False

            # >>>> TIPO 2 (Transações)
            elif tipo == '2':
                contador_ops += 1
                
                # Sequência
                num_op = linha.get("Nº operação")
                esperado = str(contador_ops).zfill(3)
                if num_op != esperado:
                    ficheiro_atual_valido = False

                # NIF e IBAN
                if not valida_iban(linha.get("IBAN")):
                    ficheiro_atual_valido = False
                
                if not valida_nif(linha.get("NIF Cliente")):
                    ficheiro_atual_valido = False

                # Descrição
                desc = linha.get("Descrição", "").strip()
                if contador_ops == 1:
                    desc_base = desc
                elif desc != desc_base:
                    ficheiro_atual_valido = False

            # >>>> TIPO 9 (Rodapé)
            elif tipo == '9':
                try:
                    val_footer = Decimal(linha.get("Valor total"))
                    qtd_footer = int(linha.get("Qtd Transações"))
                    
                    if val_footer != soma_real_valor:
                        ficheiro_atual_valido = False
                    
                    if qtd_footer != contadores_tipo['2']:
                        ficheiro_atual_valido = False
                except:
                    ficheiro_atual_valido = False

        # Se após todas as verificações o ficheiro não for válido, adiciona à lista
        if not ficheiro_atual_valido:
            lista_ficheiros_invalidos.append(nome_ficheiro)

    return lista_ficheiros_invalidos

# ==============================================================================
# 3. MODO DE EXECUÇÃO DIRETA (OUTPUT SIMPLIFICADO)
# ==============================================================================

if __name__ == "__main__":
    # Garante que encontra o módulo vizinho
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    if diretorio_atual not in sys.path:
        sys.path.insert(0, diretorio_atual)

    try:
        from leitura_ps2 import ler_ficheiros_ps2
        
        # Lê os dados
        dados = ler_ficheiros_ps2()
        
        if dados:
            # Valida e imprime APENAS a lista (ex: ['ficheiro1.ps2', 'ficheiro2.ps2'])
            ficheiros_invalidos = validar_dados(dados)
            print(ficheiros_invalidos)
        else:
            # Se não houver dados, imprime lista vazia
            print([])

    except Exception:
        # Em caso de erro de importação ou outro, imprime lista vazia para não quebrar scripts
        print([])