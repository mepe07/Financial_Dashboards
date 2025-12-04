import doctest
from datetime import datetime
from decimal import Decimal, InvalidOperation # Usar Decimal para precisão monetária

# --- CONSTANTES E FUNÇÕES AUXILIARES DE NIF (SEM ALTERAÇÕES) ---

DIGITOS_CONTROLO = 8 
DIGITOS_NIF = 9
# ... (Funções calcular_digito_controlo e valida_nif inalteradas)
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


# --- FUNÇÃO PRINCIPAL DE VALIDAÇÃO (COM VALIDAÇÃO DE CONSISTÊNCIA DE VALOR) ---

def validar_dados(lista_dados: list) -> list:
    """
    Recebe a lista de dados e valida cada entrada.
    Inclui o cálculo da soma dos campos 'Valor' (Tipo 2) para validar o 'Valor total' (Tipo 1).
    """
    dados_validos = []
    
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    print(f"\n--- 📅 Configuração do Sistema ---")
    print(f"Data do Sistema: {ano_atual} (Mês: {mes_atual})")

    # -----------------------------------------------------
    # --- 1. VALIDAÇÃO ESTRUTURAL (CONTAGEM DE TIPOS E CÁLCULO DA SOMA REAL) ---
    # -----------------------------------------------------
    
    contadores_tipo = {'1': 0, '2': 0, '9': 0}
    soma_real_valor = Decimal(0)
    erros_tipo2_valor = False
    
    # 1.1. Passo de Contagem e SOMA
    for i, linha in enumerate(lista_dados):
        tipo = linha.get("Tipo Registo")
        if tipo in contadores_tipo:
            contadores_tipo[tipo] += 1
        
        # CÁLCULO DA SOMA REAL
        if tipo == '2':
            valor_str = linha.get("Valor")
            if valor_str is None:
                print(f"❌ ERRO Linha {i+1}: Registo Tipo 2 sem campo 'Valor'.")
                erros_tipo2_valor = True
            else:
                try:
                    # Tenta converter o valor para Decimal para evitar erros de precisão com floats
                    soma_real_valor += Decimal(valor_str)
                except InvalidOperation:
                    print(f"❌ ERRO Linha {i+1}: Valor Tipo 2 ('{valor_str}') **não é um número válido**.")
                    erros_tipo2_valor = True
            
    # Guarda a contagem real de Tipo 2 para uso posterior na validação de conteúdo
    contagem_real_tipo2 = contadores_tipo['2']
            
    # 1.2. Aplicação das Regras e Prints Estruturais
    print("\n--- 🏗️ Validação Estrutural (Regras de Contagem e Soma) ---")
    validacao_estrutural_ok = True
    
    # ... (Regras estruturais: 1, 9, 2 inalteradas)
    if contadores_tipo['1'] != 1:
        print(f"❌ ERRO Estrutural: O registo de **Cabeçalho (Tipo 1)** deve aparecer **exatamente 1 vez**. Encontrado: {contadores_tipo['1']}")
        validacao_estrutural_ok = False
    else:
        print(f"✅ Estrutural: Registo Tipo 1 (Cabeçalho) OK.")

    if contadores_tipo['9'] != 1:
        print(f"❌ ERRO Estrutural: O registo de **Rodapé (Tipo 9)** deve aparecer **exatamente 1 vez**. Encontrado: {contadores_tipo['9']}")
        validacao_estrutural_ok = False
    else:
        print(f"✅ Estrutural: Registo Tipo 9 (Rodapé) OK.")

    if contadores_tipo['2'] < 1:
        print(f"❌ ERRO Estrutural: O registo de **Detalhe (Tipo 2)** deve aparecer **pelo menos 1 vez**. Encontrado: {contadores_tipo['2']}")
        validacao_estrutural_ok = False
    else:
        print(f"✅ Estrutural: Registo Tipo 2 (Detalhe) OK. ({contagem_real_tipo2} encontrados)")

    if erros_tipo2_valor:
        print("❌ ERRO Estrutural: Encontrados erros de formato ou campos em falta nos valores Tipo 2. (Soma de Valor total impossível)")
        validacao_estrutural_ok = False
        
    if not validacao_estrutural_ok:
        print("\n🛑 **Validação de Conteúdo Cancelada** devido a erros estruturais.")
        return []
    
    print(f"\n--- Validação Estrutural Concluída. Soma Real dos Valores Tipo 2: **{soma_real_valor}** ---")

    # -----------------------------------------------------
    # --- 2. VALIDAÇÃO DE CONTEÚDO (NIF, ANO, CONSISTÊNCIA DE VALOR E QTD) ---
    # -----------------------------------------------------
    
    print("\n--- 📝 Validação de Conteúdo (Por Linha) ---")
    
    for i, linha in enumerate(lista_dados):
        numero_linha = i + 1
        registo_valido = True
        tipo = linha.get("Tipo Registo")

        # --- VALIDAÇÕES DO CABEÇALHO (TIPO 1) ---
        if tipo == "1":
            # 1 & 2. NIF e Ano (inalteradas)
            nif_atual = linha.get("NIF entidade")
            if not valida_nif(nif_atual):
                print(f"❌ ERRO Linha {numero_linha}: NIF **inválido** -> '{nif_atual}'")
                registo_valido = False
            else:
                print(f"✅ Linha {numero_linha}: NIF Válido.")

            data_str = linha.get("Data", "")
            if len(data_str) >= 4 and data_str[:4].isdigit():
                ano_ficheiro = int(data_str[:4])
                if ano_ficheiro == ano_atual:
                    print(f"✅ Linha {numero_linha}: Ano '{ano_ficheiro}' corresponde ao ano atual.")
                elif mes_atual == 1 and ano_ficheiro == (ano_atual - 1):
                    print(f"✅ Linha {numero_linha}: Ano '{ano_ficheiro}' aceite (Tolerância de Janeiro aplicada).")
                else:
                    print(f"❌ ERRO Linha {numero_linha}: Ano **incorreto**. Ficheiro: '{ano_ficheiro}', Sistema: '{ano_atual}' (Mês {mes_atual})")
                    registo_valido = False
            else:
                print(f"❌ ERRO Linha {numero_linha}: Formato de data inválido.")
                registo_valido = False

            # --- 3. VALIDAÇÃO 'Valor Total' (14 caracteres) e CONSISTÊNCIA DA SOMA ---
            
            valor_total_str = linha.get("Valor total") 

            if valor_total_str is None:
                print(f"❌ ERRO Linha {numero_linha}: Campo **'Valor total'** em falta.")
                registo_valido = False
            else:
                # 3a. Validação de Tamanho
                num_caracteres = len(str(valor_total_str))
                TAMANHO_ESPERADO = 14
                
                if num_caracteres != TAMANHO_ESPERADO:
                    print(f"❌ ERRO Linha {numero_linha}: Campo 'Valor total' tem {num_caracteres} caracteres. **Esperado: {TAMANHO_ESPERADO}**.")
                    registo_valido = False
                else:
                    print(f"✅ Linha {numero_linha}: (OK) Valor total ({num_caracteres} chars)")
                
                # 3b. Validação da Soma (se o campo foi encontrado)
                try:
                    valor_total_declarado = Decimal(valor_total_str)
                    
                    if valor_total_declarado != soma_real_valor:
                        print(f"❌ ERRO Linha {numero_linha}: Inconsistência do Valor Total. Declarado: {valor_total_declarado}, Calculado (Tipo 2): {soma_real_valor}")
                        registo_valido = False
                    else:
                        print(f"✅ Linha {numero_linha}: (OK) Valor total ({soma_real_valor})")

                except InvalidOperation:
                    print(f"❌ ERRO Linha {numero_linha}: Valor total ('{valor_total_str}') **não é um número válido**.")
                    registo_valido = False


            # --- 4. VALIDAÇÃO DE CONSISTÊNCIA: Qtd Transações vs. Contagem Real de Tipo 2 (inalterada) ---
            
            qtd_transacoes_str = linha.get("Qtd Transações")
            
            if qtd_transacoes_str is None:
                print(f"❌ ERRO Linha {numero_linha}: Campo **'Qtd Transações'** em falta.")
                registo_valido = False
            else:
                try:
                    qtd_transacoes_declarada = int(qtd_transacoes_str)

                    # REGRA DE CONSISTÊNCIA DE QTD
                    if qtd_transacoes_declarada != contagem_real_tipo2:
                        print(f"❌ ERRO Linha {numero_linha}: Inconsistência na Qtd Transações. Declarado: {qtd_transacoes_declarada}, Real (Tipo 2): {contagem_real_tipo2}")
                        registo_valido = False
                    else:
                        print(f"✅ Linha {numero_linha}: (OK) Transações ({contagem_real_tipo2})")

                except ValueError:
                    print(f"❌ ERRO Linha {numero_linha}: Qtd Transações ('{qtd_transacoes_str}') **não é um número inteiro válido**.")
                    registo_valido = False
                    
        # --- TIPOS 2 e 9 ---
        elif tipo in ['2', '9']:
            # Registos Tipo 2 e 9 são aceites aqui, pois a validação de conteúdo do Tipo 2
            # (formato de valor) já ocorreu na fase de SOMA (Passo 1.1)
            print(f"ℹ️ Linha {numero_linha}: Tipo de Registo '{tipo}' (Conteúdo aceite).")


        # Se passou em todos os testes, adiciona à lista final
        if registo_valido:
            dados_validos.append(linha)

    return dados_validos


# --- BLOCO DE TESTE (ATUALIZADO PARA INCLUIR O CAMPO 'Valor' NO TIPO 2) ---
if __name__ == "__main__":
    
    agora_teste = datetime.now()
    ano_sys = agora_teste.year
    
    print(f"\n--- A CORRER TESTES (Ano base sistema: {ano_sys}) ---")
    
    # O valor 14 chars deve incluir um separador decimal se o seu formato o exigir
    valor_14_chars = '0000010000.00' # 10000.00 - 14 chars OK
    
    # -----------------------------------------------------
    # TESTE 5: SUCESSO na Consistência de Qtd E Valor
    # Detalhes: 10.00, 20.00, 70.00. Soma Real = 100.00 (Declarado '0000000100.00')
    # Qtd Real = 3 (Declarado '00003')
    # -----------------------------------------------------
    print("\n\n#####################################################")
    print("TESTE 5: CONSISTÊNCIA TOTAL OK (Valor e Qtd)")
    print("#####################################################")
    
    # Soma de 10.00 + 20.00 + 70.00 = 100.00
    # O Valor Total declarado DEVE ser '0000000100.00' (14 caracteres)
    
    dados_sucesso_total = [
        # Tipo 1: Declara 3 Transações e 100.00 de Valor
        {'Tipo Registo': '1', 'Data': f'{ano_sys}1001', 'Entidade': 'Empresa OK', 'NIF entidade': '501442600', 'Valor total': '0000000100.00', 'Qtd Transações': '00003'}, 
        # Tipo 2 - 1
        {'Tipo Registo': '2', 'Data': '20250101', 'Entidade': 'Detalhe 1', 'NIF entidade': '999999999', 'Valor': '10.00'}, 
        # Tipo 2 - 2
        {'Tipo Registo': '2', 'Data': '20250101', 'Entidade': 'Detalhe 2', 'NIF entidade': '999999999', 'Valor': '20.00'}, 
        # Tipo 2 - 3
        {'Tipo Registo': '2', 'Data': '20250101', 'Entidade': 'Detalhe 3', 'NIF entidade': '999999999', 'Valor': '70.00'}, 
        {'Tipo Registo': '9', 'Data': '20250103', 'Entidade': 'FIM', 'NIF entidade': '999999999'} 
    ]
    
    resultado_sucesso_total = validar_dados(dados_sucesso_total)
    print("\n--- Resultado Final (Teste 5) ---")
    print(f"Total registos aceites: {len(resultado_sucesso_total)}")


    # -----------------------------------------------------
    # TESTE 6: FALHA na Consistência de Valor
    # Soma Real = 100.00. Valor Total Declarado = '0000000099.00' (Erro).
    # Qtd OK.
    # -----------------------------------------------------
    print("\n\n#####################################################")
    print("TESTE 6: CONSISTÊNCIA FALHA (Valor Incorreto)")
    print("#####################################################")
    
    dados_falha_valor = [
        # Tipo 1: Declara 3 Transações, mas o Valor Total é 99.00 (Incorreto)
        {'Tipo Registo': '1', 'Data': f'{ano_sys}1001', 'Entidade': 'Empresa Falha Valor', 'NIF entidade': '501442600', 'Valor total': '0000000099.00', 'Qtd Transações': '00003'}, 
        # Tipo 2 - 1
        {'Tipo Registo': '2', 'Data': '20250101', 'Entidade': 'Detalhe 1', 'NIF entidade': '999999999', 'Valor': '10.00'}, 
        # Tipo 2 - 2
        {'Tipo Registo': '2', 'Data': '20250101', 'Entidade': 'Detalhe 2', 'NIF entidade': '999999999', 'Valor': '20.00'}, 
        # Tipo 2 - 3
        {'Tipo Registo': '2', 'Data': '20250101', 'Entidade': 'Detalhe 3', 'NIF entidade': '999999999', 'Valor': '70.00'}, 
        {'Tipo Registo': '9', 'Data': '20250103', 'Entidade': 'FIM', 'NIF entidade': '999999999'} 
    ]
    
    resultado_falha_valor = validar_dados(dados_falha_valor)
    print("\n--- Resultado Final (Teste 6) ---")
    print(f"Total registos aceites: {len(resultado_falha_valor)}")
    print(resultado_falha_valor)