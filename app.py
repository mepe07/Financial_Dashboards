from shiny import App, render, ui, reactive
import pandas as pd
from datetime import date
from src import ler_ficheiros_ps2
from src import converterParaPandas
from src import validar_dados
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from faicons import icon_svg
from matplotlib.ticker import PercentFormatter # Para o eixo da % do grafico de pareto

# --- 1. CARREGAMENTO DE DADOS ---
dados_brutos = ler_ficheiros_ps2()
ficheiros_invalidos = validar_dados(dados_brutos)

dados_validos = [
    dado for dado in dados_brutos
    if dado.get("Origem") not in ficheiros_invalidos
]

pacote = converterParaPandas(dados_validos)

df_cabecalho_global = pacote["cabecalho"]
df_movimentos_global = pacote["movimentos"]
df_rodape_global = pacote["rodape"]

# Garantir que a Data é datetime logo no início para evitar erros depois
if "Data" in df_cabecalho_global.columns:
    df_cabecalho_global["Data"] = pd.to_datetime(df_cabecalho_global["Data"])

# --- PREPARAÇÃO DOS FILTROS ---
data_min = date.today()
data_max = date.today()

if not df_cabecalho_global.empty and "Data" in df_cabecalho_global.columns:
    dates = df_cabecalho_global["Data"].dt.date
    data_min = dates.min()
    data_max = dates.max()

if "Origem" in df_cabecalho_global.columns:
    lista_ficheiros = sorted(df_cabecalho_global["Origem"].unique().tolist())
else:
    lista_ficheiros = []
opcoes_ficheiros = ["Todos"] + lista_ficheiros

if "Entidade" in df_cabecalho_global.columns:
    lista_entidades = sorted(df_cabecalho_global["Entidade"].unique().tolist())
else:
    lista_entidades = []
opcoes_entidades = ["Todas"] + lista_entidades


# --- 2. INTERFACE (UI) ---

# Barra lateral
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Filtros"),

        # Botão de Atualizar
        # ui.input_action_button("btn_atualizar", "Atualizar Dados", icon=icon_svg("arrows-rotate")),
        # ui.hr(),

        # 1. Interruptor (Switch)
        ui.input_switch("ativar_filtro_data", "Filtrar por Datas", value=True),

        # 2. O Seletor de Datas (dentro de um painel condicional)
        # Este painel só aparece se o input "ativar_filtro_data" for verdadeiro
        ui.panel_conditional(
            "input.ativar_filtro_data",  # Condição JavaScript (nome do input)
            ui.input_date_range(
                "filtro_data", 
                "Intervalo de Datas:",
                start=data_min, 
                end=data_max, 
                min=data_min, 
                max=data_max,
                format="dd/mm/yyyy", 
                language="pt-pt"
            )
        ),

        # Linha divisória
        # ui.hr(),

        ui.input_select(
            "filtro_entidade", "Entidade:", 
            choices=opcoes_entidades, selected="Todas"
        ),

        ui.input_select(
            "filtro_ficheiro", "Ficheiro Específico:", 
            choices=opcoes_ficheiros, selected="Todos",
            
        ),
        
        ui.hr(style="margin: 5px 0;"),

        # Checkboxes        
        ui.input_checkbox_group(
            "selecao_graficos", # ID do input
            "Mostrar Gráficos:", # Título
            # Dicionário: "id_interno": "Nome que aparece no ecrã"
            {
                "g_barras": "Top Entidades",
                "g_linhas": "Evolução Mensal",
                "g_linhas_global": "Evolução Global",
                "g_hist": "Histograma",
                "g_pareto": "Pareto"
            },
            # Quais começam selecionados? (Todos)
            selected=["g_barras", "g_linhas", "g_linhas_global", "g_hist", "g_pareto"] 
        ),
        
        ui.hr(style="margin: 5px 0;"),
        
        ui.p("Resumo:"),
        ui.output_text("texto_total_registos")
    ),

    # Zona central
    ui.page_fluid(
        # FLEXBOX
        ui.div(
            ui.h2("Dashboard Financeiro", style="margin: 0"),

            # Algoritmo CSS para que o sino balance quando tem notificações
            ui.div(
                ui.tags.style("""
                    /* Definir a animação 'ding' */
                    @keyframes ding {
                        0% { transform: rotate(0deg); }
                        20% { transform: rotate(15deg); }
                        40% { transform: rotate(-10deg); }
                        60% { transform: rotate(5deg); }
                        80% { transform: rotate(-5deg); }
                        100% { transform: rotate(0deg); }
                    }

                    /* Classe que ativa a animação */
                    .tem-notificacao svg {
                        animation: ding 1.2s ease-in-out infinite; /* Balança para sempre */
                        color: #ffc107; /* Muda a cor do sino para amarelo/laranja */
                    }
                """),


                # Botão de Atualizar
                ui.input_action_button(
                    "btn_atualizar", 
                    "Atualizar Dados", 
                    icon=icon_svg("arrows-rotate"), 
                    class_="btn-primary"
                ),

                # Botão de notificações
                # 1. O SCRIPT MÁGICO (Ensina o browser a ligar/desligar a animação)
                ui.tags.script("""
                    Shiny.addCustomMessageHandler('gerir_animacao_sino', function(mensagem) {
                        // Procura o botão pelo ID
                        var botao = document.getElementById(mensagem.id);
                        if (botao) {
                            if (mensagem.ativar) {
                                botao.classList.add('tem-notificacao'); // Liga animação
                            } else {
                                botao.classList.remove('tem-notificacao'); // Desliga animação
                            }
                        }
                    });
                """),

                # 2. O BOTÃO ESTÁTICO (Aparece instantaneamente!)
                # Nota: Removemos o @render.ui e colocamos o botão "fixo" aqui
                ui.input_action_button(
                    "btn_notificacoes", 
                    "Notificações", 
                    icon=icon_svg("bell"), 
                    class_="btn-secondary", # Começa cinzento (sem animação)
                    # Mantemos o estilo visual
                    #style="display: flex; align-items: center; justify-content: center; padding: 0;"
                ),
                
                # ui.input_action_button(
                #     "btn_notificacoes_placeholder", 
                #     "Notificações", 
                #     icon=icon_svg("bell"), 
                #     class_="btn-secondary",
                #     # style="display: flex; align-items: center; justify-content: center; padding: 0;"
                # ),
                #ui.output_ui("render_botao_notificacoes"),

                style="display: flex; gap: 10px;"

            ),

            style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px"

        ),
        
        
        
        ui.navset_card_underline(

            ### Aba de Gráficos ###
            ui.nav_panel("Análise Gráfica", 
                # --- CONTAINER FLEXBOX ---
                ui.div(
                    
                    # Gráfico 1 (Total cobrado por entidade)
                    ui.panel_conditional(   
                        "input.selecao_graficos.includes('g_barras')",
                        ui.card(
                            ui.card_header(
                                ui.div(
                                    "Top Entidades (Valor Total)",
                                    ui.tooltip(
                                        ui.span(
                                            icon_svg("circle-info"),
                                            style="color: #6c757d; cursor: help; margin-left: 8px; font-size: 0.9em;"
                                        ),
                                        "Análise de volume acumulado por entidade. Essencial para identificar contas estratégicas e compreender a concentração da carteira de cobranças (quem representa a maior fatia do valor total)",
                                        placement="auto"
                                    ),
                                    style="display: flex; align-items: center;"
                                )
                            ),
                            ui.output_plot("grafico_barras_entidade", height="650px")
                        )
                    ),
                    # Gráfico 2 (Evolução mensal top 5 entidades)
                    ui.panel_conditional(   
                        "input.selecao_graficos.includes('g_linhas')",                     
                        ui.card(
                            ui.card_header(
                                ui.div(
                                    "Evolução Temporal das Cobranças",
                                    ui.tooltip(
                                        ui.span(
                                            icon_svg("circle-info"),
                                            style="color: #6c757d; cursor: help; margin-left: 8px; font-size: 0.9em;"
                                        ),
                                        "Monitorização do fluxo de cobranças. Permite identificar dias com picos de cobrança para e analisar a regularidade das mesmas.",
                                        placement="auto"
                                    ),
                                    style="display: flex; align-items: center;"
                                )
                            ),
                            ui.output_plot("grafico_linha_tempo", height="600px")
                        )
                    ),

                    # Gráfico 3 (Evolução das cobranças global)
                    ui.panel_conditional (
                        # Só aparecer se não houver filtro de entidade e/ou ficheiro
                        "input.filtro_entidade === 'Todas' && input.filtro_ficheiro === 'Todos' && input.selecao_graficos.includes('g_linhas_global')",
                        ui.card(
                            ui.card_header(
                                ui.div(
                                    "Evolução Temporal das Cobranças (Soma global)",
                                    ui.tooltip(
                                        ui.span(
                                            icon_svg("circle-info"),
                                            style="color: #6c757d; cursor: help; margin-left: 8px; font-size: 0.9em;"
                                        ),
                                        "Monitorização global do fluxo de caixa. Permite estabelecer métricas de períodos mais comuns de cobrança.",
                                        placement="auto"
                                    ),
                                    style="display: flex; align-items: center;"
                                )
                            ),
                            ui.output_plot("grafico_evolucao_temporal", height="600px")
                        )
                    ),
                    
                    # Gráfico 4 (Frequência por faixa de valor)
                    ui.panel_conditional(   
                        "input.selecao_graficos.includes('g_hist')",
                        ui.card(
                            ui.card_header(
                                ui.div(
                                    "Distribuição de Valores (Histograma)",
                                    ui.tooltip(
                                        ui.span(
                                            icon_svg("circle-info"),
                                            style="color: #6c757d; cursor: help; margin-left: 8px; font-size: 0.9em;"
                                        ),
                                        "Qual é o valor médio de uma cobrança? Ajuda a entender o perfil da carteira.",
                                        placement="auto"
                                    ),
                                    style="display: flex; align-items: center;"
                                )
                            ),
                            ui.output_plot("grafico_histograma_valores", height="500px")
                        )
                    ),
                    
                    # Gráfico 5 (Pareto)
                    ui.panel_conditional(   
                        "input.selecao_graficos.includes('g_pareto')",
                        ui.card(
                            ui.card_header(
                                ui.div(
                                    "Top Clientes - Diagrama de Pareto (80/20)",
                                    ui.tooltip(
                                        ui.span(
                                            icon_svg("circle-info"), 
                                            style="color: #6c757d; cursor: help; margin-left: 8px; font-size: 0.9em;"
                                        ),
                                        "Onde a linha vermelha cruza o tracejado cinzento (80%), todos os NIFs à esquerda desse ponto representam 80% da faturação. Estes são os clientes que garantem maior rentabilidade.",
                                        placement="auto"
                                    ),
                                    style="display: flex; align-items: center;"
                                )
                            ),
                            ui.output_plot("grafico_pareto_clientes", height="600px")
                        )
                    ),

                    # --- ESTILO DO CONTAINER ---
                    # display: flex + column -> Empilha um por baixo do outro
                    # gap: 30px -> Cria o espaço vazio entre cada cartão
                    style="display: flex; flex-direction: column; gap: 30px; margin-top: 20px;"
                )
            ),
            
            
            ui.nav_panel("Cabeçalhos", ui.output_data_frame("tabela_cabecalho")),

            ui.nav_panel("Movimentos", ui.output_data_frame("tabela_movimentos")),

            ui.nav_panel("Rodapés", ui.output_data_frame("tabela_rodape")),
        )
    )
)



#-----------------------------------------------------------
#                 3. SERVIDOR (Lógica)
#-----------------------------------------------------------

def server(input, output, session):

    # --- 1. GESTÃO DE DADOS ---
    # Container reativo para guardar os dados carregados e também invalidos
    store_dados = reactive.Value(pacote)
    store_invalidos = reactive.Value(ficheiros_invalidos)


    # Função que carrega os dados do disco (ao iniciar e ao clicar no botão)
    # Função que carrega os dados do disco (ao iniciar e ao clicar no botão)
    @reactive.effect
    @reactive.event(input.btn_atualizar, ignore_init=True)
    def carregar_dados_do_disco():
        # Guardamos o ID da notificação numa variável
        id_notificacao = ui.notification_show("A ler ficheiros...", type="message", duration=None)
        
        try:
            print("--- A CARREGAR DADOS ---")
            # Ler novamente da pasta
            novos_dados_brutos = ler_ficheiros_ps2() 

            # Nova validação, pois podem ter entrado ficheiros invalidos
            lista_erros = validar_dados(novos_dados_brutos)
            store_invalidos.set(lista_erros) # guardar na memória reativa

            # Se houver erros, avisar imeatamente
            if lista_erros:
                msg = f"Atenção: Foram detetados {len(lista_erros)} ficheiros inválidos!"
                ui.notification_show(msg, type="warning", duration=5)
            
            # FILTRAGEM - Lista apenas com os ficheiros que passaram na validação
            dados_validos = [
                dado for dado in novos_dados_brutos
                if dado.get("Origem") not in lista_erros
            ]

            # Converter para pandas e guardar os válidos
            novo_pacote = converterParaPandas(dados_validos)
            store_dados.set(novo_pacote)
            
            # Atualizar os Filtros da UI dinamicamente
            df_cab = novo_pacote["cabecalho"]
            if not df_cab.empty:
                # Atualizar Entidades
                ents = ["Todas"] + sorted(df_cab["Entidade"].unique().tolist())
                ui.update_select("filtro_entidade", choices=ents, selected="Todas")
                
                # Atualizar Ficheiros
                fichs = ["Todos"] + sorted(df_cab["Origem"].unique().tolist())
                ui.update_select("filtro_ficheiro", choices=fichs, selected="Todos")
                
                # Atualizar Calendário
                if "Data" in df_cab.columns:
                    datas_dt = pd.to_datetime(df_cab["Data"])
                    min_d = datas_dt.min().date()
                    max_d = datas_dt.max().date()
                    ui.update_date_range("filtro_data", min=min_d, max=max_d, start=min_d, end=max_d)

                ui.notification_show("Dados atualizados com sucesso!", type="message", duration=3)

        except Exception as e:
            ui.notification_show(f"Erro: {e}", type="error")
            print(f"ERRO: {e}")
            
        finally:
            # Fechar notificação
            ui.notification_remove(id_notificacao)

        

    @reactive.effect
    @reactive.event(input.btn_notificacoes)
    def mostrar_janela_erros():
        # Vamos buscar a lista atual de erros
        erros = store_invalidos()
        
        if erros:
            # CASO A: Existem erros -> Mostra Janela (Modal)
            ui.modal_show(
                ui.modal(
                    ui.div(
                        ui.h4("Ficheiros Rejeitados", style="color: #dc3545; margin-top:0;"),
                        ui.p("Os seguintes ficheiros não respeitam o formato PS2 ou contêm erros de estrutura:"),
                        ui.hr(),
                        
                        # Cria uma lista HTML (Bullet points) dinâmica
                        ui.tags.ul(
                            # Loop que cria um <li> para cada ficheiro na lista
                            [ui.tags.li(nome, style="color: #dc3545; font-weight: bold;") for nome in erros]
                        ),
                        
                        ui.hr(),
                        ui.p("Nota: Estes ficheiros foram ignorados e não constam nos gráficos.", style="font-size: 0.9em; color: gray;")
                    ),
                    title="Alertas do Sistema",
                    easy_close=True,
                    footer=ui.modal_button("Fechar")
                )
            )
        # else:
        #     # CASO B: Não existem erros -> Notificação Verde
        #     ui.notification_show("Tudo operacional! Não existem ficheiros inválidos.", type="message", duration=3)



    # NOVO: Controlar a animação sem redesenhar o botão
    # NOTA: Adicionámos 'async' antes do def
    @reactive.effect
    async def controlar_animacao_botao():
        # Lemos a lista de erros
        erros = store_invalidos()
        
        # Calculamos se deve ter animação
        tem_erro = True if erros else False
        
        
        # O print ajuda a confirmar no terminal se a função está a correr
        # print(f"DEBUG: Atualizar botão. Tem erros? {tem_erro}") 
        
        # NOTA: Adicionámos 'await' aqui. É isto que faz a mensagem sair!
        await session.send_custom_message(
            "gerir_animacao_sino", 
            {"id": "btn_notificacoes", "ativar": tem_erro}
        )


    # --- 2. CÁLCULOS E FILTROS ---
    @reactive.calc
    def dados_filtrados():
        # Ler do nosso container reativo
        pacote = store_dados()
        
        if pacote is None:
            # Retorna dataframes vazios se ainda não carregou
            return {"cab": pd.DataFrame(), "mov": pd.DataFrame(), "rod": pd.DataFrame()}

        df_cabecalho = pacote["cabecalho"]
        df_movimentos = pacote["movimentos"]
        df_rodape = pacote["rodape"]

        # Ler inputs
        entidade = input.filtro_entidade()
        ficheiro = input.filtro_ficheiro()
        usar_datas = input.ativar_filtro_data()
        datas = input.filtro_data()

        cab = df_cabecalho.copy()
        
        # 1. FILTRO DE DATA
        if not cab.empty and usar_datas and datas:
            start_date, end_date = datas
            # Garante datetime
            cab["Data"] = pd.to_datetime(cab["Data"])
            mask = (cab["Data"].dt.date >= start_date) & (cab["Data"].dt.date <= end_date)
            cab = cab.loc[mask]

        # 2. FILTRO DE ENTIDADE
        if entidade != "Todas":
            cab = cab[cab["Entidade"] == entidade]

        # 3. FILTRO DE FICHEIRO
        if ficheiro != "Todos":
            cab = cab[cab["Origem"] == ficheiro]

        # Propagação
        ficheiros_validos = cab["Origem"].unique()
        mov = df_movimentos[df_movimentos["Origem"].isin(ficheiros_validos)]
        rod = df_rodape[df_rodape["Origem"].isin(ficheiros_validos)]

        return {"cab": cab, "mov": mov, "rod": rod}
    
    # -------------------------------------
    # --- TABELAS ---
    # -------------------------------------

    @render.data_frame
    def tabela_cabecalho():
        df = dados_filtrados()["cab"].copy()
        if not df.empty and "Data" in df.columns:
            # Converter para datetime só para garantir, caso venha string
            df["Data"] = pd.to_datetime(df["Data"]) 
            df["Data"] = df["Data"].dt.strftime('%d/%m/%Y')
        return render.DataGrid(df, filters=True)

    @render.data_frame
    def tabela_movimentos():
        return render.DataGrid(dados_filtrados()["mov"], filters=True)

    @render.data_frame
    def tabela_rodape():
        return render.DataGrid(dados_filtrados()["rod"], filters=True)
    
    @render.text
    def texto_total_registos():
        dados = dados_filtrados()
        num_docs = len(dados['cab'])
        total_euros = 0.0
        if not dados['cab'].empty and "Valor total" in dados['cab'].columns:
            total_euros = dados['cab']["Valor total"].sum()
        return f"{num_docs} documentos | Total: {total_euros:,.2f} €"

    # ---------------------------------------
    # --- LÓGICA DOS GRÁFICOS ---    
    # ---------------------------------------

    @render.plot
    def grafico_barras_entidade():
        """Gráfico de barras VERTICAIS com cores diferentes, RÓTULOS e TÍTULO DINÂMICO"""
        df = dados_filtrados()["cab"]
        
        # Verificação de segurança
        if df.empty or "Valor total" not in df.columns or "Entidade" not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Sem dados para exibir", ha='center')
            return fig

        # 1. Agrupar, Somar e Ordenar
        soma_entidade = df.groupby("Entidade")["Valor total"].sum().sort_values(ascending=False)
        
        # 2. Top 15 (Mantemos a lógica visual para o gráfico não ficar gigante)
        if len(soma_entidade) > 15:
            soma_entidade = soma_entidade.head(15)

        # 3. Criar a figura
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # --- CORES ---
        num_barras = len(soma_entidade)
        cmap = plt.get_cmap('tab20') 
        lista_cores = [cmap(i) for i in np.linspace(0, 1, num_barras)]

        # 4. Gerar o gráfico
        bars = ax.bar(soma_entidade.index, soma_entidade.values, color=lista_cores)

        # 5. Adicionar valores no topo
        ax.bar_label(bars, fmt='€%.2f', padding=3, fontsize=9)
        
        # --- LÓGICA DO TÍTULO DINÂMICO ---
        
        # Ler os inputs para saber se há filtros ativos
        entidade_selecionada = input.filtro_entidade()
        ficheiro_selecionado = input.filtro_ficheiro()

        # Condição: Só mostra "(Top 15)" se NÃO houver filtros específicos
        if entidade_selecionada == "Todas" and ficheiro_selecionado == "Todos":
            titulo_base = "Total Cobrado por Entidade (Top 15)"
        else:
            titulo_base = "Total Cobrado" # Removemos a menção ao Top 15

        # Lógica de Datas
        if input.ativar_filtro_data():
            datas = input.filtro_data()
            if datas:
                start, end = datas
                s_str = start.strftime('%d/%m/%Y')
                e_str = end.strftime('%d/%m/%Y')
                titulo_final = f"{titulo_base} - {s_str} a {e_str}"
            else:
                titulo_final = titulo_base
        else:
            titulo_final = titulo_base

        # 6. Formatação
        ax.set_title(titulo_final, fontsize=12, pad=15)
        ax.set_xlabel("Entidade")
        ax.set_ylabel("Valor Total (€)")
        
        ax.set_ylim(top=soma_entidade.values.max() * 1.1)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return fig




    @render.plot
    def grafico_linha_tempo():
        """Gráfico de Linhas Múltiplas: Uma linha por Entidade (Top 5)"""
        df = dados_filtrados()["cab"]
        
        # 1. Verificação de segurança
        if df.empty or "Valor total" not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Sem dados para exibir", ha='center')
            return fig

        # 2. PREPARAÇÃO DOS DADOS
        # Nota: Mantemos o filtro Top 5 na lógica de dados para garantir que o gráfico 
        # não fica ilegível se selecionar um ficheiro com 50 entidades, por exemplo.
        top_entidades = df.groupby("Entidade")["Valor total"].sum().nlargest(5).index.tolist()
        df_top = df[df["Entidade"].isin(top_entidades)]
        
        # Agrupar por Data (Mês) e Entidade
        df_pivot = df_top.set_index("Data").groupby([pd.Grouper(freq='ME'), 'Entidade'])["Valor total"].sum().unstack(fill_value=0)

        # 3. Criar a figura
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 4. Desenhar as Linhas
        cmap = plt.get_cmap('tab10')
        
        for i, entidade in enumerate(df_pivot.columns):
            ax.plot(df_pivot.index, df_pivot[entidade], 
                    marker='o', linestyle='-', linewidth=2, 
                    label=entidade, color=cmap(i)) 

        # 5. Formatar Datas em Português
        def formatar_data_pt(x, pos):
            dt = mdates.num2date(x)
            meses = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
                     7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
            return f"{meses[dt.month]}/{str(dt.year)[2:]}"

        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(plt.FuncFormatter(formatar_data_pt))
        
        # 6. Formatar Valores (Eixo Y)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))

        # 7. --- TÍTULO DINÂMICO ---
        
        entidade_selecionada = input.filtro_entidade()
        ficheiro_selecionado = input.filtro_ficheiro()

        # Se não houver filtros, especificamos que é o Top 5.
        # Se houver filtros, usamos um título genérico.
        if entidade_selecionada == "Todas" and ficheiro_selecionado == "Todos":
            titulo_base = "Evolução Mensal (Top 5 Entidades)"
        else:
            titulo_base = "Evolução Mensal das Cobranças"

        # Adicionar datas ao título
        if input.ativar_filtro_data():
            datas = input.filtro_data()
            if datas:
                start, end = datas
                s_str = start.strftime('%d/%m/%Y')
                e_str = end.strftime('%d/%m/%Y')
                titulo_final = f"{titulo_base} - {s_str} a {e_str}"
            else:
                titulo_final = titulo_base
        else:
            titulo_final = titulo_base

        ax.set_title(titulo_final, fontsize=12, pad=15)
        ax.set_ylabel("Valor Cobrado (€)")
        ax.grid(True, linestyle='--', alpha=0.5)
        
        ax.legend(title="Entidade", bbox_to_anchor=(1.02, 1), loc='upper left')
        
        plt.xticks(rotation=45)
        plt.tight_layout()

        return fig
    


    
    @render.plot
    def grafico_evolucao_temporal():
        """Gráfico de evolução temporal (diária ou mensal) - Simples"""
        df = dados_filtrados()["cab"]
        
        # 1. Verificação de segurança
        if df.empty or "Valor total" not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Sem dados para exibir", ha='center')
            return fig

        # 2. Agrupar por Data e Somar
        df = df.sort_values("Data")
        soma_tempo = df.groupby("Data")["Valor total"].sum()

        # 3. Criar Figura
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(soma_tempo.index, soma_tempo.values, marker='o', linestyle='-', color='#55a868')

        # 4. Formatação do Eixo X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # 5. --- LÓGICA DO TÍTULO DINÂMICO ---
        titulo_base = "Evolução das Cobranças"
        
        if input.ativar_filtro_data():
            datas = input.filtro_data()
            if datas:
                start, end = datas
                # Formatar datas para Dia/Mês/Ano
                s_str = start.strftime('%d/%m/%Y')
                e_str = end.strftime('%d/%m/%Y')
                titulo_final = f"{titulo_base} - {s_str} a {e_str}"
            else:
                titulo_final = titulo_base
        else:
            titulo_final = titulo_base

        # Aplicar Título e Eixos
        ax.set_title(titulo_final, fontsize=12, pad=15)
        ax.set_ylabel("Valor (€)")
        
        # Formatar Eixo Y em Euros (opcional, mas fica bem)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))

        ax.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return fig
    



    @render.plot
    def grafico_histograma_valores():
        """Histograma: Distribuição dos montantes com linha de Média"""
        df = dados_filtrados()["cab"]
        
        # 1. Segurança
        if df.empty or "Valor total" not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Sem dados para exibir", ha='center')
            return fig

        # 2. Dados
        valores = df["Valor total"]
        ticket_medio = valores.mean()
        
        # 3. Criar Figura
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 4. Desenhar Histograma
        # bins=30: Divide os dados em 30 "gavetas" ou faixas de valor
        # color='#17a2b8': Um azul-petróleo para distinguir dos outros gráficos
        # edgecolor='white': Cria linhas brancas entre as barras para facilitar a leitura
        n, bins, patches = ax.hist(valores, bins=30, color='#17a2b8', edgecolor='white', alpha=0.9)

        # 5. Adicionar Linha do Ticket Médio (Vermelha Tracejada)
        ax.axvline(ticket_medio, color='#d9534f', linestyle='--', linewidth=2, label=f'Cobrança média: €{ticket_medio:,.2f}')

        # 6. Título Dinâmico
        titulo_base = "Frequência por Faixa de Valor"
        if input.ativar_filtro_data():
            datas = input.filtro_data()
            if datas:
                start, end = datas
                s_str = start.strftime('%d/%m/%Y')
                e_str = end.strftime('%d/%m/%Y')
                titulo_final = f"{titulo_base} ({s_str} a {e_str})"
            else:
                titulo_final = titulo_base
        else:
            titulo_final = titulo_base

        # 7. Formatação
        ax.set_title(titulo_final, fontsize=12, pad=15)
        ax.set_xlabel("Valor da Cobrança (€)")
        ax.set_ylabel("Quantidade de Documentos")
        
        # Formatar eixo X em Euros
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))
        
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        
        # Adicionar a legenda (para mostrar o valor da média)
        ax.legend()
        
        plt.tight_layout()
        return fig



    @render.plot
    def grafico_pareto_clientes():
        """Diagrama de Pareto: Barras (Valor) + Linha (% Acumulada)"""
        dados = dados_filtrados()
        df_mov = dados["mov"]
        
        # 1. Segurança e Preparação
        if df_mov.empty or "Valor" not in df_mov.columns or "NIF Cliente" not in df_mov.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Sem movimentos para exibir", ha='center')
            return fig

        # Garantir que o valor é numérico
        df_mov["Valor"] = pd.to_numeric(df_mov["Valor"], errors='coerce').fillna(0)

        # 2. Agrupar por NIF Cliente
        pareto_df = df_mov.groupby("NIF Cliente")["Valor"].sum().sort_values(ascending=False)
        
        # Filtrar Top 20
        top_n = 20
        if len(pareto_df) > top_n:
            pareto_df = pareto_df.head(top_n)

        # 3. Calcular Percentagem Acumulada
        total_geral = pareto_df.sum() 
        cum_percentage = pareto_df.cumsum() / total_geral * 100

        # 4. Criar Figura e Eixo Principal (Barras)
        fig, ax1 = plt.subplots(figsize=(12, 7))
        
        ax1.bar(pareto_df.index, pareto_df.values, color="#4c72b0", label="Valor Cobrado")
        ax1.set_ylabel("Valor Cobrado (€)", color="#4c72b0", fontweight='bold')
        ax1.tick_params(axis='y', labelcolor="#4c72b0")
        ax1.set_xlabel("NIF Cliente")
        
        # Formatar Eixo Y1 em Euros
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))

        # 5. Criar Eixo Secundário (Linha)
        ax2 = ax1.twinx()
        
        ax2.plot(pareto_df.index, cum_percentage.values, color="#c44e52", marker="o", linewidth=2, label="% Acumulada")
        ax2.set_ylabel("Percentagem Acumulada", color="#c44e52", fontweight='bold')
        ax2.tick_params(axis='y', labelcolor="#c44e52")
        
        # Formatar Eixo Y2 em Percentagem
        ax2.yaxis.set_major_formatter(PercentFormatter())
        ax2.set_ylim(0, 110)

        # 6. Linha de Referência dos 80%
        ax2.axhline(80, color="gray", linestyle="--", linewidth=1, alpha=0.7)
        ax2.text(len(pareto_df)-1, 80, ' Regra 80%', va='center', ha='left', color="gray", fontsize=9)

        # 7. Título Dinâmico
        titulo_base = f"Top {top_n} Clientes (Pareto)"
        if input.ativar_filtro_data():
            datas = input.filtro_data()
            if datas:
                start, end = datas
                s_str = start.strftime('%d/%m/%Y')
                e_str = end.strftime('%d/%m/%Y')
                titulo_final = f"{titulo_base} - {s_str} a {e_str}"
            else:
                titulo_final = titulo_base
        else:
            titulo_final = titulo_base

        plt.title(titulo_final, fontsize=12, pad=20)
        
        # Rodar labels do eixo X
        ax1.set_xticklabels(pareto_df.index, rotation=45, ha='right')
        
        plt.tight_layout()
        return fig
    

    # -----------------------------------
    # --- CHECKBOX DINAMICAS
    # -----------------------------------

    @reactive.effect
    def gerir_opcoes_graficos():
        # 1. Ler os filtros
        entidade = input.filtro_entidade()
        ficheiro = input.filtro_ficheiro()

        # 2. Ler seleção atual de forma isolada (para não criar ciclo infinito)
        with reactive.isolate():
            selecao_atual = list(input.selecao_graficos())

        # 3. Lógica de atualização
        if entidade == "Todas" and ficheiro == "Todos":
            # CASO 1: Mostrar "Evolução Global"
            novas_opcoes = {
                "g_barras": "Top Entidades",
                "g_linhas": "Evolução Mensal",
                "g_linhas_global": "Evolução Global", 
                "g_hist": "Histograma",
                "g_pareto": "Pareto"
            }
            
            # --- O TRUQUE ESTÁ AQUI ---
            # Se a opção global não estiver selecionada, adicionamo-la manualmente
            if "g_linhas_global" not in selecao_atual:
                selecao_atual.append("g_linhas_global")
            # --------------------------

        else:
            # CASO 2: Esconder "Evolução Global"
            novas_opcoes = {
                "g_barras": "Top Entidades",
                "g_linhas": "Evolução Mensal",
                "g_hist": "Histograma",
                "g_pareto": "Pareto"
            }
            
            # Removemos da seleção para não causar erros (pois a opção deixou de existir)
            if "g_linhas_global" in selecao_atual:
                selecao_atual.remove("g_linhas_global")

        # 4. Atualizar o Input
        ui.update_checkbox_group(
            "selecao_graficos",
            choices=novas_opcoes,
            selected=selecao_atual # Enviamos a lista corrigida
        )




app = App(app_ui, server)