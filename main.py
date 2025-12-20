from src import ler_ficheiro_ps2, ler_ficheiros_ps2, converterParaPandas, validar_dados
import sys

def main():    

    try:

               
        # Chamar função que lê todos os ficheiros ps2
        lista_dados = ler_ficheiros_ps2()

        if not lista_dados:
            print("Nenhum ficheiro ps2 encontrado")
            return
        
        dados_validados = validar_dados(lista_dados)

        pacote_tabelas = converterParaPandas(lista_dados)
        df_cabecalho = pacote_tabelas["cabecalho"]
        df_movimentos = pacote_tabelas["movimentos"]
        df_rodape = pacote_tabelas["rodape"]

        # Converter dados retornados para uma tabela com recurso ao Pandas
        # df_Pandas = converterParaPandas(lista_dados)
        # df_cabecalho = df_Pandas["cabecalho"]
        # df_movimentos = df_Pandas["movimentos"]
        # df_rodape = df_Pandas["rodape"]

        print("\n=== Tabela: Cabeçalhos ===")
        if not df_cabecalho.empty:
            print(df_cabecalho)

        print("\n=== Tabela: Movimentos ===")
        if not df_movimentos.empty:
            print(df_movimentos)

        print("\n=== Tabela: Movimentos ===")
        if not df_rodape.empty:
            print(df_rodape)

        # print(df_cabecalho)
        # print()
        # print(df_movimentos)
        # print()
        # print(df_rodape)


        # print("--- Tipos de Dados (Verificação) ---")
        # print(df_cabecalho.dtypes)
        

         #Teste do leitura_ps2.py
        # for registo in lista_dados:
        #     print("NOVO REGISTO")
        #     print("")
        #     for chave, valor in registo.items():
        #         print(f"{chave}: {valor}")
        #         print("")

    except FileNotFoundError as e:
        print(f"Ficheiro não encontrado: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
