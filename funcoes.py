import pandas as pd
import os
from datetime import datetime
import pytz
import streamlit as st

def process_file_for_superior(file_path):
    """
    Function to process files for Graduação (Superior).
    Renames 'Tipo de Vaga' to 'Forma de Ingresso' for Graduação level.
    """
    df = pd.read_excel(file_path)
    
    # Splitting the "Cargo" column into 'Curso', 'Modalidade', 'Campus', 'Turno', 'Tipo de Vaga'
    cargo_split = df['Cargo'].str.split(r' - ', expand=True)
    
    if cargo_split.shape[1] == 3:
        df['Curso'] = cargo_split[0]
        df['Campus'] = cargo_split[1]
        df['Turno'] = cargo_split[2]
        df['Modalidade'] = 'Superior'
        df['FormaIngresso'] = df['Tipo de Vaga']
    else: 
        df['Curso'] = cargo_split[0]
        df['Modalidade'] = cargo_split[1]
        df['Campus'] = cargo_split[2]
        df['Turno'] = cargo_split[3]
        df['FormaIngresso'] = cargo_split[4]
    

    # df.rename({"Isenções deferidas": 'Deferidas', "Inscrições homologadas": 'Homologadas'}, axis=1, inplace=True) 
    df['Campus'] = df['Campus'].apply(lambda r: r.replace("Campus","").replace("campus","").strip().upper() )
    df['Curso'] = df['Curso'].apply(lambda r: r
                                    .replace("Tecnologia em","").strip().upper())
    
    lista_licenciatura = ["PEDAGOGIA","MATEMÁTICA","FÍSICA","EDUCAÇÃO FÍSICA","CIÊNCIAS BIOLÓGICAS","GEOGRAFIA"]
    lista_tecnologico =  ["LOGÍSTICA","ANÁLISE E DESENVOLVIMENTO DE SISTEMAS","CONSERVAÇÃO E RESTAURO","DESIGN DE INTERIORES","GESTÃO AMBIENTAL","GESTÃO DA QUALIDADE","PROCESSOS GERENCIAIS"]

    def tipo_curso(x):
        if x in lista_licenciatura: return "Licenciatura"
        if x in lista_tecnologico: return "Tecnológico"
        return "Bacharelado"    

    df["Modalidade"] =  df["Curso"].apply(tipo_curso)
    # Primeira letra maiúscula 
    df["Nivel"] = df["Nivel"].apply(lambda x: x.capitalize())

    # Selecting and reordering the desired columns
    final_df = df[['Curso', 'Modalidade', 'Campus', 'Turno', 'Nivel', 'Inscritos', 'Pagos', 'Isenções deferidas', 'Inscrições homologadas', 'FormaIngresso']]
    
    return final_df


def process_file_for_integrado(file_path):
    """
    Function to process files for Técnico level.
    Keeps the column name as 'Tipo de Vaga'.
    """
    df = pd.read_excel(file_path)
    
    # Splitting the "Cargo" column into 'Curso', 'Modalidade', 'Campus', 'Turno', 'Tipo de Vaga'
    cargo_split = df['Cargo'].str.split(' - ', expand=True)
    
    df['Curso'] = cargo_split[0] 
    df['Campus'] = cargo_split[1]
    df['Turno'] = cargo_split[2]
    df['Modalidade'] = df['Tipo de Vaga'] if 'Tipo de Vaga' in df.columns else 'Integrado'
    df['FormaIngresso'] = 'Processo Seletivo'
        
    
    # df.rename({"Isenções deferidas": 'Deferidas', "Inscrições homologadas": 'Homologadas'}, axis=1, inplace=True) 
    df['Campus'] = df['Campus'].apply(lambda r: r.replace("Campus","").replace("campus","").strip().upper() )
    df['Curso'] = df['Curso'].apply(lambda r: r
                                    .replace("Técnico Integrado em","")
                                    .replace("Técnico Integrado","")
                                    .replace("Técnico Subsequente em","").strip().upper())
    df['Modalidade'] = df['Modalidade'].apply(lambda r: str(r).replace("Curso Técnico","").strip())

    # Primeira letra maiúscula 
    df["Nivel"] = df["Nivel"].apply(lambda x: x.capitalize())

    # Selecting and reordering the desired columns
    final_df = df[['Curso', 'Modalidade', 'Campus', 'Turno', 'Nivel', 'Inscritos', 'Pagos', 
                   'Isenções deferidas', 'Inscrições homologadas', 'FormaIngresso']]
    
    return final_df


def process_file_for_subsequente(file_path):
    """
    Function to process files for Subsequente level.
    Keeps the column name as 'Tipo de Vaga'.
    """
    df = pd.read_excel(file_path)
    
    # Splitting the "Cargo" column into 'Curso', 'Modalidade', 'Campus', 'Turno', 'Tipo de Vaga'
    cargo_split = df['Cargo'].str.split(' - ', expand=True)
    
    df['Curso'] = cargo_split[0]
    df['Campus'] = cargo_split[1]
    df['Turno'] = cargo_split[2]
    df['Modalidade'] = df['Tipo de Vaga'] if 'Tipo de Vaga' in df.columns else 'Subsequente'
    df['FormaIngresso'] = 'Processo Seletivo'
        
    
    # df.rename({"Isenções deferidas": 'Deferidas', "Inscrições homologadas": 'Homologadas'}, axis=1, inplace=True) 
    df['Campus'] = df['Campus'].apply(lambda r: r.replace("Campus","").replace("campus","").strip().upper() )
    df['Curso'] = df['Curso'].apply(lambda r: r
                                    .replace("Técnico Subsequente","")
                                    .replace("Técnico Subsequente em","").strip().upper())
    
    # Primeira letra maiúscula 
    df["Nivel"] = df["Nivel"].apply(lambda x: x.capitalize())

    # Selecting and reordering the desired columns
    final_df = df[['Curso', 'Modalidade', 'Campus', 'Turno', 'Nivel', 'Inscritos', 'Pagos', 
                   'Isenções deferidas', 'Inscrições homologadas', 'FormaIngresso']]
    
    return final_df


def diff(df1, df2, tipo="Curso"):
    
    df11 = df1.groupby(tipo)[["Inscritos","Pagos", "Isenções deferidas","Inscrições homologadas"]].sum().reset_index().sort_values(by='Inscritos', ascending=False)
    df11.set_index(tipo, inplace=True)

    df22 = df2.groupby(tipo)[["Inscritos","Pagos", "Isenções deferidas","Inscrições homologadas"]].sum().reset_index().sort_values(by='Inscritos', ascending=False)
    df22.set_index(tipo, inplace=True)

    dfdiff = df22 - df11
    return dfdiff.reset_index().sort_values("Inscritos")


def get_last_modified_file(path): 

    # Obtém o tempo de modificação em segundos desde a época
    timestamp = os.path.getmtime(path)

    # Converte o timestamp para uma data legível
    data_modificacao = datetime.fromtimestamp(timestamp) 

    # Define o fuso horário para "America/Sao_Paulo"
    fuso_horario = pytz.timezone("America/Sao_Paulo")

    data_modificacao = data_modificacao.astimezone(fuso_horario)

    return data_modificacao.strftime("%d/%m/%Y %H:%M:%S")


# Função para amostrar por intervalo regular com dois valores por dia
def amostrar_dois_por_dia(df):

    # Função auxiliar para amostrar dois valores por dia, mantendo o primeiro e o último Timestamp
    def amostrar_grupo(grupo):
        # Adiciona uma coluna 'Data' extraída de 'Timestamp' para agrupar por dia
        grupo['Data'] = grupo['Timestamp'].dt.date
        # Função para garantir dois registros por dia (primeiro e último do dia)
        def amostrar_dia(dia_grupo):
            if len(dia_grupo) > 2:
                return pd.concat( [dia_grupo.iloc[[0]], dia_grupo.iloc[[-1]]] )
            else:
                return dia_grupo
        
        # Aplica a função de amostragem a cada dia
        return grupo.groupby('Data', group_keys=False).apply(amostrar_dia).drop(columns='Data')

    # Agrupa por 'Unidade', 'Curso','Modalidade','FormaIngresso' e aplica a amostragem de dois valores por dia
    amostrado = df.groupby(['Unidade', 'Curso'], group_keys=False).apply(amostrar_grupo).reset_index(drop=True)
    
    return amostrado.sort_values(by='Timestamp')



def _normalizar(texto):
    """Normaliza texto para comparação: maiúsculas, sem acentos, espaços simples."""
    if not isinstance(texto, str):
        return ""
    import unicodedata
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = texto.upper().strip().replace('  ', ' ')
    # Correções de grafia conhecidas (site vs edital)
    correcoes = {
        'INTELIGENCA ARTIFICIAL': 'INTELIGENCIA ARTIFICIAL',
        'LETRAS (PORTUGUES INGLES)': 'LETRAS (PORTUGUES/INGLES)',
    }
    return correcoes.get(texto, texto)


@st.cache_data(ttl=3600)  # Referência estática; cache longo
def carregar_vagas():
    """Carrega a referência de vagas por curso (dados dos editais IFMG 2027)."""
    vagas_file = "dados/vagas_referencia.csv"
    if not os.path.exists(vagas_file):
        return pd.DataFrame()
    df = pd.read_csv(vagas_file)
    # Chave normalizada: campus|curso|modalidade|forma
    df['CampusNorm'] = df['Campus'].apply(_normalizar)
    df['CursoNorm'] = df['Curso'].apply(_normalizar)
    df['Chave'] = (df['CampusNorm'] + '|' + df['CursoNorm'] + '|' + df['Modalidade'] + '|' + df['FormaSelecao'].fillna('').str.upper())
    return df


def aplicar_vagas(df_all):
    """Aplica as vagas do edital ao DataFrame de inscrições (merge pela chave)."""
    df_vagas = carregar_vagas()
    if df_vagas.empty:
        df_all['Vagas'] = 0
        df_all['Inscr./Vagas'] = 0
        return df_all

    # Cria chave normalizada no df de inscrições
    df_all['UnidadeNorm'] = df_all['Unidade'].apply(_normalizar)
    df_all['CursoNorm'] = df_all['Curso'].apply(_normalizar)

    # Para SUP, o curso no site é "Nome (FORMA)" - extrai a forma
    def extrair_forma_sup(curso):
        curso = str(curso)
        if ' (ENEM)' in curso:
            return 'ENEM'
        if ' (Histórico e Redação)' in curso:
            return 'HISTÓRICO E REDAÇÃO'
        return ''

    def limpar_curso_sup(curso):
        curso = str(curso)
        curso = curso.replace(' (ENEM)', '').replace(' (Histórico e Redação)', '')
        return curso

    df_all['Forma'] = ''
    mask_sup = df_all['Modalidade'] == 'SUP'
    df_all.loc[mask_sup, 'Forma'] = df_all.loc[mask_sup, 'Curso'].apply(extrair_forma_sup)
    df_all['CursoBase'] = df_all['Curso'].apply(limpar_curso_sup)
    df_all['CursoNorm'] = df_all['CursoBase'].apply(_normalizar)

    # Monta chave no df de inscrições
    df_all['Chave'] = df_all['UnidadeNorm'] + '|' + df_all['CursoNorm'] + '|' + df_all['Modalidade'] + '|' + df_all['Forma']

    # Merge das vagas
    df_vagas_map = df_vagas[['Chave', 'TotalVagas']].drop_duplicates(subset='Chave')
    df_all = df_all.merge(df_vagas_map, on='Chave', how='left')

    # Preenche vagas: se não encontrou, 0
    df_all['Vagas'] = df_all['TotalVagas'].fillna(0).astype(int)
    df_all.drop(columns=['TotalVagas'], inplace=True)

    # Inscr./Vagas (protegido contra divisão por zero)
    df_all['Inscr./Vagas'] = df_all.apply(
        lambda r: round(r['Inscritos'] / r['Vagas'], 2) if r['Vagas'] > 0 else 0, axis=1
    )

    # Limpa colunas auxiliares
    df_all.drop(columns=['UnidadeNorm', 'CursoNorm', 'CursoBase', 'Forma', 'Chave'], inplace=True)

    return df_all


@st.cache_data(ttl=60) # Cache por 60 segundos para atualização mais rápida
def load_data():
    df_all = pd.read_csv("dados/processed/all_data.csv")
    
    df_all['Data'] = pd.to_datetime(df_all['Timestamp'])
    df_all.drop(columns=['Timestamp'], inplace=True)
    
    # Remove linhas de total ('Todos' no Curso)
    df_all = df_all[df_all['Curso'] != 'Todos'].copy()
    
    # Remove duplicatas por segurança (mesma coleta + unidade + curso + modalidade)
    df_all = df_all.drop_duplicates(subset=['Data', 'Unidade', 'Curso', 'Modalidade']).copy()
    
    # Aplica as vagas do edital
    df_all = aplicar_vagas(df_all)
    
    return df_all


@st.cache_data(ttl=60) # Cache por 60 segundos para atualização mais rápida
def load_cards():
    """Carrega os cards do painel de controle (Inscrições, Pagas, Isenção, etc.)."""
    cards_file = "dados/processed/cards.csv"
    if not os.path.exists(cards_file):
        return pd.DataFrame()
    
    df_cards = pd.read_csv(cards_file)
    df_cards['Data'] = pd.to_datetime(df_cards['Timestamp'])
    df_cards.drop(columns=['Timestamp'], inplace=True)
    
    # Remove duplicatas por segurança
    df_cards = df_cards.drop_duplicates(subset=['Data', 'Modalidade']).copy()
    
    return df_cards
