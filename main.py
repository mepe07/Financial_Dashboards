from src import ler_ficheiro_ps2, validar_dados
import sys

def main():

    nome_ficheiro = "exemplo.ps2"

    try:
        # Chamar função em leitura_ps2.py
        lista_dados = ler_ficheiro_ps2(nome_ficheiro)

        dados_validados = validar_dados(lista_dados)

        #for registo in lista_dados:
        #    print("NOVO REGISTO")
        #    print("")

        #    for chave, valor in registo.items():
        #        print(f"{chave}: {valor}")
        #        print("")

    except FileNotFoundError as e:
        print(f"Ficheiro não encontrado: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()