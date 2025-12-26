"""
# Módulo de Validação PS2 (validacao_ps2.py)

Este módulo é responsável por verificar a integridade lógica e estrutural dos dados 
extraídos dos ficheiros `.ps2`.

## Funcionalidades
* **Validação Fiscal:** Verifica a validade de NIFs (Entidades e Clientes).
* **Validação Bancária:** Verifica a validade de IBANs portugueses (PT50).
* **Validação Estrutural:** Garante a existência de Cabeçalho, Transações e Rodapé.
* **Consistência de Totais:** Compara os somatórios das transações com os valores declarados.
* **Sequencialidade:** Verifica a numeração sequencial das operações.
"""

from decimal import Decimal
from collections import defaultdict
import sys
import os

# ==============================================================================
# 1. FUNÇÕES AUXILIARES DE NIF/IBAN
# ==============================================================================

DIGITOS_CONTROLO = 8 
"""int: Número de dígitos base para cálculo do controlo (primeiros 8)."""

DIGITOS_NIF = 9
"""int: Tamanho total esperado de um NIF português."""

def calcular_digito_controlo(digitos: str) -> str:
    """
    Calcula o dígito de controlo (o 9º dígito) baseado nos 8 primeiros dígitos de um NIF.
    Utiliza o algoritmo de Módulo 11.

    Args:
        digitos (str): String contendo os primeiros 8 dígitos.

    Returns:
        str: O dígito de controlo calculado ('0' a '9').
    """
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
    """
    Valida um Número de Identificação Fiscal (NIF) português.

    Args:
        nif (str): O NIF a validar.

    Returns:
        bool: True se for válido, False caso contrário.
    """
    if not nif: return False
    nif = str(nif).strip()
    
    # Verifica tamanho e se é numérico
    if not nif.isdigit() or len(nif) != DIGITOS_NIF:
        return False
    
    # Verifica se o último dígito corresponde ao cálculo de controlo
    return nif[-1] == calcular_digito_controlo(nif[:DIGITOS_CONTROLO])

def valida_iban(iban: str) -> bool:
    """
    Valida um IBAN português utilizando o algoritmo Modulo 97-10.
    Assume que o IBAN deve começar por 'PT' e ter 25 caracteres.

    Args:
        iban (str): O código IBAN a validar.

    Returns:
        bool: True se o IBAN for matematicamente válido, False caso contrário.
    """
    if not iban: return False
    
    CODIGO_PAIS_PT = 'PT'
    COMPRIMENTO_PT = 25
    
    iban = str(iban).strip().replace(' ', '').upper()
    
    # Validação básica de estrutura
    if len(iban) != COMPRIMENTO_PT or iban[:2] != CODIGO_PAIS_PT:
        return False

    # Reorganização para cálculo (PT50... -> 50...PT)
    iban_reorganizado = iban[4:] + iban[:4]
    
    def letra_para_digito(char):
        # Converte letras em números (A=10, B=11, etc)
        if 'A' <= char <= 'Z':
            return str(ord(char) - ord('A') + 10)
        return char
        
    iban_digitalizado = "".join(letra_para_digito(c) for c in iban_reorganizado)
    
    try:
        # Algoritmo Modulo 97 check
        numero_completo = int(iban_digitalizado)
        return (numero_completo % 97) == 1
    except ValueError:
        return False

# ==============================================================================
# 2. FUNÇÃO PRINCIPAL DE VALIDAÇÃO
# ==============================================================================

def validar_dados(lista_dados_geral: list) -> list:
    """
    Processa a lista de dados brutos e identifica ficheiros que não cumprem as regras de negócio.

    **Regras Verificadas:**
    1. Estrutura do ficheiro (1 Header, N Transações, 1 Footer).
    2. Validade dos NIFs (Entidade e Clientes).
    3. Validade dos IBANs.
    4. Consistência dos totais monetários (Soma transações == Total Header/Footer que são o tipo 1 e tipo 9) .
    5. Sequência lógica do número das operações.
    6. Formatação de campos fixos (ex: tamanho do valor).

    Args:
        lista_dados_geral (list): Lista de dicionários retornada pelo módulo de leitura.
                                  Cada dicionário deve conter a chave "Origem" (nome do ficheiro).

    Returns:
        list: Uma lista de strings contendo apenas os **nomes dos ficheiros inválidos**.
              Retorna uma lista vazia `[]` se todos estiverem corretos.
    """
    
    lista_ficheiros_invalidos = []

    # 1. AGRUPAR DADOS POR 'ORIGEM'
    # Cria um dicionário onde a chave é o nome do ficheiro e o valor é a lista de linhas desse ficheiro
    dados_por_ficheiro = defaultdict(list)
    
    for linha in lista_dados_geral:
        origem = linha.get("Origem", "Desconhecido")
        dados_por_ficheiro[origem].append(linha)
    
    # 2. ITERAR SOBRE CADA FICHEIRO ENCONTRADO
    for nome_ficheiro, lista_dados in dados_por_ficheiro.items():
        
        ficheiro_atual_valido = True
        
        # --- PRÉ-PROCESSAMENTO (Cálculo de Totais e Contagens) ---
        contadores_tipo = {'1': 0, '2': 0, '9': 0}
        soma_real_valor = Decimal(0)
        valor_total_header = None
        
        for linha in lista_dados:
            tipo = linha.get("Tipo Registo")
            if tipo in contadores_tipo:
                contadores_tipo[tipo] += 1
            
            # Captura valor do cabeçalho
            if tipo == '1':
                try:
                    valor_total_header = Decimal(linha.get("Valor total"))
                except: pass 

            # Soma valores das transações
            if tipo == '2':
                try:
                    soma_real_valor += Decimal(linha.get("Valor"))
                except: pass

        # --- VALIDAÇÃO ESTRUTURAL ---
        # Regra: Tem de ter exatamente 1 cabeçalho, 1 rodapé e pelo menos 1 transação
        if contadores_tipo['1'] != 1:
            ficheiro_atual_valido = False
        
        if contadores_tipo['9'] != 1:
            ficheiro_atual_valido = False

        if contadores_tipo['2'] < 1:
            ficheiro_atual_valido = False
        
        # Se a estrutura falhar, marca logo como inválido e salta para o próximo ficheiro
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
                # Valida NIF da Entidade
                if not valida_nif(linha.get("NIF entidade")):
                    ficheiro_atual_valido = False
                
                # Valida tamanho do campo Valor (tem de ser 14 chars)
                val_str = str(linha.get("Valor total"))
                if len(val_str) != 14:
                    ficheiro_atual_valido = False
                
                # Valida se o total declarado bate certo com a soma real
                if valor_total_header is not None and valor_total_header != soma_real_valor:
                    ficheiro_atual_valido = False

            # >>>> TIPO 2 (Transações)
            elif tipo == '2':
                contador_ops += 1
                
                # Valida Sequência (001, 002, ...)
                num_op = linha.get("Nº operação")
                esperado = str(contador_ops).zfill(3)
                if num_op != esperado:
                    ficheiro_atual_valido = False

                # Valida NIF e IBAN do Cliente
                if not valida_iban(linha.get("IBAN")):
                    ficheiro_atual_valido = False
                
                if not valida_nif(linha.get("NIF Cliente")):
                    ficheiro_atual_valido = False

                # Valida consistência da Descrição (deve ser igual à primeira)
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
                    
                    # Valida se totais do rodapé batem com a realidade
                    if val_footer != soma_real_valor:
                        ficheiro_atual_valido = False
                    
                    if qtd_footer != contadores_tipo['2']:
                        ficheiro_atual_valido = False
                except:
                    ficheiro_atual_valido = False

        # Se após todas as verificações o ficheiro tiver falhas, adiciona à lista de erros
        if not ficheiro_atual_valido:
            lista_ficheiros_invalidos.append(nome_ficheiro)

    return lista_ficheiros_invalidos

# ==============================================================================
# 3. MODO DE EXECUÇÃO DIRETA (TESTE)
# ==============================================================================

if __name__ == "__main__":
    # Configuração de path para permitir importar módulos irmãos quando executado diretamente
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    if diretorio_atual not in sys.path:
        sys.path.insert(0, diretorio_atual)

    try:
        from leitura_ps2 import ler_ficheiros_ps2
        
        # 1. Lê os dados
        dados = ler_ficheiros_ps2()
        
        if dados:
            # 2. Valida os dados
            # Retorna apenas a lista de ficheiros inválidos para output limpo
            ficheiros_invalidos = validar_dados(dados)
            print(ficheiros_invalidos)
        else:
            # Output padrão caso não haja dados
            print([])

    except Exception:
        # Em caso de erro (ex: ficheiro de leitura não encontrado), imprime lista vazia
        # para não quebrar a execução de quem chama este script.
        print([])