"""
# Módulo de Leitura PS2 (leitura_ps2.py)

Este módulo é responsável pela camada de acesso aos dados (Data Access Layer).
Ele abstrai a localização dos ficheiros no sistema de ficheiros e realiza o *parsing*
do formato posicional (largura fixa) dos ficheiros `.ps2` para estruturas de dados Python (dicionários).

## Funcionalidades
* **Localização Dinâmica:** Encontra a pasta `data` independentemente do sistema operativo.
* **Leitura Individual:** Processa um único ficheiro e converte linhas de texto em registos estruturados.
* **Leitura em Lote:** Encontra e processa todos os ficheiros `.ps2` disponíveis.
* **Enriquecimento:** Adiciona metadados (como o nome do ficheiro de origem) a cada registo.
"""

from pathlib import Path

def obter_path_data() -> Path:
    """
    Calcula e retorna o caminho absoluto para a pasta 'data' do projeto.
    
    A função navega na árvore de diretorias a partir da localização deste script 
    (`src/leitura_ps2.py`) para encontrar a raiz do projeto e, consequentemente, a pasta `data`.

    Returns:
        Path: Objeto `pathlib.Path` que aponta para a pasta de dados.
    """
    # 1. __file__ é o caminho deste ficheiro (src/leitura_ps2.py)
    # 2. .parent é a pasta onde ele está (src)
    # 3. .parent.parent é a raiz do projeto (onde está data)
    raiz_projeto = Path(__file__).parent.parent
    path_data = raiz_projeto / 'data'
    return path_data

def ler_ficheiro_ps2(nome_ficheiro: str) -> list:
    """
    Lê um ficheiro `.ps2` específico e converte o seu conteúdo numa lista de dicionários.

    Realiza o *parsing* das linhas baseado no primeiro caracter (Tipo de Registo):
    * **Tipo 1 (Cabeçalho):** Extrai Data, Entidade, NIF, Valor Total e Quantidade.
    * **Tipo 2 (Transação):** Extrai Operação, IBAN (adiciona prefixo PT50), NIF Cliente, Valor e Descrição.
    * **Tipo 9 (Rodapé):** Extrai Totais de controlo.

    Args:
        nome_ficheiro (str): O nome do ficheiro (ex: 'DD_2025_01.ps2'). O ficheiro deve estar dentro da pasta `data`.

    Returns:
        list: Uma lista de dicionários, onde cada dicionário representa uma linha processada.
    
    Raises:
        FileNotFoundError: Se o ficheiro indicado não existir na pasta `data`.
    """
    pasta_dados = obter_path_data()
    caminho_completo = pasta_dados / nome_ficheiro

    if not caminho_completo.exists():
        raise FileNotFoundError(f"O ficheiro não foi encontrado: {caminho_completo}")

    lista_dados = []

    # Abrir o ficheiro (modo 'r' para texto, utf-8 para caracteres portugueses)
    with open(caminho_completo, 'r', encoding='utf-8') as f:
        # Leitura linha a linha
        for linha in f:
            linha = linha.rstrip('\n') # Remove quebras de linha

            # Caso a linha esteja vazia, ignora
            if not linha:
                continue
            
            dados_linha = {}
            tipo_registo = linha[0]
            dados_linha["Tipo Registo"] = tipo_registo

            if tipo_registo == "1":
                # Estrutura Cabeçalho:
                # [1:9] Data | [9:39] Entidade | [52:61] NIF | [61:75] Valor | [75:] Qtd
                dados_linha.update ({
                    "Data" : linha[1:9],
                    "Entidade" : linha[9:39].strip(),
                    "NIF entidade" : linha[52:61],
                    "Valor total" : linha[61:75],
                    "Qtd Transações" : linha[75:].strip()
                })

            elif tipo_registo == "2":
                # Estrutura Transação:
                # [1:8] Tipo Op | [8:11] Nº Op | [11:32] Parte IBAN | [32:41] NIF Cli | [41:55] Valor | [55:] Desc
                dados_linha.update ({
                    "Tipo operação" : linha[1:8],
                    "Nº operação" : linha[8:11],
                    # Reconstrói o IBAN completo adicionando o código país e check digits fixos (PT50)
                    "IBAN" : "PT50" + linha[11:32],
                    "NIF Cliente" : linha[32:41],
                    "Valor" : linha[41:55],
                    "Descrição" : linha[55:].strip()
                })

            elif tipo_registo == "9":
                # Estrutura Rodapé:
                # [1:15] Valor Total | [15:] Qtd Total
                dados_linha.update ({
                    "Valor total" : linha[1:15],
                    "Qtd Transações" : linha[15:].strip()
                })

            # Adicionar o dicionario à lista
            lista_dados.append(dados_linha)
     
    return lista_dados


def ler_ficheiros_ps2() -> list:
    """
    Procura e processa todos os ficheiros com extensão `.ps2` na pasta de dados.

    Esta função atua como um agregador:
    1. Lista todos os ficheiros `.ps2`.
    2. Chama `ler_ficheiro_ps2` para cada um.
    3. Adiciona o campo `"Origem"` a cada registo para rastreabilidade.
    4. Combina todos os registos numa única lista "flat".

    Returns:
        list: Uma lista contendo todos os registos de todos os ficheiros encontrados.
              Retorna uma lista vazia se não houver ficheiros ou se ocorrerem erros de leitura.
    """

    # Encontrar a pasta com os ficheiros ps2
    pasta_dados = obter_path_data()

    # Listar ficheiros ps2 usando glob pattern
    lista_ficheiros = list(pasta_dados.glob("*.ps2"))

    todos_os_registos = []

    # Loop pelos ficheiros encontrados
    for ficheiro in lista_ficheiros:
        nome_ficheiro = ficheiro.name

        try:
            dados_ficheiro_atual = ler_ficheiro_ps2(nome_ficheiro)

            # Adicionar flag origem para saber de onde veio o dado (útil na validação)
            for registo in dados_ficheiro_atual:
                registo["Origem"] = nome_ficheiro

            # Juntar à lista principal
            todos_os_registos.extend(dados_ficheiro_atual)

        except Exception as e:
            # Em produção, isto deveria ser um log, mas print serve para consola
            print(f"Erro ao ler {nome_ficheiro}: {e}")

    return todos_os_registos

# --- BLOCO DE TESTE RÁPIDO ---
if __name__ == "__main__":
    # Este bloco só corre se executar este ficheiro diretamente.
    # Serve para testar se a leitura está a funcionar sem estragar o projeto principal.
    
    print("--- A Testar Leitura ---")
    
    # 1. Verifica se encontra a pasta
    print(f"Pasta Data localizada em: {obter_path_data()}")

    # 2. Tenta ler todos os ficheiros
    try:
        resultado = ler_ficheiros_ps2()
        print(f"Total de registos lidos: {len(resultado)}")
        
        if resultado:
            print("Exemplo do primeiro registo lido:")
            print(resultado[0])
            
    except Exception as e:
        print(f"Erro durante o teste: {e}")