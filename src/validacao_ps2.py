import doctest
from datetime import datetime
from decimal import Decimal, InvalidOperation 

# --- FUNÇÕES AUXILIARES DE NIF/IBAN ---
DIGITOS_CONTROLO = 8 
DIGITOS_NIF = 9


def calcular_digito_controlo(digitos: str) -> str:
    """Calcula o digito de controlo de um NIF."""
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


def valida_iban(iban: str) -> bool:
    """
    Valida um IBAN usando o algoritmo Modulo 97-10, estritamente para PT (25 caracteres).
    NÃO ignora erros matemáticos.
    """
    
    CODIGO_PAIS_PT = 'PT'
    COMPRIMENTO_PT = 25
    
    # Limpeza de espaços e quebras de linha
    iban = str(iban).strip().replace(' ', '').upper()
    
    # 1. Validação inicial de comprimento e código de país
    if len(iban) != COMPRIMENTO_PT or iban[:2] != CODIGO_PAIS_PT:
        return False

    # 2. Reorganização: Move os 4 primeiros caracteres (PT50) para o fim
    iban_reorganizado = iban[4:] + iban[:4]
    
    # 3. Digitalização (Conversão de Letras para Dígitos)
    def letra_para_digito(char):
        if 'A' <= char <= 'Z':
            return str(ord(char) - ord('A') + 10)
        return char
        
    iban_digitalizado = "".join(letra_para_digito(c) for c in iban_reorganizado)
    
    # 4. Validação Modulo 97-10 (Cálculo Rigoroso)
    try:
        numero_completo = int(iban_digitalizado)
        resto = numero_completo % 97 
        
        # Só retorna True se o resto for EXATAMENTE 1
        return resto == 1
    
    except ValueError:
        return False

# --- FUNÇÃO PRINCIPAL DE VALIDAÇÃO ---
# (Resto do código 'validar_dados' e testes inalterados, usando a nova função valida_iban)

def validar_dados(lista_dados: list) -> int:
    """
    Recebe a lista de dados, valida-os e retorna um inteiro:
    1 se o ficheiro for totalmente válido, 0 caso contrário.
    """
    
    # VARIÁVEL DE ESTADO DE VALIDADE
    ficheiro_valido = True
    
    agora = datetime.now()
    ano_atual = agora.year
    mes_atual = agora.month
    
    print(f"\n--- 📅 Configuração do Sistema ---")
    print(f"Data do Sistema: {ano_atual} (Mês: {mes_atual})")

    # -----------------------------------------------------
    # --- 1. PASSO DE PRÉ-PROCESSAMENTO E SOMA ---
    # -----------------------------------------------------
    
    contadores_tipo = {'1': 0, '2': 0, '9': 0}
    soma_real_valor = Decimal(0)
    erros_tipo2_valor = False
    
    mes_base_ficheiro = None 
    ano_base_ficheiro = None
    valor_total_tipo1 = None
    qtd_transacoes_tipo1 = None
    ultimo_num_operacao_tipo2_str = None 

    # 1.1. Passo de Contagem, SOMA e Extração de Referências
    for i, linha in enumerate(lista_dados):
        tipo = linha.get("Tipo Registo")
        if tipo in contadores_tipo:
            contadores_tipo[tipo] += 1
        
        if tipo == '1':
            data_str = linha.get("Data", "")
            if len(data_str) >= 6 and data_str[:6].isdigit():
                ano_base_ficheiro = data_str[:4]
                mes_base_ficheiro = data_str[4:6]
            
            valor_total_str = linha.get("Valor total") 
            if valor_total_str is None or str(valor_total_str).strip() == "":
                valor_total_tipo1 = None 
            else:
                try:
                    valor_total_tipo1 = Decimal(valor_total_str)
                except (InvalidOperation, TypeError):
                    valor_total_tipo1 = None 
            
            try:
                qtd_transacoes_tipo1 = int(linha.get("Qtd Transações"))
            except (TypeError, ValueError):
                qtd_transacoes_tipo1 = None

        if tipo == '2':
            ultimo_num_operacao_tipo2_str = linha.get("Nº operação")
            valor_str = linha.get("Valor")
            if valor_str is None:
                erros_tipo2_valor = True 
            else:
                try:
                    soma_real_valor += Decimal(valor_str)
                except InvalidOperation:
                    erros_tipo2_valor = True
            
    contagem_real_tipo2 = contadores_tipo['2']
            
    # -----------------------------------------------------
    # --- 2. VALIDAÇÃO ESTRUTURAL ---
    # -----------------------------------------------------
    
    print("\n--- 🏗️ Validação Estrutural (Regras de Contagem e Soma) ---")
    
    if contadores_tipo['1'] != 1:
        print(f"❌ ERRO Estrutural: O registo de **Cabeçalho (Tipo 1)** deve aparecer **exatamente 1 vez**. Encontrado: {contadores_tipo['1']}")
        ficheiro_valido = False
    
    if contadores_tipo['9'] != 1:
        print(f"❌ ERRO Estrutural: O registo de **Rodapé (Tipo 9)** deve aparecer **exatamente 1 vez**. Encontrado: {contadores_tipo['9']}")
        ficheiro_valido = False

    if contadores_tipo['2'] < 1:
        print(f"❌ ERRO Estrutural: O registo de **Detalhe (Tipo 2)** deve aparecer **pelo menos 1 vez**. Encontrado: {contadores_tipo['2']}")
        ficheiro_valido = False
    
    if erros_tipo2_valor:
        print("❌ ERRO Estrutural: Encontrados erros de formato ou campos em falta nos valores Tipo 2. (Soma de Valor total impossível)")
        ficheiro_valido = False
        
    if not ficheiro_valido:
        print("\n🛑 **Validação de Conteúdo Cancelada** devido a erros estruturais.")
        return 0 

    if mes_base_ficheiro is None or ano_base_ficheiro is None:
        print("❌ ERRO Estrutural: Impossível extrair Mês/Ano de referência do registo Tipo 1 para validações de detalhe.")
        return 0
    
    print(f"\n--- Validação Estrutural Concluída. Soma Real dos Valores Tipo 2: **{soma_real_valor}** ---")
    
    data_esperada_mm_aaaa = f'{mes_base_ficheiro}/{ano_base_ficheiro}'
    print(f"ℹ️ Data Base do Ficheiro (Tipo 1) para validações: **{data_esperada_mm_aaaa}**")


    # -----------------------------------------------------
    # --- 3. VALIDAÇÃO DE CONTEÚDO (POR LINHA) ---
    # -----------------------------------------------------
    
    print("\n--- 📝 Validação de Conteúdo (Por Linha) ---")
    
    contador_operacoes_tipo2 = 0 
    descricao_base_tipo2 = None 

    for i, linha in enumerate(lista_dados):
        numero_linha = i + 1
        registo_valido = True
        tipo = linha.get("Tipo Registo")

        # --- VALIDAÇÕES DO CABEÇALHO (TIPO 1) ---
        if tipo == "1":
            
            # 1. NIF Entidade
            nif_atual = linha.get("NIF entidade")
            if not valida_nif(nif_atual):
                print(f"❌ ERRO Linha {numero_linha}: NIF Entidade **inválido** -> '{nif_atual}'")
                registo_valido = False

            # 2. Ano
            data_str = linha.get("Data", "")
            if len(data_str) >= 4 and data_str[:4].isdigit():
                ano_ficheiro_int = int(data_str[:4])
                
                if not (ano_ficheiro_int == ano_atual or (mes_atual == 1 and ano_ficheiro_int == (ano_atual - 1))):
                    print(f"❌ ERRO Linha {numero_linha}: Ano **incorreto**. Ficheiro: '{ano_ficheiro_int}', Sistema: '{ano_atual}' (Mês {mes_atual})")
                    registo_valido = False
            else:
                print(f"❌ ERRO Linha {numero_linha}: Formato de data inválido.")
                registo_valido = False

            # 3. Entidade
            nome_entidade = linha.get("Entidade")
            LIMITE_CARACTERES = 43
            
            if nome_entidade is None or str(nome_entidade).strip() == "":
                print(f"❌ ERRO Linha {numero_linha}: Campo **'Entidade'** em falta ou vazio.")
                registo_valido = False
            else:
                entidade_str = str(nome_entidade)
                if len(entidade_str) > LIMITE_CARACTERES:
                    print(f"❌ ERRO Linha {numero_linha}: Campo 'Entidade' tem {len(entidade_str)} caracteres. **Máximo permitido: {LIMITE_CARACTERES}**.")
                    registo_valido = False

            # 4. Valor Total
            valor_total_str = linha.get("Valor total") 

            # Verificação de robustez 
            if valor_total_str is None or valor_total_tipo1 is None:
                print(f"❌ ERRO Linha {numero_linha}: Campo 'Valor total' está **em falta**, vazio ou **não é um número válido**.")
                registo_valido = False
            else:
                num_caracteres = len(str(valor_total_str))
                TAMANHO_ESPERADO = 14
                
                if num_caracteres != TAMANHO_ESPERADO:
                    print(f"❌ ERRO Linha {numero_linha}: Campo 'Valor total' tem {num_caracteres} caracteres. **Tamanho esperado: {TAMANHO_ESPERADO}**.")
                    registo_valido = False
                
                try:
                    valor_total_declarado = Decimal(valor_total_str)
                    
                    if valor_total_declarado != soma_real_valor:
                        print(f"❌ ERRO Linha {numero_linha}: Inconsistência do Valor Total. Declarado: {valor_total_declarado}, Calculado (Tipo 2): {soma_real_valor}")
                        registo_valido = False

                except InvalidOperation:
                    print(f"❌ ERRO Linha {numero_linha}: Valor total ('{valor_total_str}') **não é um número válido**.")
                    registo_valido = False


            # 5. Qtd Transações
            qtd_transacoes_str = linha.get("Qtd Transações")
            
            if qtd_transacoes_str is None:
                print(f"❌ ERRO Linha {numero_linha}: Campo 'Qtd Transações' está **em falta**.")
                registo_valido = False
            else:
                try:
                    qtd_transacoes_declarada = int(qtd_transacoes_str)

                    if qtd_transacoes_declarada != contagem_real_tipo2:
                        print(f"❌ ERRO Linha {numero_linha}: Inconsistência na Qtd Transações. Declarado: {qtd_transacoes_declarada}, Real (Tipo 2): {contagem_real_tipo2}")
                        registo_valido = False

                except ValueError:
                    print(f"❌ ERRO Linha {numero_linha}: Qtd Transações ('{qtd_transacoes_str}') **não é um número inteiro válido**.")
                    registo_valido = False
                    
            if not registo_valido:
                ficheiro_valido = False
            else:
                print(f"✅ Linha {numero_linha} (Tipo 1): OK.")


        # --- VALIDAÇÕES DO DETALHE (TIPO 2) ---
        elif tipo == '2':
            
            # 0. NIF Cliente (VALIDAÇÃO)
            nif_cliente = linha.get("NIF Cliente") 
            if not valida_nif(nif_cliente):
                print(f"❌ ERRO Linha {numero_linha}: Tipo 2 - NIF Cliente **inválido** ou em falta -> '{nif_cliente}'")
                registo_valido = False
            
            # 1. Tipo operação
            tipo_operacao = linha.get("Tipo operação")
            if tipo_operacao is None or str(tipo_operacao).strip() == "":
                print(f"❌ ERRO Linha {numero_linha}: Tipo 2 - Campo **'Tipo operação'** em falta ou vazio.")
                registo_valido = False

            # 2. Nº operação (Sequência)
            contador_operacoes_tipo2 += 1
            num_operacao_str = linha.get("Nº operação")
            num_operacao_esperado = str(contador_operacoes_tipo2).zfill(3)
            
            if num_operacao_str is None or num_operacao_str != num_operacao_esperado:
                print(f"❌ ERRO Linha {numero_linha}: Tipo 2 - Nº Operação incorreto. Declarado: '{num_operacao_str}', Esperado: '{num_operacao_esperado}' (Sequência).")
                registo_valido = False

            # 3. IBAN
            iban_str = linha.get("IBAN")
            if iban_str is None or str(iban_str).strip() == "" or not valida_iban(iban_str):
                print(f"❌ ERRO Linha {numero_linha}: Tipo 2 - IBAN inválido ou com formato incorreto. ('{iban_str}')")
                registo_valido = False
            
            # 4. VALIDAÇÕES DE DESCRIÇÃO
            descricao = linha.get("Descrição")
            if descricao is None:
                descricao_str = ""
            else:
                descricao_str = str(descricao).strip() 

            if descricao_str == "":
                print(f"❌ ERRO Linha {numero_linha}: Tipo 2 - Campo **'Descrição'** em falta ou vazio.")
                registo_valido = False
            else:
                # 4a. Validação de Uniformidade 
                if contador_operacoes_tipo2 == 1:
                    descricao_base_tipo2 = descricao_str
                elif descricao_str != descricao_base_tipo2:
                    print(f"❌ ERRO Linha {numero_linha}: Tipo 2 - Descrição inconsistente. Atual: '{descricao_str}', Base: '{descricao_base_tipo2}'")
                    registo_valido = False
                
                # 4b. Validação da Data
                TAMANHO_DATA_MM_AAAA = 7 
                data_campo_esperada = f'{mes_base_ficheiro}/{ano_base_ficheiro}' 
                
                if len(descricao_str) < TAMANHO_DATA_MM_AAAA or descricao_str[-TAMANHO_DATA_MM_AAAA:] != data_campo_esperada:
                    data_descricao = descricao_str[-TAMANHO_DATA_MM_AAAA:] if len(descricao_str) >= TAMANHO_DATA_MM_AAAA else "curta"
                    print(f"❌ ERRO Linha {numero_linha}: Tipo 2 - Data na Descrição inconsistente. Descrição (últimos 7): '{data_descricao}', Esperado: '{data_campo_esperada}' (Data Base Tipo 1).")
                    registo_valido = False

            if not registo_valido:
                ficheiro_valido = False
            else:
                print(f"✅ Linha {numero_linha} (Tipo 2): OK.")


        # --- VALIDAÇÕES DO RODAPÉ (TIPO 9) ---
        elif tipo == '9':
            
            # 1. Validação do Campo "Valor total"
            valor_total_rodapé_str = linha.get("Valor total")
            
            if valor_total_rodapé_str is None:
                 print(f"❌ ERRO Linha {numero_linha}: Tipo 9 - Campo **'Valor total'** em falta.")
                 registo_valido = False
            else:
                try:
                    valor_rodapé_declarado = Decimal(valor_total_rodapé_str)

                    # Consistência com o Valor Total do Tipo 1 e Soma Real Tipo 2
                    if (valor_total_tipo1 is not None and valor_rodapé_declarado != valor_total_tipo1) or \
                       (valor_rodapé_declarado != soma_real_valor):
                        print(f"❌ ERRO Linha {numero_linha}: Tipo 9 - Valor total ({valor_rodapé_declarado}) **inconsistente** com Tipo 1 ({valor_total_tipo1}) ou soma Tipo 2 ({soma_real_valor}).")
                        registo_valido = False
                        
                except InvalidOperation:
                    print(f"❌ ERRO Linha {numero_linha}: Tipo 9 - Valor total ('{valor_total_rodapé_str}') **não é um número válido**.")
                    registo_valido = False


            # 2. Validação do Campo "Qtd Transações"
            qtd_transacoes_rodapé_str = linha.get("Qtd Transações")
            
            if qtd_transacoes_rodapé_str is None:
                print(f"❌ ERRO Linha {numero_linha}: Tipo 9 - Campo **'Qtd Transações'** em falta.")
                registo_valido = False
            else:
                try:
                    qtd_rodapé_declarada = int(qtd_transacoes_rodapé_str)
                    
                    # 2a. Consistência com Tipo 1 e Contagem Real Tipo 2
                    if (qtd_transacoes_tipo1 is not None and qtd_rodapé_declarada != qtd_transacoes_tipo1) or \
                       (qtd_rodapé_declarada != contagem_real_tipo2):
                        print(f"❌ ERRO Linha {numero_linha}: Tipo 9 - Qtd Transações ({qtd_rodapé_declarada}) **inconsistente** com Tipo 1 ({qtd_transacoes_tipo1}) ou contagem Tipo 2 ({contagem_real_tipo2}).")
                        registo_valido = False
                        
                    # 2b. Qtd Transações (Tipo 9) vs. Nº Operação da última linha Tipo 2
                    try:
                        ultimo_num_operacao_int = int(ultimo_num_operacao_tipo2_str)
                        if qtd_rodapé_declarada != ultimo_num_operacao_int:
                             print(f"❌ ERRO Linha {numero_linha}: Tipo 9 - Qtd Transações ({qtd_rodapé_declarada}) **não coincide com o Nº Operação da última linha Tipo 2** ({ultimo_num_operacao_int}).")
                             registo_valido = False
                    except (ValueError, TypeError):
                        pass

                except ValueError:
                    print(f"❌ ERRO Linha {numero_linha}: Tipo 9 - Qtd Transações ('{qtd_transacoes_rodapé_str}') **não é um número inteiro válido**.")
                    registo_valido = False
            
            if not registo_valido:
                ficheiro_valido = False
            else:
                print(f"✅ Linha {numero_linha} (Tipo 9): OK.")

    # --- RESULTADO FINAL ---
    print("\n--- Conclusão da Validação ---")
    
    if ficheiro_valido:
        print("✅ SUCESSO: O ficheiro é totalmente VÁLIDO.")
    else:
        print("❌ FALHA: O ficheiro é INVÁLIDO (verifique os erros acima).")

    # Retorna 1 se todas as validações correram bem, 0 caso contrário.
    return 1 if ficheiro_valido else 0


# --- BLOCO DE TESTE ---
if __name__ == "__main__":
    
    agora_teste = datetime.now()
    ano_sys = agora_teste.year
    
    # -----------------------------------------------------
    # VARIÁVEIS PARA SUCESSO (TESTE 4)
    # -----------------------------------------------------
    VALOR_TOTAL_OK = '0000000100.00' 
    QTD_TRANSACOES_OK = '00002'
    entidade_ok = 'TESTE COM DADOS VALIDOS'
    
    # NIFs Válidos
    NIF_ENTIDADE_OK = '501442600'
    NIF_CLIENTE_OK_1 = '500123456' 
    NIF_CLIENTE_OK_2 = '500987658' 
    
    # IBANs Portugueses Válidos que começam OBRIGATORIAMENTE por PT50
    # Nota: Tivemos de ajustar os zeros finais para validar matematicamente com PT50
    IBAN_VALIDO_1 = 'PT50000000000000000000098' 
    IBAN_VALIDO_2 = 'PT50000000000000000000195' 
    
    DATA_TIPO_1 = f'{ano_sys}1001' 
    DATA_DESC_ESPERADA = f'10/{ano_sys}' 
    DESCRICAO_UTILIZADOR = f'Transferencia Poupanca {DATA_DESC_ESPERADA}' 
    
    print(f"\n--- A CORRER TESTES (Ano base sistema: {ano_sys}) ---")

    # -----------------------------------------------------
    # TESTE 4: SUCESSO TOTAL (IBANs PT50 Validados) - Esperado: 1
    # -----------------------------------------------------
    print("\n\n#####################################################")
    print("TESTE 4: SUCESSO TOTAL (IBANs PT50) - Esperado: 1")
    print("#####################################################")
    
    dados_sucesso_nif_cliente_ok = [
        # Tipo 1 (Cabeçalho)
        {'Tipo Registo': '1', 'Data': DATA_TIPO_1, 'Entidade': entidade_ok, 'NIF entidade': NIF_ENTIDADE_OK, 'Valor total': VALOR_TOTAL_OK, 'Qtd Transações': QTD_TRANSACOES_OK}, 
        
        # Tipo 2 (Detalhe 1) - IBAN PT50 Validado
        {'Tipo Registo': '2', 'Data': f'{ano_sys}1026', 'Entidade': 'Detalhe 1', 'NIF Cliente': NIF_CLIENTE_OK_1, 'Valor': '40.00', 'Tipo operação': 'TRF', 'Nº operação': '001', 'IBAN': IBAN_VALIDO_1, 'Descrição': DESCRICAO_UTILIZADOR}, 
        
        # Tipo 2 (Detalhe 2) - IBAN PT50 Validado
        {'Tipo Registo': '2', 'Data': f'{ano_sys}1026', 'Entidade': 'Detalhe 2', 'NIF Cliente': NIF_CLIENTE_OK_2, 'Valor': '60.00', 'Tipo operação': 'TRF', 'Nº operação': '002', 'IBAN': IBAN_VALIDO_2, 'Descrição': DESCRICAO_UTILIZADOR}, 
        
        # Tipo 9 (Rodapé)
        {'Tipo Registo': '9', 'Data': f'{ano_sys}1001', 'Entidade': 'FIM', 'NIF entidade': '999999999', 'Valor total': VALOR_TOTAL_OK, 'Qtd Transações': QTD_TRANSACOES_OK} 
    ]
    
    resultado_sucesso_final = validar_dados(dados_sucesso_nif_cliente_ok)
    print("\n--- Resultado Final (Teste 4) ---")
    print(f"Status do Ficheiro (1=Válido, 0=Inválido): **{resultado_sucesso_final}**")