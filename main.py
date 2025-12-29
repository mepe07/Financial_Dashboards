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

        print("\n=== Tabela: Cabeçalhos ===")
        if not df_cabecalho.empty:
            print(df_cabecalho)

        print("\n=== Tabela: Movimentos ===")
        if not df_movimentos.empty:
            print(df_movimentos)

        print("\n=== Tabela: Movimentos ===")
        if not df_rodape.empty:
            print(df_rodape)


    except FileNotFoundError as e:
        print(f"Ficheiro não encontrado: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()
