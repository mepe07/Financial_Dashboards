import pandas as pd
from typing import List, Dict, Any


def converterParaPandas(lista_dicionarios: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
    """
    Converte uma lista de dicionários num DataFrame Pandas e faz a limpeza básica.
    
    Args:
        lista_dicionarios: A lista vinda da leitura do ficheiro.
        
    Returns:
        pd.DataFrame: O dataframe pronto a ser usado no Shiny.
    """

    # Se a lista estiver vazia, cria uma DataFrame vazio para não dar erro
    if not lista_dicionarios:
        return pd.DataFrame()
    
    # Criar listas temporárias para separar os tipos de registo
    lista_tipo1 = []
    lista_tipo2 = []
    lista_tipo9 = []

    # Separar os tipos de registo
    for registo in lista_dicionarios:
        # Se falhar leitura, assume 0
        tipoReg = registo.get("Tipo Registo", '0')

        if str(tipoReg) == '1':
            lista_tipo1.append(registo)
        if str(tipoReg) == '2':
            lista_tipo2.append(registo)
        if str(tipoReg) == '9':
            lista_tipo9.append(registo)

    # Criar DataFrames limpos
    df_t1 = pd.DataFrame(lista_tipo1)
    df_t2 = pd.DataFrame(lista_tipo2)
    df_t9 = pd.DataFrame(lista_tipo9)

    
    # Limpeza tabela tipo 1
    if not df_t1.empty:
        # Converter string da data para Data real
        if "Data" in df_t1.columns:
            df_t1["Data"] = pd.to_datetime(df_t1["Data"], format='%Y%m%d', errors='coerce')

        # Converter o valor total para numero, assumindo 2 casas decimais
        if "Valor total" in df_t1.columns:
            df_t1["Valor total"] = pd.to_numeric(df_t1["Valor total"], errors='coerce') / 100

    # Limpeza tipo 2
    if not df_t2.empty:
        # Converter 'Valor' para numero
        if 'Valor' in df_t2.columns:
            df_t2["Valor"] = pd.to_numeric(df_t2["Valor"], errors='coerce') / 100

    # Limpeza tipo 9
    if not df_t9.empty:
        if "Valor total" in df_t9.columns:
            df_t9["Valor total"] = pd.to_numeric(df_t9["Valor total"], errors='coerce') / 100

    return {
        "cabecalho": df_t1,
        "movimentos": df_t2,
        "rodape": df_t9
    }
