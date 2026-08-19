import pandas as pd
import os
from datetime import datetime
import shutil
import re
from log import logger
from validacao import (
    validar_cursos,
    validar_escolas,
    validar_escolas_resumo,
    validar_cards,
    validar_salto_total,
    validar_completude_coleta,
    mover_para_quarentena,
)


def _validar_e_mover(file_path, validador, contexto=""):
    """Valida o arquivo; se tiver erros graves, move para quarentena e retorna None."""
    df = pd.read_csv(file_path)
    resultado = validador(df)
    resultado.log(contexto or os.path.basename(file_path))

    if not resultado.valido:
        motivo = "; ".join(resultado.erros[:3])
        mover_para_quarentena(file_path, motivo)
        return None
    return df


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


def extrair_modalidade_do_arquivo(file_name):
    """Extrai a modalidade (INT/SUB/SUP) do nome do arquivo."""
    match = re.search(r'(?:dados|escolas|escolas_resumo)_([A-Z]+)_\d{8}_\d{4}', file_name)
    if match:
        return match.group(1)
    return file_name.split('_')[1] if len(file_name.split('_')) > 1 else ''


def extrair_timestamp_do_arquivo(file_path, file_name, prefixo='dados'):
    """
    Extrai o timestamp da coleta.
    Prioridade:
    1. Timestamp do nome do arquivo (ex: dados_INT_20260806_0744.csv)
       - Granularidade de minuto; consistente entre INT/SUB/SUP da MESMA coleta
    2. Coluna 'Timestamp' já existente no CSV (escrita pelo scraper)
    3. mtime do arquivo
    """
    # 1. Extrai do nome do arquivo: dados_INT_20260805_2346.csv
    match = re.search(rf'{prefixo}_[A-Z]+_(\d{{8}}_\d{{4}})', file_name)
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


def processar_cards(files, input_folder, processed_folder, backup_folder):
    cards_files = [f for f in files if f.startswith('cards_') and f.endswith('.csv')]
    if not cards_files:
        return

    cards_file_path = os.path.join(processed_folder, "cards.csv")
    cards_all = pd.read_csv(cards_file_path) if os.path.exists(cards_file_path) else pd.DataFrame()
    cards_dataframes = []
    if not cards_all.empty:
        cards_dataframes.append(cards_all)

    for file in cards_files:
        file_path = os.path.join(input_folder, file)
        df_cards = _validar_e_mover(file_path, validar_cards, contexto=f"cards/{file}")
        if df_cards is None:
            continue
        collection_ts = extrair_timestamp_do_arquivo(file_path, file)
        df_cards['Timestamp'] = collection_ts
        cards_dataframes.append(df_cards)
        shutil.move(file_path, os.path.join(backup_folder, file))

    cards_concatenado = pd.concat(cards_dataframes, ignore_index=True)
    cards_concatenado = cards_concatenado.drop_duplicates(subset=['Timestamp', 'Modalidade'])
    cards_concatenado.to_csv(cards_file_path, index=False, encoding="utf-8")
    logger.info(f"Cards processados: {len(cards_concatenado)} linhas em {cards_file_path}")


def processar_dados(files, input_folder, processed_folder, backup_folder):
    data_files = [f for f in files if f.startswith('dados_') and f.endswith('.csv')]
    if not data_files:
        return

    all_data_path = os.path.join(processed_folder, "all_data.csv")
    df_all = pd.read_csv(all_data_path) if os.path.exists(all_data_path) else pd.DataFrame()
    dataframes = []
    if not df_all.empty:
        dataframes.append(df_all)

    for file in data_files:
        file_path = os.path.join(input_folder, file)

        # Valida integridade do arquivo (quarentena se inválido)
        df = _validar_e_mover(file_path, validar_cursos, contexto=f"dados/{file}")
        if df is None:
            continue

        # Ajusta os totais
        df = ajustar_totais(df)

        # Registra o timestamp da coleta (preserva o timestamp original)
        collection_ts = extrair_timestamp_do_arquivo(file_path, file, prefixo='dados')
        df['Timestamp'] = collection_ts
        modalidade = extrair_modalidade_do_arquivo(file)
        df["Modalidade"] = modalidade

        # Checa salto vs última coleta histórica (aviso)
        if not df_all.empty:
            salto = validar_salto_total(df_all, df['Inscritos'].sum(), modalidade)
            salto.log(contexto=f"salto/{file}")

        dataframes.append(df)

        shutil.move(file_path, os.path.join(backup_folder, file))

    # Valida a completude das coletas novas (todas as modalidades por timestamp)
    # dataframes[0] é o histórico; o restante são as coletas novas
    coletas_novas = pd.concat(dataframes[1:], ignore_index=True) if len(dataframes) > 1 else pd.DataFrame()
    if not coletas_novas.empty:
        completude = validar_completude_coleta(coletas_novas)
        # Coletas incompletas são removidas do histórico (evita distorção nos gráficos)
        if completude.erros:
            completude.log(contexto="completude")
            timestamps_invalidos = set()
            for msg in completude.erros:
                # msg no formato: "coleta <ts> incompleta: ..." (ts pode conter espaços)
                m = re.search(r'coleta (.+?) incompleta', msg)
                if m:
                    timestamps_invalidos.add(m.group(1))
            coletas_novas = coletas_novas[~coletas_novas['Timestamp'].isin(list(timestamps_invalidos))]
            logger.error(
                f"[validacao] coletas incompletas removidas do histórico: {sorted(timestamps_invalidos)}"
            )
        else:
            completude.log(contexto="completude")

    csv_file_path = os.path.join(processed_folder, "all_data")
    df_all = pd.concat([dataframes[0], coletas_novas], ignore_index=True) if not coletas_novas.empty \
        else dataframes[0].copy()
    df_all.to_csv(f"{csv_file_path}.csv", index=False, encoding="utf-8")
    logger.info(f"Dados processados: {len(df_all)} linhas em {csv_file_path}.csv")


def processar_escolas(files, input_folder, processed_folder, backup_folder):
    """Concatena Top 30 escolas por modalidade em escolas_all.csv (histórico)."""
    escola_files = [f for f in files if f.startswith('escolas_') and f.endswith('.csv')
                    and not f.startswith('escolas_resumo_')]
    if not escola_files:
        return

    out_path = os.path.join(processed_folder, "escolas_all.csv")
    out_all = pd.read_csv(out_path) if os.path.exists(out_path) else pd.DataFrame()
    frames = []
    if not out_all.empty:
        frames.append(out_all)

    for file in escola_files:
        file_path = os.path.join(input_folder, file)
        df = _validar_e_mover(file_path, validar_escolas, contexto=f"escolas/{file}")
        if df is None:
            continue
        collection_ts = extrair_timestamp_do_arquivo(file_path, file, prefixo='escolas')
        df['Timestamp'] = collection_ts
        df["Modalidade"] = extrair_modalidade_do_arquivo(file)
        frames.append(df)
        shutil.move(file_path, os.path.join(backup_folder, file))

    concat = pd.concat(frames, ignore_index=True)
    concat = concat.drop_duplicates(subset=['Timestamp', 'Modalidade', 'Campus', 'Escola'])
    concat.to_csv(out_path, index=False, encoding="utf-8")
    logger.info(f"Escolas processadas: {len(concat)} linhas em {out_path}")


def processar_escolas_resumo(files, input_folder, processed_folder, backup_folder):
    """Concatena resumos (tipo/área/cidade) em escolas_resumo_all.csv (histórico)."""
    resumo_files = [f for f in files if f.startswith('escolas_resumo_') and f.endswith('.csv')]
    if not resumo_files:
        return

    out_path = os.path.join(processed_folder, "escolas_resumo_all.csv")
    out_all = pd.read_csv(out_path) if os.path.exists(out_path) else pd.DataFrame()
    frames = []
    if not out_all.empty:
        frames.append(out_all)

    for file in resumo_files:
        file_path = os.path.join(input_folder, file)
        df = _validar_e_mover(file_path, validar_escolas_resumo, contexto=f"escolas_resumo/{file}")
        if df is None:
            continue
        collection_ts = extrair_timestamp_do_arquivo(file_path, file, prefixo='escolas_resumo')
        df['Timestamp'] = collection_ts
        df["Modalidade"] = extrair_modalidade_do_arquivo(file)
        frames.append(df)
        shutil.move(file_path, os.path.join(backup_folder, file))

    concat = pd.concat(frames, ignore_index=True)
    concat = concat.drop_duplicates(subset=['Timestamp', 'Modalidade', 'Campus', 'Categoria', 'Label'])
    concat.to_csv(out_path, index=False, encoding="utf-8")
    logger.info(f"Resumo escolas processado: {len(concat)} linhas em {out_path}")


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

    processar_cards(files, input_folder, processed_folder, backup_folder)
    processar_dados(files, input_folder, processed_folder, backup_folder)
    processar_escolas(files, input_folder, processed_folder, backup_folder)
    processar_escolas_resumo(files, input_folder, processed_folder, backup_folder)

    print(f"{timestamp_str} - Todos os arquivos processados e movidos com sucesso!")
    logger.info(f"Todos os arquivos processados e movidos com sucesso!")