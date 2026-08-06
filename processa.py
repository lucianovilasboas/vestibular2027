import pandas as pd
import os
from datetime import datetime
import shutil
import re
from log import logger


# Função para ajustar a linha de totais
def ajustar_totais(df):

    df = df.drop(df[df['Unidade'] == 'Totais'].index)
    df = df.drop(df[df['Unidade'] == 'Todas'].index)

    # Colunas numéricas (soma) vs texto (rótulo fixo)
    colunas_texto = ['Unidade', 'Curso', 'Modalidade', 'Timestamp']
    totais = {}
    for col in df.columns:
        if col in colunas_texto:
            continue
        # Soma colunas numéricas; texto não-numérico vira 0
        try:
            totais[col] = df[col].sum()
        except TypeError:
            totais[col] = 0

    totais['Unidade'] = 'Todas'
    totais['Curso'] = 'Todos'

    # Adiciona a linha de totais como nova linha (não sobrescreve)
    df = pd.concat([df, pd.DataFrame([totais])], ignore_index=True)

    return df


def extrair_timestamp_do_arquivo(file_path, file_name):
    """
    Extrai o timestamp da coleta.
    Prioridade:
    1. Timestamp do nome do arquivo (ex: dados_INT_20260806_0744.csv)
       - Granularidade de minuto; consistente entre INT/SUB/SUP da MESMA coleta
    2. Coluna 'Timestamp' já existente no CSV (escrita pelo scraper)
    3. mtime do arquivo
    """
    # 1. Extrai do nome do arquivo: dados_INT_20260805_2346.csv
    match = re.search(r'dados_[A-Z]+_(\d{8}_\d{4})', file_name)
    if match:
        ts_str = match.group(1)
        try:
            # Converte 20260805_2346 para datetime
            dt = datetime.strptime(ts_str, "%Y%m%d_%H%M")
            return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            pass

    # 2. Tenta ler a coluna Timestamp do CSV
    try:
        df_sample = pd.read_csv(file_path, nrows=1)
        if 'Timestamp' in df_sample.columns:
            ts = df_sample['Timestamp'].iloc[0]
            # Valida se é um timestamp válido
            pd.to_datetime(ts)
            return ts
    except Exception:
        pass

    # 3. Fallback: mtime do arquivo
    mtime = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S.%f")


if __name__ == "__main__":

    # Define os caminhos das pastas
    dados_folder = "./dados"
    input_folder = "./dados/input"
    processed_folder = "./dados/processed"
    backup_folder = "./dados/backup"
    timestamp = datetime.now()
    # Gera o novo nome para o arquivo com base na data de leitura
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

    # Tenta listar todos os arquivos na pasta de entrada
    try:
        files = os.listdir(input_folder)
        if not files:
            print(f"{timestamp_str} - Nenhum arquivo encontrado na pasta input.")
            logger.warn(f"Nenhum arquivo encontrado na pasta input.")
            exit()
    except Exception as e:
        print(f"{timestamp_str} - Nenhum arquivo encontrado na pasta input.")
        logger.warn(f"Nenhum arquivo encontrado na pasta input - {e}")
        exit()

    # --- Processa arquivos de CARDS (cards_*.csv) separadamente ---
    cards_files = [f for f in files if f.startswith('cards_') and f.endswith('.csv')]
    if cards_files:
        cards_file_path = os.path.join(processed_folder, "cards.csv")
        cards_all = pd.read_csv(cards_file_path) if os.path.exists(cards_file_path) else pd.DataFrame()
        cards_dataframes = []
        if not cards_all.empty:
            cards_dataframes.append(cards_all)

        for file in cards_files:
            file_path = os.path.join(input_folder, file)
            df_cards = pd.read_csv(file_path)
            collection_ts = extrair_timestamp_do_arquivo(file_path, file)
            df_cards['Timestamp'] = collection_ts
            cards_dataframes.append(df_cards)
            shutil.move(file_path, os.path.join(backup_folder, file))

        cards_concatenado = pd.concat(cards_dataframes, ignore_index=True)
        # Remove duplicatas por segurança
        cards_concatenado = cards_concatenado.drop_duplicates(subset=['Timestamp', 'Modalidade'])
        cards_concatenado.to_csv(cards_file_path, index=False, encoding="utf-8")
        logger.info(f"Cards processados: {len(cards_concatenado)} linhas em {cards_file_path}")

    # --- Processa arquivos de dados (dados_*.csv) ---
    data_files = [f for f in files if f.startswith('dados_') and f.endswith('.csv')]

    # lendo o dataframe final
    df_all = pd.read_csv("./dados/processed/all_data.csv")
    dataframes = []
    if not df_all.empty:
        dataframes.append(df_all)

    for file in data_files:
        # Define o caminho completo do arquivo
        file_path = os.path.join(input_folder, file)

        # Lê o arquivo CSV
        df = pd.read_csv(file_path)

        # Ajusta os totais
        df = ajustar_totais(df)

        # Registra o timestamp da coleta (preserva o timestamp original)
        collection_ts = extrair_timestamp_do_arquivo(file_path, file)
        df['Timestamp'] = collection_ts
        df["Modalidade"] = file.split("_")[1]

        dataframes.append(df)

        shutil.move(file_path, os.path.join(backup_folder, file))

    csv_file_path = os.path.join(processed_folder, "all_data")
    df_all = pd.concat(dataframes)
    df_all.to_csv(f"{csv_file_path}.csv", index=False, encoding="utf-8")

    print(f"{timestamp_str} - Todos os arquivos processados e movidos com sucesso!")
    logger.info(f"Todos os arquivos processados e movidos com sucesso!")