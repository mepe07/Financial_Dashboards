from shiny import App, render, ui, reactive
import pandas as pd
from src import ler_ficheiros_ps2
from src import converterParaPandas

# --- 1. CARREGAMENTO DE DADOS (Executa apenas 1 vez ao iniciar a App) ---
dados_brutos = ler_ficheiros_ps2()
pacote = converterParaPandas(dados_brutos)

# Extrair as tabelas globais
df_cabecalho_global = pacote["cabecalho"]
df_movimentos_global = pacote["movimentos"]
df_rodape_global = pacote["rodape"]

# Obter lista de ficheiros únicos para o filtro (Se a coluna Origem existir)
if "Origem" in df_cabecalho_global.columns:
    lista_ficheiros = df_cabecalho_global["Origem"].unique().tolist()
else:
    lista_ficheiros = []

# --- 2. INTERFACE (UI) ---
app_ui = ui.page_sidebar(
    # Barra Lateral
    ui.sidebar(
        ui.h3("Filtros"),
        ui.input_select(
            "filtro_ficheiro", 
            "Escolher Ficheiro:", 
            choices=lista_ficheiros, 
            multiple=False
        ),
        ui.hr(),
        ui.p("Total de registos carregados:"),
        ui.output_text("texto_total_registos")
    ),
    
    # Área Principal com Abas
    ui.page_fluid(
        ui.h2("Análise de Ficheiros PS2"),
        ui.navset_card_underline(
            ui.nav_panel("Visão Geral (Cabeçalhos)", ui.output_data_frame("tabela_cabecalho")),
            ui.nav_panel("Movimentos Detalhados", ui.output_data_frame("tabela_movimentos")),
            ui.nav_panel("Sumários (Rodapés)", ui.output_data_frame("tabela_rodape")),
        )
    )
)

# --- 3. SERVIDOR (Lógica) ---
def server(input, output, session):

    # --- Cálculos Reativos (Filtram os dados quando o user muda a seleção) ---
    
    @reactive.calc
    def dados_filtrados():
        # Descobre qual ficheiro o utilizador escolheu
        ficheiro_escolhido = input.filtro_ficheiro()
        
        # Filtra as 3 tabelas
        # Nota: Usamos .copy() para não estragar os dados originais
        cab = df_cabecalho_global[df_cabecalho_global["Origem"] == ficheiro_escolhido] if not df_cabecalho_global.empty else pd.DataFrame()
        mov = df_movimentos_global[df_movimentos_global["Origem"] == ficheiro_escolhido] if not df_movimentos_global.empty else pd.DataFrame()
        rod = df_rodape_global[df_rodape_global["Origem"] == ficheiro_escolhido] if not df_rodape_global.empty else pd.DataFrame()
        
        return {"cab": cab, "mov": mov, "rod": rod}

    # --- Renderização das Tabelas ---

    @render.data_frame
    def tabela_cabecalho():
        dados = dados_filtrados()
        return render.DataGrid(dados["cab"], filters=True)

    @render.data_frame
    def tabela_movimentos():
        dados = dados_filtrados()
        return render.DataGrid(dados["mov"], filters=True)

    @render.data_frame
    def tabela_rodape():
        dados = dados_filtrados()
        return render.DataGrid(dados["rod"], filters=True)
    
    @render.text
    def texto_total_registos():
        # Mostra o total de movimentos do ficheiro selecionado
        dados = dados_filtrados()
        return f"{len(dados['mov'])} movimentos encontrados."

# --- 4. LANÇAR APP ---
app = App(app_ui, server)