#!/usr/bin/env python3
"""
Scraper v3 Standalone - Usa endpoint AJAX /inscricao/data diretamente.
Login UMA VEZ, depois troca apenas o processo via session.

Conta apenas inscrições de OPÇÃO 1 (inscrições válidas).
Também captura os cards do /paineldecontrole (Inscrições, Pagas, Isenção, etc.).
"""

import requests
import pandas as pd
import os
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings()

load_dotenv()  # carrega credenciais do arquivo .env (uso local)

BASE_URL = "https://fundacao.cefetmg.br"
LOGIN_URL = f"{BASE_URL}/login"
USERNAME = os.getenv("FCM_USERNAME")
PASSWORD = os.getenv("FCM_PASSWORD")

if not USERNAME or not PASSWORD:
    logger.error("Credenciais não encontradas. Verifique o arquivo .env (FCM_USERNAME e FCM_PASSWORD).")
    raise SystemExit("Faltam credenciais no arquivo .env")

PROCESSOS = {
    "INT": "IFMGTI271",
    "SUB": "IFMGTS271",
    "SUP": "IFMGGR271",
}

DOWNLOAD_DIR = "./dados/input"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(service=Service(), options=options)
    driver.set_page_load_timeout(60)
    return driver


def do_login(driver):
    """Faz login uma única vez."""
    logger.info("Fazendo login...")
    driver.get(LOGIN_URL)
    time.sleep(3)

    wait = WebDriverWait(driver, 30)
    username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    logger.info("Campo username encontrado")
    username_input.send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.bg-blue.btn-block"))).click()
    wait.until(EC.url_contains("paineldecontrole"))
    logger.info("Login realizado, painel carregado")
    time.sleep(2)

    # Transfere cookies para requests.Session
    session = requests.Session()
    session.verify = False
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    return session


def select_processo(driver, session, modalidade):
    """Seleciona o processo no Selenium e atualiza cookies na session."""
    logger.info(f"Selecionando processo {modalidade} ({PROCESSOS[modalidade]})...")
    driver.get(f"{BASE_URL}/processoseletivo/{PROCESSOS[modalidade]}/session")
    time.sleep(2)

    # Atualiza cookies na session (pode ter mudado)
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    return session


def fetch_all_inscricoes(session, modalidade):
    """Busca TODAS as inscrições via endpoint AJAX."""
    logger.info(f"Buscando dados {modalidade} via AJAX...")

    url = f"{BASE_URL}/inscricao/data"
    params = {
        'sEcho': '3',
        'iColumns': '7',
        'sColumns': '',
        'iDisplayStart': '0',
        'iDisplayLength': '99999',
        'mDataProp_0': '0', 'mDataProp_1': '1', 'mDataProp_2': '2',
        'mDataProp_3': '3', 'mDataProp_4': '4', 'mDataProp_5': '5', 'mDataProp_6': '6',
        'sSearch': '', 'bRegex': 'false',
        'iSortCol_0': '0', 'sSortDir_0': 'asc',
        'iSortCol_1': '5', 'sSortDir_1': 'asc',
        'iSortingCols': '2',
        'bSortable_0': 'true', 'bSortable_1': 'true', 'bSortable_2': 'true',
        'bSortable_3': 'true', 'bSortable_4': 'true', 'bSortable_5': 'true', 'bSortable_6': 'true',
    }
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': f'{BASE_URL}/inscricao',
    }

    resp = session.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    total = data.get('iTotalRecords', 0)
    rows = data.get('aaData', [])
    logger.info(f"  Recebidos {len(rows)} de {total} registros")

    df = pd.DataFrame(rows, columns=['Inscricao', 'CPF', 'Nome', 'Unidade', 'Curso', 'Opcao', 'Acoes'])
    df['Modalidade'] = modalidade
    return df


def fetch_painel_cards(session, modalidade):
    """Busca os cards do /paineldecontrole para a modalidade."""
    logger.info(f"Buscando cards {modalidade} via /paineldecontrole...")

    resp = session.get(f"{BASE_URL}/paineldecontrole", timeout=30)
    resp.raise_for_status()
    html = resp.text

    # Extrai os cards (número + label)
    boxes = re.findall(
        r'<div class="small-box (?:bg-\w+)">.*?<h3>\s*([\d.]+)\s*</h3>.*?<p>\s*([^<]+)\s*</p>',
        html, re.DOTALL
    )

    cards = {}
    for num, label in boxes:
        label_clean = label.strip()
        try:
            value = int(num.replace('.', ''))
        except ValueError:
            value = num.strip()
        cards[label_clean] = value

    logger.info(f"  Cards {modalidade}: {cards}")
    return cards


def save_cards(cards_por_modalidade):
    """Salva o arquivo de cards dados/input/cards_<timestamp>.csv."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    rows = []
    for modalidade, cards in cards_por_modalidade.items():
        row = {
            'Modalidade': modalidade,
            'Inscricoes': cards.get('Inscrições', 0),
            'InscricoesPagas': cards.get('Inscrições Pagas', 0),
            'Isencao': cards.get('Solic. de Isenção', 0),
            'IsencaoDeferidas': cards.get('Solic. De Isenção Deferidas', 0),
            'CondicoesEspeciais': cards.get('Solic. de Condições Especiais', 0),
            'CondicoesDeferidas': cards.get('Solic. de Condições Especiais Deferidas', 0),
        }
        rows.append(row)

    df_cards = pd.DataFrame(rows)
    filepath = os.path.join(DOWNLOAD_DIR, f"cards_{timestamp}.csv")
    df_cards.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Cards salvos: {filepath}")
    return filepath


def aggregate_and_save(df, modalidade):
    """Agrega por Unidade+Curso considerando APENAS a opção 1 e salva CSV."""
    # Filtra apenas opção 1 (inscrições válidas)
    df_op1 = df[df['Opcao'] == 1].copy()

    agg = df_op1.groupby(['Unidade', 'Curso']).agg(Inscritos=('Inscricao', 'count')).reset_index()
    agg['Modalidade'] = modalidade
    agg['Vagas'] = 0
    agg['Campus'] = agg['Unidade'].str.replace('Campus', '').str.replace('campus', '').str.strip().str.upper()

    final = agg[['Campus', 'Curso', 'Vagas', 'Inscritos']].copy()
    final.columns = ['Unidade', 'Curso', 'Vagas', 'Inscritos']
    final['Inscr./Vagas'] = 0
    final['Timestamp'] = datetime.now()
    final['Modalidade'] = modalidade

    cols = ['Unidade', 'Curso', 'Vagas', 'Inscritos', 'Inscr./Vagas', 'Timestamp', 'Modalidade']
    final = final[cols]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filepath = os.path.join(DOWNLOAD_DIR, f"dados_{modalidade}_{timestamp}.csv")
    final.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Salvo: {filepath} ({len(final)} cursos, {final['Inscritos'].sum()} inscrições opção 1)")
    return filepath


def main():
    logger.info("=== Scraper v3 - Login Único + AJAX (opção 1 + cards) ===")
    driver = create_driver()
    cards_por_modalidade = {}
    try:
        # Login UMA VEZ
        session = do_login(driver)

        # Para cada modalidade: seleciona processo + busca AJAX + cards
        for modalidade in PROCESSOS:
            logger.info(f"\n--- {modalidade} ---")
            session = select_processo(driver, session, modalidade)
            df = fetch_all_inscricoes(session, modalidade)
            if not df.empty:
                aggregate_and_save(df, modalidade)
            else:
                logger.warning(f"Sem dados para {modalidade}")

            # Captura os cards do painel de controle
            try:
                cards = fetch_painel_cards(session, modalidade)
                cards_por_modalidade[modalidade] = cards
            except Exception as e:
                logger.error(f"Erro ao buscar cards para {modalidade}: {e}")

        # Salva os cards após todas as modalidades
        if cards_por_modalidade:
            save_cards(cards_por_modalidade)

    finally:
        driver.quit()
        logger.info("=== Fim ===")


if __name__ == "__main__":
    main()