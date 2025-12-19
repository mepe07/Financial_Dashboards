from src import ler_ficheiro_ps2
from src import converterParaPandas
import sys

def main():

    nome_ficheiro = "exemplo.ps2"

    try:
        # Chamar função em leitura_ps2.py
        lista_dados = ler_ficheiro_ps2(nome_ficheiro)

        # Converter dados retornados para uma tabela com recurso ao Pandas
        df_Pandas = converterParaPandas(lista_dados)
        df_cabecalho = df_Pandas["cabecalho"]
        df_movimentos = df_Pandas["movimentos"]
        df_rodape = df_Pandas["rodape"]

        print(df_cabecalho)
        print()
        print(df_movimentos)
        print()
        print(df_rodape)


        # print("--- Tipos de Dados (Verificação) ---")
        # print(df_cabecalho.dtypes)
        

         #Teste do leitura_ps2.py
        for registo in lista_dados:
            print("NOVO REGISTO")
            print("")
            for chave, valor in registo.items():
                print(f"{chave}: {valor}")
                print("")

    except FileNotFoundError as e:
        print(f"Ficheiro não encontrado: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
