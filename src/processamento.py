import pandas as pd
from typing import List, Dict, Any

def converterParaPandas(lista_dicionarios: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
    """
    Converte a lista de dados brutos em DataFrames do Pandas organizados e limpos.

    Esta função recebe a lista de dicionários gerada pela leitura dos ficheiros PS2
    e realiza três operações principais:
    1.  **Separação:** Divide os dados em três tabelas distintas baseadas no `Tipo Registo` (1, 2 ou 9).
    2.  **Criação:** Instancia DataFrames do Pandas para cada tipo.
    3.  **Limpeza:** Converte strings de datas para objetos `datetime` e transforma
        valores monetários (que vêm em cêntimos/inteiros) para decimais (divisão por 100).

    Args:
        lista_dicionarios (List[Dict[str, Any]]): A lista crua contendo todos os registos
            lidos dos ficheiros. Cada item da lista é um dicionário representando uma linha do ficheiro.

    Returns:
        Dict[str, pd.DataFrame]: Um dicionário contendo as três estruturas de dados essenciais:
            
            * **`"cabecalho"`** (*pd.DataFrame*): Registos do Tipo 1 (Dados da Entidade/Ficheiro).
            * **`"movimentos"`** (*pd.DataFrame*): Registos do Tipo 2 (Detalhe de cada cobrança/cliente).
            * **`"rodape"`** (*pd.DataFrame*): Registos do Tipo 9 (Totais de controlo).

    Example:
        ```python
        dados_raw = ler_ficheiros_ps2()
        pacote = converterParaPandas(dados_raw)

        # Aceder aos movimentos
        df_mov = pacote['movimentos']
        
        # Aceder ao cabeçalho
        df_cab = pacote['cabecalho']
        ```
    """

    # Se a lista estiver vazia, retorna DataFrames vazios para garantir a estabilidade do tipo de retorno
    if not lista_dicionarios:
        return {
            "cabecalho": pd.DataFrame(),
            "movimentos": pd.DataFrame(),
            "rodape": pd.DataFrame()
        }
    
    # Criar listas temporárias para separar os tipos de registo
    lista_tipo1 = []
    lista_tipo2 = []
    lista_tipo9 = []

    # Separar os tipos de registo
    for registo in lista_dicionarios:
        # Se a chave "Tipo Registo" falhar ou não existir, assume '0' (ignorado)
        tipoReg = registo.get("Tipo Registo", '0')

        if str(tipoReg) == '1':
            lista_tipo1.append(registo)
        elif str(tipoReg) == '2':
            lista_tipo2.append(registo)
        elif str(tipoReg) == '9':
            lista_tipo9.append(registo)

    # Criar DataFrames limpos a partir das listas separadas
    df_t1 = pd.DataFrame(lista_tipo1)
    df_t2 = pd.DataFrame(lista_tipo2)
    df_t9 = pd.DataFrame(lista_tipo9)

    # --- LÓGICA DE LIMPEZA E CONVERSÃO DE TIPOS ---

    # 1. Limpeza Tabela Tipo 1 (Cabeçalho)
    if not df_t1.empty:
        # Converter string 'YYYYMMDD' para objeto datetime real
        if "Data" in df_t1.columns:
            df_t1["Data"] = pd.to_datetime(df_t1["Data"], format='%Y%m%d', errors='coerce')

        # Converter valores monetários (Ex: 1500 -> 15.00)
        if "Valor total" in df_t1.columns:
            df_t1["Valor total"] = pd.to_numeric(df_t1["Valor total"], errors='coerce') / 100

    # 2. Limpeza Tabela Tipo 2 (Movimentos)
    if not df_t2.empty:
        # Converter 'Valor' individual para float
        if 'Valor' in df_t2.columns:
            df_t2["Valor"] = pd.to_numeric(df_t2["Valor"], errors='coerce') / 100

    # 3. Limpeza Tabela Tipo 9 (Rodapé)
    if not df_t9.empty:
        # Converter totais de controlo para float
        if "Valor total" in df_t9.columns:
            df_t9["Valor total"] = pd.to_numeric(df_t9["Valor total"], errors='coerce') / 100

    return {
        "cabecalho": df_t1,
        "movimentos": df_t2,
        "rodape": df_t9
    }