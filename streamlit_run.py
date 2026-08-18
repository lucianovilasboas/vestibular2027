import streamlit as st 
import pandas as pd 
import plotly.express as px
from funcoes import load_data
from funcoes import load_cards
from funcoes import load_escolas
from funcoes import load_escolas_resumo
from funcoes import get_last_modified_file

st.set_page_config(page_title="Vestibular IFMG 2027",  page_icon="📊", layout="wide")

# --- CSS CUSTOMIZADO ---
st.markdown("""
<style>
    /* Fonte e fundo */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    }
    .stApp {
        background-color: #f8f9fa;
    }

    /* Cabeçalho */
    h1, h2, h3 {
        color: #1a3d2f !important;
    }

    /* Cards KPI */
    .kpi-card {
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 6px solid;
        background: #ffffff;
        color: #212529;
    }
    .kpi-label {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.75;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        line-height: 1.1;
    }
    .kpi-green { border-left-color: #2e7d32; }
    .kpi-blue  { border-left-color: #1565c0; }
    .kpi-orange{ border-left-color: #ef6c00; }
    .kpi-purple{ border-left-color: #6a1b9a; }
    .kpi-teal  { border-left-color: #00838f; }
    .kpi-red   { border-left-color: #c62828; }

    /* Bloco de painel */
    .panel-title {
        font-size: 20px;
        font-weight: 700;
        color: #1a3d2f;
        margin-bottom: 10px;
    }

    /* Selectbox mais bonito */
    .stSelectbox [data-baseweb="select"] > div {
        border-radius: 8px;
        border: 1px solid #ced4da;
    }

    /* ===== HEADER INSTITUCIONAL ===== */
    .header-banner {
        background: linear-gradient(135deg, #0f2e24 0%, #1a4a38 55%, #2e7d32 100%);
        border-radius: 16px;
        padding: 28px 32px 24px 32px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
        position: relative;
        overflow: hidden;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.12);
    }
    /* brilho decorativo no canto */
    .header-banner::before {
        content: "";
        position: absolute;
        top: -80px;
        right: -80px;
        width: 260px;
        height: 260px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0) 70%);
        pointer-events: none;
    }
    .header-banner::after {
        content: "";
        position: absolute;
        bottom: -90px;
        left: -70px;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(46,125,50,0.45) 0%, rgba(46,125,50,0) 70%);
        pointer-events: none;
    }
    .header-title {
        font-size: 26px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
        text-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }
    .header-subtitle {
        font-size: 15px;
        color: rgba(255,255,255,0.85);
        margin-bottom: 14px;
        font-weight: 400;
    }
    .header-banner img {
        border-radius: 10px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        border: 2px solid rgba(255,255,255,0.25);
        max-width: 340px !important;
        width: auto !important;
        height: auto !important;
        margin: 0 auto;
        display: block;
    }
    .header-update {
        margin-top: 14px;
        font-size: 12.5px;
        color: rgba(255,255,255,0.75);
        background: rgba(0,0,0,0.25);
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        letter-spacing: 0.3px;
    }

    /* Footer */
    .footer-note {
        text-align: center;
        color: #6c757d;
        font-size: 13px;
        margin-top: 24px;
    }
</style>
""", unsafe_allow_html=True)


# Função para renderizar card KPI customizado
def kpi_card(col, label, value, cor="kpi-green"):
    with col:
        st.markdown(
            f'<div class="kpi-card {cor}">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


df_all = load_data()  
df_cards = load_cards()
df_escolas = load_escolas()
df_escolas_resumo = load_escolas_resumo()

# ===== HEADER INSTITUCIONAL (não fixo - não atrapalha navegação) =====
import base64

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

img_b64 = img_to_base64("vestibular-2027-imagem.png")
data_atualizacao = get_last_modified_file('dados/processed/all_data.csv')

st.markdown(
    f"""
    <div class="header-banner">
        <div class="header-title">🎓 Processo Seletivo IFMG 2027</div>
        <div class="header-subtitle">Acompanhamento de inscrições em tempo real</div>
        <img src="data:image/png;base64,{img_b64}" alt="Vestibular IFMG 2027"/>
        <div class="header-update">🕒 Última atualização: {data_atualizacao}</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Labels amigáveis por modalidade
MODALIDADE_LABELS = {
    "INT": "Cursos Técnicos Integrados",
    "SUB": "Cursos Técnicos Subsequentes",
    "SUP": "Cursos de Graduação",
}
LABEL_MODALIDADE = {v: k for k, v in MODALIDADE_LABELS.items()}
TOTAL_LABEL = "Total"

COTA_LABELS = {
    "LB_PPI": "LB - Pretos/Pardos/Indígenas",
    "LB_Q": "LB - Quilombolas",
    "LB_PCD": "LB - Pessoa com Deficiência",
    "LB_EP": "LB - Escola Pública",
    "LI_PPI": "LI - Pretos/Pardos/Indígenas",
    "LI_Q": "LI - Quilombolas",
    "LI_PCD": "LI - Pessoa com Deficiência",
    "LI_EP": "LI - Escola Pública",
    "AC": "Ampla Concorrência",
}

def fmt(v):
    return f"{v:,}".replace(",", ".")


def render_cards_institucionais(df_cards):
    """Renderiza os cards do /paineldecontrole com seletor de modalidade."""
    if df_cards.empty:
        return
    modalidades_cards = sorted(df_cards['Modalidade'].unique())
    modalidades_cards_labels = [TOTAL_LABEL] + [MODALIDADE_LABELS.get(m, m) for m in modalidades_cards]

    card_select_cols = st.columns([3, 1, 3])
    with card_select_cols[0]:
        card_modalidade_label = st.selectbox('Selecione a modalidade:', modalidades_cards_labels, key='card_modalidade_select', index=0)

    if card_modalidade_label == TOTAL_LABEL:
        ultima_cards_data = df_cards['Data'].max()
        df_cards_ultima = df_cards[df_cards['Data'] == ultima_cards_data]
        inscricoes = int(df_cards_ultima['Inscricoes'].sum())
        inscricoes_pagas = int(df_cards_ultima['InscricoesPagas'].sum())
        isencao = int(df_cards_ultima['Isencao'].sum())
        isencao_deferidas = int(df_cards_ultima['IsencaoDeferidas'].sum())
        cond_especiais = int(df_cards_ultima['CondicoesEspeciais'].sum())
        cond_deferidas = int(df_cards_ultima['CondicoesDeferidas'].sum())
    else:
        card_modalidade = LABEL_MODALIDADE.get(card_modalidade_label, card_modalidade_label)
        df_cards_mod = df_cards[df_cards['Modalidade'] == card_modalidade]
        ultima_cards_data = df_cards_mod['Data'].max()
        cards_row = df_cards_mod[df_cards_mod['Data'] == ultima_cards_data].iloc[0]
        inscricoes = int(cards_row.get('Inscricoes', 0))
        inscricoes_pagas = int(cards_row.get('InscricoesPagas', 0))
        isencao = int(cards_row.get('Isencao', 0))
        isencao_deferidas = int(cards_row.get('IsencaoDeferidas', 0))
        cond_especiais = int(cards_row.get('CondicoesEspeciais', 0))
        cond_deferidas = int(cards_row.get('CondicoesDeferidas', 0))

    card_cols = st.columns(4)
    kpi_card(card_cols[0], "Inscrições", fmt(inscricoes), "kpi-green")
    kpi_card(card_cols[1], "Inscrições Pagas", fmt(inscricoes_pagas), "kpi-blue")
    kpi_card(card_cols[2], "Solic. de Isenção", fmt(isencao), "kpi-orange")
    kpi_card(card_cols[3], "Isenções Deferidas", fmt(isencao_deferidas), "kpi-purple")

    if cond_especiais > 0 or cond_deferidas > 0:
        cond_cols = st.columns(2)
        kpi_card(cond_cols[0], "Solic. de Condições Especiais", fmt(cond_especiais), "kpi-teal")
        kpi_card(cond_cols[1], "Condições Especiais Deferidas", fmt(cond_deferidas), "kpi-red")


def ultima_coleta_por_modalidade(df):
    """Retorna a última coleta de cada modalidade (evita timestamps divergentes na mesma coleta)."""
    if df.empty:
        return df
    frames = []
    for mod in df['Modalidade'].unique():
        dmod = df[df['Modalidade'] == mod]
        ult = dmod['Data'].max()
        frames.append(dmod[dmod['Data'] == ult])
    return pd.concat(frames, ignore_index=True)


def plot_evolucao(df, titulo="Evolução das Inscrições ao Longo do Tempo", key="evolucao"):
    df_grouped = df.groupby("Data")['Inscritos'].sum().reset_index().sort_values("Data")
    if df_grouped.empty:
        st.info("Sem dados para exibir.")
        return
    fig = px.line(df_grouped, x="Data", y="Inscritos", markers=True,
                  title=titulo, height=500, color_discrete_sequence=["#2e7d32"])
    fig.update_traces(mode="lines+markers", hovertemplate="%{y}")
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial", size=14),
        title=dict(font=dict(size=18, color="#1a3d2f")),
        xaxis=dict(gridcolor="#e9ecef"),
        yaxis=dict(gridcolor="#e9ecef"),
    )
    st.plotly_chart(fig, width='stretch', key=key)


# ===== ABAS =====
tab_geral, tab_curso, tab_escola = st.tabs(["📊 Visão Geral", "🎓 Por Curso", "🏫 Por Escola"])

# ============ ABA 1: VISÃO GERAL ============
with tab_geral:
    st.markdown('<div class="panel-title">📊 Painel Institucional - IFMG 2027</div>', unsafe_allow_html=True)
    render_cards_institucionais(df_cards)

    st.markdown("---")

    # --- SELETORES (campus, modalidade, curso) ---
    cols = st.columns([3,1,3])

    with cols[0]:
        unidades = [TOTAL_LABEL] + sorted([u for u in df_all['Unidade'].unique() if u != 'Todas'])
        unidade = st.selectbox('Selecione o campus:', unidades, key='unidade_select', index=0)

    if unidade == TOTAL_LABEL:
        df_unidade = df_all
        modalidades_disponiveis = sorted(df_all['Modalidade'].unique())
    else:
        df_unidade = df_all[df_all['Unidade'] == unidade]
        modalidades_disponiveis = sorted(df_unidade['Modalidade'].unique())

    modalidade_labels_disponiveis = [TOTAL_LABEL] + [MODALIDADE_LABELS.get(m, m) for m in modalidades_disponiveis]

    with cols[1]:
        modalidade_label = st.selectbox('Selecione a modalidade:', modalidade_labels_disponiveis, key='modalidade_select', index=0)
        modalidade = LABEL_MODALIDADE.get(modalidade_label, modalidade_label)

    ultima_data = df_all['Data'].max()
    if modalidade != TOTAL_LABEL:
        # Última coleta considerando a modalidade selecionada (cada modalidade tem seu timestamp)
        ultima_data = df_unidade[df_unidade['Modalidade'] == modalidade]['Data'].max()

    if modalidade == TOTAL_LABEL:
        df_filter = ultima_coleta_por_modalidade(df_unidade)
        df_filter_mapa = df_unidade
    else:
        df_filter = df_unidade[(df_unidade['Modalidade'] == modalidade) & (df_unidade['Data'] == ultima_data)]
        df_filter_mapa = df_unidade[df_unidade['Modalidade'] == modalidade]

    with cols[2]:
        cursos = sorted(df_filter['Curso'].unique())
        curso = st.selectbox('Selecione o curso:', [TOTAL_LABEL] + cursos, key='curso_select', index=0)

    if curso != TOTAL_LABEL:
        df_filter = df_filter[df_filter['Curso'] == curso]
        df_filter_mapa = df_filter_mapa[df_filter_mapa['Curso'] == curso]

    # Labels para exibição
    unidade_label = "IFMG - Total" if unidade == TOTAL_LABEL else unidade
    modalidade_label_exib = "Todas as Modalidades" if modalidade == TOTAL_LABEL else MODALIDADE_LABELS.get(modalidade, modalidade)

    # --- EVOLUÇÃO DAS INSCRIÇÕES ---
    st.subheader('📈 Evolução das Inscrições')
    st.write(f"**Unidade:** {unidade_label} | **Modalidade:** {modalidade_label_exib} | **Curso:** {curso} | **Total de inscrições:** {df_filter['Inscritos'].sum()}")
    plot_evolucao(df_filter_mapa, key="evol_visao_geral")

    st.subheader('📊 Resumo dos dados')
    colunas = ["Unidade","Curso","Modalidade","Vagas","Inscritos","Inscr./Vagas","Data"]
    st.dataframe(df_filter[colunas].sort_values(by="Inscritos", ascending=False).reset_index(drop=True), width='stretch')

    st.markdown("""___""")

    st.subheader('📊 Comparativo de Inscrições por Unidade')

    df_all_filtered = df_all[df_all['Data'] == ultima_data]
    df_all_filtered = df_all_filtered[df_all_filtered['Unidade'] != 'Todas']
    
    df_unidades_modalidades = df_all_filtered.groupby(['Unidade', 'Modalidade'])['Inscritos'].sum().reset_index()
    df_unidades_modalidades = df_unidades_modalidades.sort_values(by='Inscritos', ascending=False)
    df_unidades_modalidades['Modalidade'] = df_unidades_modalidades['Modalidade'].map(MODALIDADE_LABELS).fillna(df_unidades_modalidades['Modalidade'])

    fig_barras = px.bar(
        df_unidades_modalidades, 
        x='Unidade', 
        y='Inscritos', 
        color='Modalidade',
        title='Total de Inscrições por Unidade e Modalidade',
        barmode='group'
    )
    
    fig_barras.update_layout(
        xaxis_title="Unidade",
        yaxis_title="Total de Inscrições",
        height=600,
        showlegend=True,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial", size=14),
        title=dict(font=dict(size=18, color="#1a3d2f")),
    )
    
    fig_barras.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_barras, width='stretch', key='bar_unidades')

    st.subheader('📈 Evolução das Inscrições por Unidade')

    df_evolucao_unidades = df_all[df_all['Unidade'] != 'Todas'].groupby(['Data', 'Unidade'])['Inscritos'].sum().reset_index()
    
    df_totais_unidades = df_evolucao_unidades.groupby('Unidade')['Inscritos'].sum().sort_values(ascending=False)
    ordem_legenda = df_totais_unidades.index.tolist()

    fig_evolucao = px.line(
        df_evolucao_unidades,
        x='Data',
        y='Inscritos',
        color='Unidade',
        title='Evolução das Inscrições por Unidade',
        markers=True,
        category_orders={'Unidade': ordem_legenda}
    )
    fig_evolucao.update_traces(mode="lines+markers", hovertemplate="%{y}")
    fig_evolucao.update_layout(
        height=600,
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Arial", size=14),
        title=dict(font=dict(size=18, color="#1a3d2f")),
    )

    st.plotly_chart(fig_evolucao, width='stretch', key='evol_unidades')

# ============ ABA 2: POR CURSO ============
with tab_curso:
    st.markdown('<div class="panel-title">🎓 Inscrições por Curso</div>', unsafe_allow_html=True)

    if df_all.empty:
        st.warning("Sem dados de cursos. Execute o scraper_v4.py primeiro.")
    else:
        cols_curso = st.columns([3, 3, 3])

        with cols_curso[0]:
            unidades_curso = [TOTAL_LABEL] + sorted([u for u in df_all['Unidade'].unique() if u != 'Todas'])
            unidade_curso = st.selectbox('Campus:', unidades_curso, key='unidade_curso_select', index=0)

        if unidade_curso == TOTAL_LABEL:
            df_curso_base = df_all
            mods_curso = sorted(df_all['Modalidade'].unique())
        else:
            df_curso_base = df_all[df_all['Unidade'] == unidade_curso]
            mods_curso = sorted(df_curso_base['Modalidade'].unique())

        with cols_curso[1]:
            mod_curso_label = st.selectbox('Modalidade:', [TOTAL_LABEL] + [MODALIDADE_LABELS.get(m, m) for m in mods_curso], key='mod_curso_select', index=0)
            mod_curso = LABEL_MODALIDADE.get(mod_curso_label, mod_curso_label)

        if mod_curso == TOTAL_LABEL:
            df_curso_base = df_curso_base
        else:
            df_curso_base = df_curso_base[df_curso_base['Modalidade'] == mod_curso]

        ultima_data_curso = df_curso_base['Data'].max()
        if mod_curso == TOTAL_LABEL:
            df_curso_ultima = ultima_coleta_por_modalidade(df_curso_base)
        else:
            df_curso_ultima = df_curso_base[df_curso_base['Data'] == ultima_data_curso]

        with cols_curso[2]:
            cursos_curso = sorted(df_curso_ultima['Curso'].unique())
            curso_escolhido = st.selectbox('Curso:', [TOTAL_LABEL] + cursos_curso, key='curso_curso_select', index=0)

        if curso_escolhido != TOTAL_LABEL:
            df_curso_sel = df_curso_ultima[df_curso_ultima['Curso'] == curso_escolhido]
        else:
            df_curso_sel = df_curso_ultima

        df_curso_sel = df_curso_sel[df_curso_sel['Curso'] != 'Todos']

        # KPIs da seleção
        k1, k2, k3, k4 = st.columns(4)
        kpi_card(k1, "Inscritos", fmt(int(df_curso_sel['Inscritos'].sum())), "kpi-green")
        if 'Homologados' in df_curso_sel.columns:
            kpi_card(k2, "Homologados", fmt(int(df_curso_sel['Homologados'].sum())), "kpi-blue")
        kpi_card(k3, "Vagas", fmt(int(df_curso_sel['Vagas'].sum())), "kpi-orange")
        kpi_card(k4, "Inscr./Vagas", f"{df_curso_sel['Inscr./Vagas'].mean():.2f}", "kpi-purple")

        st.markdown("---")

        # Evolução da seleção
        st.subheader('📈 Evolução das Inscrições')
        df_curso_evol = df_curso_base
        if curso_escolhido != TOTAL_LABEL:
            df_curso_evol = df_curso_base[df_curso_base['Curso'] == curso_escolhido]
        plot_evolucao(df_curso_evol, key="evol_por_curso")

        # Tabela de cursos
        st.subheader('📋 Tabela de Cursos (última coleta)')
        colunas_curso = ["Unidade","Curso","Vagas","Inscritos","Inscr./Vagas"]
        if 'Homologados' in df_curso_sel.columns:
            colunas_curso += ["Homologados","Homolog./Vagas"]
        st.dataframe(df_curso_sel[colunas_curso].sort_values(by="Inscritos", ascending=False).reset_index(drop=True), width='stretch')

        # Análise de cotas (opção 1)
        if 'AC' in df_curso_sel.columns:
            st.markdown("---")
            st.subheader('🎯 Reserva de Vagas por Cota (opção 1)')
            cota_cols = [c for c in COTA_LABELS if c in df_curso_sel.columns]
            if cota_cols:
                df_cotas = df_curso_sel[['Curso'] + cota_cols].groupby('Curso', as_index=False).sum(numeric_only=True)
                df_cotas_melt = df_cotas.melt(id_vars='Curso', var_name='Cota', value_name='Inscritos')
                df_cotas_melt['Cota'] = df_cotas_melt['Cota'].map(COTA_LABELS)

                fig_cotas = px.bar(
                    df_cotas_melt,
                    x='Inscritos', y='Cota', color='Cota',
                    orientation='h',
                    title='Inscritos por Cota',
                    height=max(400, 60 * len(cota_cols) + 100),
                )
                fig_cotas.update_layout(
                    showlegend=False,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Segoe UI, Arial", size=14),
                    title=dict(font=dict(size=18, color="#1a3d2f")),
                )
                st.plotly_chart(fig_cotas, width='stretch', key='bar_cotas')

                st.dataframe(df_cotas.sort_values(by='Curso'), width='stretch')

# ============ ABA 3: POR ESCOLA ============
with tab_escola:
    st.markdown('<div class="panel-title">🏫 Inscrições por Escola de Origem</div>', unsafe_allow_html=True)

    if df_escolas.empty:
        st.warning("Sem dados de escolas. Execute o scraper_v4.py para coletar o painel de escolas.")
    else:
        # Seletor de modalidade (escolas)
        mods_escola = sorted(df_escolas['Modalidade'].unique())
        col_esc = st.columns([2, 2, 2])
        with col_esc[0]:
            mod_escola_label = st.selectbox('Modalidade (escolas):', [TOTAL_LABEL] + [MODALIDADE_LABELS.get(m, m) for m in mods_escola], key='mod_escola_select', index=0)
            mod_escola = LABEL_MODALIDADE.get(mod_escola_label, mod_escola_label)

        df_esc_base = df_escolas if mod_escola == TOTAL_LABEL else df_escolas[df_escolas['Modalidade'] == mod_escola]

        # Seletor de campus (escolas)
        campi_escola = sorted([c for c in df_esc_base['Campus'].unique() if c and c != 'Todas as unidades'])
        with col_esc[1]:
            campus_escola_label = st.selectbox('Campus (escolas):', [TOTAL_LABEL] + campi_escola, key='campus_escola_select', index=0)

        if campus_escola_label != TOTAL_LABEL:
            df_esc_base = df_esc_base[df_esc_base['Campus'] == campus_escola_label]

        # Última coleta
        ultima_esc = df_esc_base['Data'].max()
        df_esc_ultima = df_esc_base[df_esc_base['Data'] == ultima_esc]

        with col_esc[2]:
            st.markdown(f"### 📅 Última coleta")
            st.write(ultima_esc.strftime("%d/%m/%Y %H:%M"))

        st.markdown("---")

        # Top 30 escolas (geral quando "Total", ou do campus selecionado)
        if campus_escola_label == TOTAL_LABEL:
            df_top_base = df_esc_ultima[df_esc_ultima['Campus'] == 'Todas as unidades']
        else:
            df_top_base = df_esc_ultima
        st.subheader(f'🏆 Top 30 Escolas de Origem (total de inscrições: {fmt(int(df_top_base["Inscritos"].sum()))})')
        df_top = df_top_base.sort_values(by='Inscritos', ascending=False)

        # Gráfico de barras horizontais
        fig_escolas = px.bar(
            df_top,
            x='Inscritos', y='Escola',
            orientation='h',
            title='Top 30 Escolas por Inscrições',
            color='Inscritos',
            color_continuous_scale='Greens',
            height=800,
        )
        fig_escolas.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Segoe UI, Arial", size=14),
            title=dict(font=dict(size=18, color="#1a3d2f")),
        )
        fig_escolas.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_escolas, width='stretch', key='bar_escolas')

        # Tabela
        colunas_tabela_esc = ['Rank','Escola','Cidade','Tipo','Area','Inscritos']
        if campus_escola_label == TOTAL_LABEL and 'Campus' in df_top.columns:
            colunas_tabela_esc = ['Campus'] + colunas_tabela_esc
        st.dataframe(df_top[colunas_tabela_esc].reset_index(drop=True), width='stretch')

        # Donuts de resumo (tipo/área/cidade)
        st.markdown("---")
        st.subheader('📊 Distribuição por Tipo, Área e Cidade')
        df_resumo_filtro = df_escolas_resumo
        if not df_escolas_resumo.empty:
            if mod_escola != TOTAL_LABEL:
                df_resumo_filtro = df_escolas_resumo[df_escolas_resumo['Modalidade'] == mod_escola]
            if campus_escola_label != TOTAL_LABEL:
                df_resumo_filtro = df_resumo_filtro[df_resumo_filtro['Campus'] == campus_escola_label]
            if not df_resumo_filtro.empty:
                ultima_resumo = df_resumo_filtro['Data'].max()
                df_resumo_ultima = df_resumo_filtro[df_resumo_filtro['Data'] == ultima_resumo]

                categorias = ['tipo', 'area', 'cidade']
                donut_cols = st.columns(3)
                for i, cat in enumerate(categorias):
                    df_cat = df_resumo_ultima[df_resumo_ultima['Categoria'] == cat]
                    if df_cat.empty:
                        continue
                    with donut_cols[i]:
                        fig_donut = px.pie(
                            df_cat,
                            names='Label', values='Valor',
                            title=f'Por {cat.capitalize()}',
                            hole=0.5,
                            height=350,
                        )
                        fig_donut.update_layout(
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Segoe UI, Arial", size=13),
                            title=dict(font=dict(size=16, color="#1a3d2f")),
                            showlegend=True,
                            legend=dict(orientation="h", yanchor="bottom", y=-0.3, font=dict(size=11)),
                        )
                        st.plotly_chart(fig_donut, width='stretch', key=f'donut_{cat}')

        # Evolução por escola
        st.markdown("---")
        st.subheader('📈 Evolução das Escolas ao Longo do Tempo')
        df_evol_base = df_esc_base
        if campus_escola_label == TOTAL_LABEL:
            df_evol_base = df_esc_base[df_esc_base['Campus'] == 'Todas as unidades']
        df_evol_esc = df_evol_base.groupby(['Data', 'Escola'])['Inscritos'].sum().reset_index()
        top_escolas = df_evol_esc.groupby('Escola')['Inscritos'].sum().sort_values(ascending=False).head(10).index.tolist()
        df_evol_esc_top = df_evol_esc[df_evol_esc['Escola'].isin(top_escolas)]

        fig_evol_esc = px.line(
            df_evol_esc_top,
            x='Data', y='Inscritos', color='Escola',
            title='Evolução das 10 Escolas com mais Inscrições',
            markers=True,
            height=600,
        )
        fig_evol_esc.update_traces(mode="lines+markers", hovertemplate="%{y}")
        fig_evol_esc.update_layout(
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Segoe UI, Arial", size=14),
            title=dict(font=dict(size=18, color="#1a3d2f")),
        )
        st.plotly_chart(fig_evol_esc, width='stretch', key='evol_escolas')

st.markdown('<div class="footer-note">Desenvolvido com ❤️ por Luciano Espiridiao — luciano.espiridiao@ifmg.edu.br · 2025 · Todos os direitos reservados.</div>', unsafe_allow_html=True)