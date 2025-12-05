"""
Módulo de Leitura e Processamento de Ficheiros .ps2.

Este módulo é responsável por localizar os dados de forma dinâmica
e extrair informações dos ficheiros .ps2.
"""

from pathlib import Path

def obter_path_data():
    """
    Retorna o caminho absoluto para a pasta 'data' do projeto.
    
    Funciona independentemente do sistema operativo (Windows/Linux)
    e de onde o script está a ser executado.

    Returns:
        Path: Objeto Path que aponta para a pasta 'data'.
    """
    # 1. __file__ é o caminho deste ficheiro (src/leitura_ps2.py)
    # 2. .parent é a pasta onde ele está (src)
    # 3. .parent.parent é a raiz do projeto (onde está data)
    raiz_projeto = Path(__file__).parent.parent
    path_data = raiz_projeto / 'data'
    return path_data



def ler_ficheiro_ps2(nome_ficheiro):
    """
    Lê um ficheiro .ps2 e converte o seu conteúdo num dicionário.

    Args:
        nome_ficheiro (str): O nome do ficheiro (ex: 'cliente01.ps2').

    Returns:
        dict: Dicionário com os dados processados.
              Ex: {'id': '123', 'valor': '500', ...}
    
    Raises:
        FileNotFoundError: Se o ficheiro não for encontrado na pasta data.
    """
    pasta_dados = obter_path_data()
    caminho_completo = pasta_dados / nome_ficheiro

    if not caminho_completo.exists():
        raise FileNotFoundError(f"O ficheiro não foi encontrado: {caminho_completo}")

    # Lista vazia
    lista_dados = []


    # Abrir o ficheiro (modo 'r' para texto. Se for binário real, usar 'rb')
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        # Leitura linha a linha
        for linha in f:
            linha = linha.rstrip('\n') # Remove quebras de linha

            # Caso a linha esteja vazia, ignora
            if not linha:
                continue
            
            # Dicionario novo para cada linha
            dados_linha = {}

            tipo_registo = linha[0]
            dados_linha["Tipo Registo"] = tipo_registo

            if tipo_registo == "1":
                # Cabeçalho
                dados_linha.update ({
                    "Data" : linha[1:9],
                    "Entidade" : linha[9:39].strip(),
                    "NIF entidade" : linha[39:48],
                    "Valor total" : linha[48:62],
                    "Qtd Transações" : linha[62:].strip()
                })
               

            elif tipo_registo == "2":
                # Transação
                dados_linha.update ({
                    "Tipo operação" : linha[1:8],
                    "Nº operação" : linha[8:11],
                    "IBAN" : "PT50"+linha[11:41],
                    "Valor" : linha[41:55],
                    "Descrição" : linha[55:].strip()
                })
                


            elif tipo_registo == "9":
                dados_linha.update ({
                    "Valor total" : linha[1:15],
                    "Qtd Transações" : linha[15:].strip()
                })
                


            # Adicionar o dicionario à lista
            lista_dados.append(dados_linha)
     

    return lista_dados



# --- BLOCO DE TESTE RÁPIDO ---
if __name__ == "__main__":
    # Este bloco só corre se executar este ficheiro diretamente.
    # Serve para testar se a leitura está a funcionar sem estragar o projeto.
    
    print("--- A Testar Leitura ---")
    
    # 1. Verifica se encontra a pasta
    print(f"Pasta Data localizada em: {obter_path_data()}")

    # 2. Tenta ler um ficheiro de teste (crie um ficheiro dummy para testar)
    # Exemplo: crie um ficheiro em data/teste.ps2 com o conteúdo: "ID: 99"
    try:
        resultado = ler_ficheiro_ps2("exemplo.ps2")
        # print("Dados lidos com sucesso:", resultado)
        for entrada in resultado:
            print()
            print(entrada)
            
    except Exception as e:
        print(f"Erro ao ler (normal se não criou o ficheiro ainda): {e}")