import doctest
from datetime import datetime

# --- CONSTANTES E FUNÇÕES AUXILIARES DE NIF ---

DIGITOS_CONTROLO = 8 
DIGITOS_NIF = 9

def calcular_digito_controlo(digitos: str) -> str:
    """Calcula o digito de controle de um NIF."""
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
    nif = str(nif).strip()
    if not nif.isdigit() or len(nif) != DIGITOS_NIF:
        return False
    return nif[-1] == calcular_digito_controlo(nif[:DIGITOS_CONTROLO])


# --- FUNÇÃO PRINCIPAL DE VALIDAÇÃO ---

def validar_dados(lista_dados: list) -> list:
    """
    Recebe a lista de dados bruta e valida cada entrada.
    Valida NIF e valida Ano (com tolerância em Janeiro para o ano anterior).
    """
    dados_validos = []
    
    # Obter data atual do sistema
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    print(f"\n--- A Analisar Dados ---")
    print(f"Data do Sistema: {ano_atual} (Mês: {mes_atual})")

    for i, linha in enumerate(lista_dados):
        numero_linha = i + 1
        registo_valido = True
        
        tipo = linha.get("Tipo Registo")

        # --- VALIDAÇÕES DO CABEÇALHO (TIPO 1) ---
        if tipo == "1":
            # 1. Validação do NIF
            nif_atual = linha.get("NIF entidade")
            if not valida_nif(nif_atual):
                print(f"❌ ERRO Linha {numero_linha}: NIF inválido -> '{nif_atual}'")
                registo_valido = False
            else:
                print(f"✅ Linha {numero_linha}: NIF Válido.")

            # 2. Validação do Ano com exceção de Janeiro
            data_str = linha.get("Data", "")
            
            # Precisamos garantir que temos pelo menos os 4 digitos do ano
            if len(data_str) >= 4 and data_str[:4].isdigit():
                ano_ficheiro = int(data_str[:4])
                
                # Lógica de validação do ano
                if ano_ficheiro == ano_atual:
                    print(f"✅ Linha {numero_linha}: Ano '{ano_ficheiro}' corresponde ao ano atual.")
                
                elif mes_atual == 1 and ano_ficheiro == (ano_atual - 1):
                    # Se estamos em Janeiro e o ficheiro é do ano passado -> VÁLIDO
                    print(f"✅ Linha {numero_linha}: Ano '{ano_ficheiro}' aceite (Tolerância de Janeiro aplicada).")
                
                else:
                    # Qualquer outro caso é erro
                    print(f"❌ ERRO Linha {numero_linha}: Ano incorreto. Ficheiro: '{ano_ficheiro}', Sistema: '{ano_atual}' (Mês {mes_atual})")
                    registo_valido = False
            else:
                print(f"❌ ERRO Linha {numero_linha}: Formato de data inválido.")
                registo_valido = False

        # Se passou em todos os testes, adiciona à lista final
        if registo_valido:
            dados_validos.append(linha)

    return dados_validos


# --- BLOCO DE TESTE ---
if __name__ == "__main__":
    
    # Para testar, vamos simular os anos baseados no sistema atual
    agora_teste = datetime.now()
    ano_sys = agora_teste.year
    ano_anterior = ano_sys - 1
    ano_futuro = ano_sys + 1

    print(f"--- A correr testes (Ano base sistema: {ano_sys}) ---")
    
    # ATENÇÃO: O resultado deste teste depende do mês em que você está a executar o código!
    # Se correr isto em Janeiro, o 'ano_anterior' vai dar ✅. 
    # Se correr em Fevereiro ou depois, o 'ano_anterior' vai dar ❌.

    dados_exemplo = [
        # 1. Ano Atual (Sempre Válido)
        {
            'Tipo Registo': '1', 
            'Data': f'{ano_sys}0501',  
            'Entidade': 'Empresa Atual', 
            'NIF entidade': '501442600'
        },
        # 2. Ano Anterior (Válido APENAS se estivermos em Janeiro)
        {
            'Tipo Registo': '1', 
            'Data': f'{ano_anterior}1231',   
            'Entidade': 'Empresa Ano Passado', 
            'NIF entidade': '501442600'
        }, 
        # 3. Ano Futuro (Sempre Inválido)
        {
            'Tipo Registo': '1', 
            'Data': f'{ano_futuro}0101',
            'Entidade': 'Empresa Futuro', 
            'NIF entidade': '501442600'
        }
    ]

    resultado = validar_dados(dados_exemplo)
    
    print("\n--- Resultado Final ---")
    print(f"Total registos aceites: {len(resultado)}")