# from shiny import App, render, ui, reactive
# import pandas as pd
# from datetime import date
# from src import ler_ficheiros_ps2
# from src import converterParaPandas
# import matplotlib.pyplot as plt


# # --- 1. CARREGAMENTO DE DADOS ---
# print("A carregar dados para o Shiny...")
# dados_brutos = ler_ficheiros_ps2()
# pacote = converterParaPandas(dados_brutos)

# df_cabecalho_global = pacote["cabecalho"]
# df_movimentos_global = pacote["movimentos"]
# df_rodape_global = pacote["rodape"]

# # --- PREPARAÇÃO DOS FILTROS ---

# # A. Limites de Data (para o calendário)
# data_min = date.today()
# data_max = date.today()

# if not df_cabecalho_global.empty and "Data" in df_cabecalho_global.columns:
#     # Converter para data python (remove as horas)
#     dates = pd.to_datetime(df_cabecalho_global["Data"]).dt.date
#     data_min = dates.min()
#     data_max = dates.max()

# # B. Lista de Ficheiros
# if "Origem" in df_cabecalho_global.columns:
#     lista_ficheiros = sorted(df_cabecalho_global["Origem"].unique().tolist())
# else:
#     lista_ficheiros = []
# opcoes_ficheiros = ["Todos"] + lista_ficheiros

# # C. Lista de Entidades
# if "Entidade" in df_cabecalho_global.columns:
#     lista_entidades = sorted(df_cabecalho_global["Entidade"].unique().tolist())
# else:
#     lista_entidades = []
# opcoes_entidades = ["Todas"] + lista_entidades


# # --- 2. INTERFACE (UI) ---
# app_ui = ui.page_sidebar(
#     ui.sidebar(
#         ui.h3("Filtros"),
        
#         # Filtro 1: Data (NOVO)
#         ui.input_date_range(
#             "filtro_data",
#             "Intervalo de Datas:",
#             start=data_min,
#             end=data_max,
#             min=data_min,
#             max=data_max,
#             format="dd/mm/yyyy",
#             language="pt"
#         ),

#         ui.hr(),

#         # Filtro 2: Entidade
#         ui.input_select(
#             "filtro_entidade", 
#             "Entidade:", 
#             choices=opcoes_entidades, 
#             selected="Todas"
#         ),

#         # Filtro 3: Ficheiro
#         ui.input_select(
#             "filtro_ficheiro", 
#             "Ficheiro Específico:", 
#             choices=opcoes_ficheiros, 
#             selected="Todos"
#         ),
        
#         ui.hr(),
#         ui.p("Resumo:"),
#         ui.output_text("texto_total_registos")
#     ),
    
#     ui.page_fluid(
#         ui.h2("Dashboard Financeiro PS2"),
#         ui.navset_card_underline(
#             ui.nav_panel("Visão Geral", ui.output_data_frame("tabela_cabecalho")),
#             ui.nav_panel("Movimentos", ui.output_data_frame("tabela_movimentos")),
#             ui.nav_panel("Totais (Rodapé)", ui.output_data_frame("tabela_rodape")),
#         )
#     )
# )

# # --- 3. SERVIDOR (Lógica) ---
# def server(input, output, session):

#     # --- CÁLCULO CENTRAL (Coração da App) ---
#     @reactive.calc
#     def dados_filtrados():
#         entidade = input.filtro_entidade()
#         ficheiro = input.filtro_ficheiro()
#         datas = input.filtro_data() # Retorna tupla (start, end)

#         # Cópias de segurança
#         cab = df_cabecalho_global.copy()
        
#         # 1. FILTRO DE DATA (Aplica primeiro ao cabeçalho)
#         if not cab.empty and datas:
#             start_date, end_date = datas
#             # Garante que a coluna é datetime
#             cab["Data"] = pd.to_datetime(cab["Data"])
#             # Filtra entre as datas escolhidas
#             mask = (cab["Data"].dt.date >= start_date) & (cab["Data"].dt.date <= end_date)
#             cab = cab.loc[mask]

#         # 2. FILTRO DE ENTIDADE
#         if entidade != "Todas":
#             cab = cab[cab["Entidade"] == entidade]

#         # 3. FILTRO DE FICHEIRO
#         if ficheiro != "Todos":
#             cab = cab[cab["Origem"] == ficheiro]

#         # --- PROPAGAÇÃO AOS OUTROS DADOS ---
#         # Agora que temos o cabeçalho filtrado, descobrimos quais os ficheiros que sobraram
#         # e usamos isso para filtrar os movimentos.
        
#         ficheiros_validos = cab["Origem"].unique()
        
#         mov = df_movimentos_global[df_movimentos_global["Origem"].isin(ficheiros_validos)]
#         rod = df_rodape_global[df_rodape_global["Origem"].isin(ficheiros_validos)]

#         return {"cab": cab, "mov": mov, "rod": rod}

#     # --- RENDERIZAÇÃO ---
#     @render.data_frame
#     def tabela_cabecalho():
#         # Formatar a data para ficar bonita na tabela (só dia-mês-ano)
#         df = dados_filtrados()["cab"].copy()
#         if not df.empty and "Data" in df.columns:
#             df["Data"] = df["Data"].dt.strftime('%d/%m/%Y')
#         return render.DataGrid(df, filters=True)

#     @render.data_frame
#     def tabela_movimentos():
#         return render.DataGrid(dados_filtrados()["mov"], filters=True)

#     @render.data_frame
#     def tabela_rodape():
#         return render.DataGrid(dados_filtrados()["rod"], filters=True)
    
#     @render.text
#     def texto_total_registos():
#         dados = dados_filtrados()
#         num_movs = len(dados['mov'])
        
#         total_euros = 0.0
#         if not dados['cab'].empty and "Valor total" in dados['cab'].columns:
#             total_euros = dados['cab']["Valor total"].sum()
            
#         return f"{num_movs} movimentos | {total_euros:,.2f} €"

# app = App(app_ui, server)








from shiny import App, render, ui, reactive
import pandas as pd
from datetime import date
# Se der erro nestes imports locais ao testar, comente-os e use dados ficticios
from src import ler_ficheiros_ps2
from src import converterParaPandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# --- 1. CARREGAMENTO DE DADOS ---
print("A carregar dados para o Shiny...")
dados_brutos = ler_ficheiros_ps2()
pacote = converterParaPandas(dados_brutos)

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
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("Filtros"),
        
        ui.input_date_range(
            "filtro_data", "Intervalo de Datas:",
            start=data_min, end=data_max, min=data_min, max=data_max,
            format="dd/mm/yyyy", language="pt"
        ),

        ui.hr(),

        ui.input_select(
            "filtro_entidade", "Entidade:", 
            choices=opcoes_entidades, selected="Todas"
        ),

        ui.input_select(
            "filtro_ficheiro", "Ficheiro Específico:", 
            choices=opcoes_ficheiros, selected="Todos"
        ),
        
        ui.hr(),
        ui.p("Resumo:"),
        ui.output_text("texto_total_registos")
    ),
    
    ui.page_fluid(
        ui.h2("Dashboard Financeiro PS2"),
        ui.navset_card_underline(
            ui.nav_panel("Visão Geral", ui.output_data_frame("tabela_cabecalho")),
            
            # ### NOVO: Aba de Gráficos ###
            ui.nav_panel("Análise Gráfica", 
                ui.layout_columns(
                    ui.card(
                        ui.card_header("Top Entidades (Valor Total)"),
                        ui.output_plot("grafico_barras_entidade")
                    ),
                    ui.card(
                        ui.card_header("Evolução Temporal"),
                        ui.output_plot("grafico_linha_tempo")
                    ),
                )
            ),
            # -----------------------------

            ui.nav_panel("Movimentos", ui.output_data_frame("tabela_movimentos")),
            ui.nav_panel("Totais (Rodapé)", ui.output_data_frame("tabela_rodape")),
        )
    )
)

# --- 3. SERVIDOR (Lógica) ---
def server(input, output, session):

    @reactive.calc
    def dados_filtrados():
        entidade = input.filtro_entidade()
        ficheiro = input.filtro_ficheiro()
        datas = input.filtro_data()

        cab = df_cabecalho_global.copy()
        
        # 1. FILTRO DE DATA
        if not cab.empty and datas:
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

        ficheiros_validos = cab["Origem"].unique()
        mov = df_movimentos_global[df_movimentos_global["Origem"].isin(ficheiros_validos)]
        rod = df_rodape_global[df_rodape_global["Origem"].isin(ficheiros_validos)]

        return {"cab": cab, "mov": mov, "rod": rod}

    # --- TABELAS ---
    @render.data_frame
    def tabela_cabecalho():
        df = dados_filtrados()["cab"].copy()
        if not df.empty and "Data" in df.columns:
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

    # --- ### NOVO: LÓGICA DOS GRÁFICOS ### ---
    
    @render.plot
    def grafico_barras_entidade():
        """Gráfico de barras: Quem são as entidades com maior valor acumulado"""
        df = dados_filtrados()["cab"]
        
        if df.empty or "Valor total" not in df.columns or "Entidade" not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Sem dados para exibir", ha='center')
            return fig

        # Agrupar por entidade e somar
        # Se selecionou "Todas", mostra as Top 10. Se selecionou 1, mostra só essa.
        soma_entidade = df.groupby("Entidade")["Valor total"].sum().sort_values(ascending=True)
        
        # Se houver muitas, pegar só as top 10 para o gráfico não ficar ilegível
        if len(soma_entidade) > 15:
            soma_entidade = soma_entidade.tail(15)

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(soma_entidade.index, soma_entidade.values, color="#4c72b0")
        
        ax.set_xlabel("Valor Total (€)")
        ax.set_title("Total Cobrado por Entidade (Top 15)")
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Ajustar layout para nomes não cortarem
        plt.tight_layout()
        return fig

    @render.plot
    def grafico_linha_tempo():
        """Gráfico de evolução temporal (diária ou mensal)"""
        df = dados_filtrados()["cab"]
        
        if df.empty or "Valor total" not in df.columns:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "Sem dados para exibir", ha='center')
            return fig

        # Agrupar por Data
        df = df.sort_values("Data")
        soma_tempo = df.groupby("Data")["Valor total"].sum()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(soma_tempo.index, soma_tempo.values, marker='o', linestyle='-', color='#55a868')

        # Formatação de datas no eixo X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        plt.xticks(rotation=45)
        ax.set_ylabel("Valor (€)")
        ax.set_title("Evolução das Cobranças no Período Selecionado")
        ax.grid(True)
        
        plt.tight_layout()
        return fig

app = App(app_ui, server)