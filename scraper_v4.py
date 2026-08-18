#!/usr/bin/env python3
"""
Scraper v4 - Novo layout FCM (2027/1)
- Login normal (username/password) via /login
- Para cada modalidade (INT/SUB/SUP):
    * Troca o processo ativo via /processoseletivo/{CODIGO}/session
    * Painel de Controle (/paineldecontrole): cards KPI (Inscrições, Pagas, Isenção...)
    * Painel Inscrições por Curso (/painelinscricoescursos): array JS 'dadosTabelaInscricoes'
        com vagas, inscritos e homologados por opção + reservas de vagas (cotas LB_*/LI_*/AC)
    * Painel Inscrições por Escola (/painelinscricoesescolas): Top 30 escolas + resumos
        por tipo, área e cidade (donuts Morris)
- Salva CSVs em dados/input/: dados_{MOD}_{ts}.csv, escolas_{MOD}_{ts}.csv,
  escolas_resumo_{MOD}_{ts}.csv e cards_{ts}.csv
"""

import requests
import pandas as pd
import os
import re
import time
from datetime import datetime
from bs4 import BeautifulSoup
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

COTAS = ["LB_PPI", "LB_Q", "LB_PCD", "LB_EP", "LI_PPI", "LI_Q", "LI_PCD", "LI_EP", "AC"]

# Códigos das unidades usados no painel de escolas (/painelinscricoesescolas/{CODIGO})
# A chave "TOD" representa "todas as unidades" (página sem código)
UNIDADES_ESCOLAS = {
    "TOD": "Todas as unidades",
    "ARC": "Arcos",
    "BAM": "Bambuí",
    "BET": "Betim",
    "CON": "Congonhas",
    "LAF": "Conselheiro Lafaiete",
    "FOR": "Formiga",
    "GVA": "Governador Valadares",
    "IBI": "Ibirité",
    "IPA": "Ipatinga",
    "ITA": "Itabirito",
    "OBR": "Ouro Branco",
    "OPR": "Ouro Preto",
    "PIU": "Piumhi",
    "PNV": "Ponte Nova",
    "RNV": "Ribeirão das Neves",
    "SAB": "Sabará",
    "SLZ": "Santa Luzia",
    "SJE": "São João Evangelista",
}

# Correções de acentos perdidos pelo site (serve HTML em latin-1 com "?" no lugar de acentos)
CORRECOES_ACENTO = {
    "P?blica": "Pública",
    "P?blico": "Público",
    "P?blicos": "Públicos",
    "N?O": "NÃO",
    "N?o": "Não",
    "N?": "N?",
    "PA?SES": "PAÍSES",
    "PA?S": "PAÍS",
    "A?O": "ÃO",
    "T?C": "TÉC",
}


def normalizar_texto(s):
    """Colapsa espaços e tenta corrigir acentos perdidos (encoding do site)."""
    s = re.sub(r'\s+', ' ', str(s)).strip()
    for k, v in CORRECOES_ACENTO.items():
        s = s.replace(k, v)
    return s


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
    """Faz login uma única vez no painel."""
    logger.info("Fazendo login...")
    driver.get(LOGIN_URL)
    time.sleep(3)

    wait = WebDriverWait(driver, 30)
    username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    username_input.send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.bg-blue.btn-block"))).click()
    wait.until(EC.url_contains("paineldecontrole"))
    logger.info("Login realizado, painel carregado")
    time.sleep(2)

    session = requests.Session()
    session.verify = False
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    return session


def select_processo(driver, session, modalidade):
    """Seleciona o processo (modalidade) e mantém cookies na session."""
    logger.info(f"Selecionando processo {modalidade} ({PROCESSOS[modalidade]})...")
    driver.get(f"{BASE_URL}/processoseletivo/{PROCESSOS[modalidade]}/session")
    time.sleep(3)

    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    return session


def fetch_painel_cursos(driver):
    """Extrai o array 'dadosTabelaInscricoes' do painel Inscrições por Curso."""
    logger.info("Acessando Painel de Inscrições por Curso...")
    driver.get(f"{BASE_URL}/painelinscricoescursos")
    time.sleep(3)

    dados = driver.execute_script("return typeof dadosTabelaInscricoes !== 'undefined' ? dadosTabelaInscricoes : null;")
    if not dados:
        logger.warning("Array dadosTabelaInscricoes não encontrado na página.")
        return None

    rows = []
    for c in dados:
        op1 = c.get('opcoes', {}).get('1') or {}
        row = {
            'Unidade': normalizar_texto(c.get('unidade', '')),
            'Curso': normalizar_texto(c.get('curso', '')),
            'Vagas': int(c.get('vagas', 0) or 0),
            'Inscritos': int(op1.get('inscritos', 0) or 0),
            'Homologados': int(op1.get('validos', 0) or 0),
        }
        for cota in COTAS:
            row[cota] = int(op1.get(cota, 0) or 0)
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return None

    df['Inscr./Vagas'] = df.apply(
        lambda r: round(r['Inscritos'] / r['Vagas'], 2) if r['Vagas'] > 0 else 0, axis=1
    )
    df['Homolog./Vagas'] = df.apply(
        lambda r: round(r['Homologados'] / r['Vagas'], 2) if r['Vagas'] > 0 else 0, axis=1
    )

    logger.info(f"  Painel de Cursos: {len(df)} linhas, {df['Inscritos'].sum()} inscritos (opção 1)")
    return df


def parse_painel_escolas_html(html):
    """Extrai Top 30 (tabela) e donuts (tipo/área/cidade) do HTML server-side."""
    soup = BeautifulSoup(html, "html.parser")

    # --- Tabela Top 30 escolas ---
    escolas = []
    for tr in soup.select("table tbody tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
        if len(cells) >= 6:
            escolas.append({
                'Rank': int(cells[0]) if cells[0].isdigit() else None,
                'Escola': normalizar_texto(cells[1]),
                'Cidade': normalizar_texto(cells[2]),
                'Tipo': normalizar_texto(cells[3]),
                'Area': normalizar_texto(cells[4]),
                'Inscritos': int(re.sub(r'\D', '', cells[5]) or 0),
            })

    # --- Donuts (tipo / área / cidade) ---
    resumo = {'tipo': [], 'area': [], 'cidade': []}
    for script in soup.find_all("script"):
        text = script.string or ""
        if 'Morris.Donut' not in text:
            continue
        blocos = re.findall(r"Morris\.Donut\(\{(.*?)\}\s*\)", text, re.DOTALL)
        for bloco in blocos:
            elem_match = re.search(r"element:\s*'(grafico-inscricoes-[^']+)'", bloco)
            if not elem_match:
                continue
            qual = 'cidade' if 'cidade' in elem_match.group(1) else ('area' if 'area' in elem_match.group(1) else 'tipo')
            pares = re.findall(r'label:\s*"([^"]+)",\s*\n?\s*value:\s*(\d+)', bloco)
            for label, valor in pares:
                resumo[qual].append({'Label': normalizar_texto(label), 'Valor': int(valor)})

    return escolas, resumo


def fetch_painel_escolas(session, unidade_codigo="TOD"):
    """Extrai Top 30 escolas e donuts para uma unidade via requests (HTML server-side).

    unidade_codigo: código da unidade (ARC, BAM...) ou "TOD" para todas as unidades.
    """
    if unidade_codigo == "TOD":
        url = f"{BASE_URL}/painelinscricoesescolas"
        nome = "Todas as unidades"
    else:
        url = f"{BASE_URL}/painelinscricoesescolas/{unidade_codigo}"
        nome = UNIDADES_ESCOLAS.get(unidade_codigo, unidade_codigo)

    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    escolas, resumo = parse_painel_escolas_html(resp.text)
    logger.info(f"  Escolas {nome}: {len(escolas)} escolas, "
                f"{sum(len(v) for v in resumo.values())} linhas de resumo")
    return escolas, resumo


def fetch_painel_cards(driver):
    """Extrai os cards do painel de controle."""
    logger.info("Acessando Painel de Controle (cards)...")
    driver.get(f"{BASE_URL}/paineldecontrole")
    time.sleep(3)

    html = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
    boxes = re.findall(
        r'<div class="small-box (?:bg-\w+)">.*?<h3>\s*([\d.]+)\s*</h3>.*?<p>\s*([^<]+)\s*</p>',
        html, re.DOTALL
    )
    cards = {}
    for num, label in boxes:
        label_clean = normalizar_texto(label)
        try:
            cards[label_clean] = int(num.replace('.', ''))
        except ValueError:
            cards[label_clean] = num.strip()
    return cards


def save_painel_cursos(df, modalidade, coleta_ts):
    """Salva dados_{MOD}_{ts}.csv (uma linha por curso, opção 1)."""
    timestamp = coleta_ts.strftime("%Y%m%d_%H%M")
    df = df.copy()
    df['Timestamp'] = coleta_ts
    df['Modalidade'] = modalidade

    cols = (['Unidade', 'Curso', 'Vagas', 'Inscritos', 'Homologados',
             'Inscr./Vagas', 'Homolog./Vagas'] + COTAS +
            ['Timestamp', 'Modalidade'])
    filepath = os.path.join(DOWNLOAD_DIR, f"dados_{modalidade}_{timestamp}.csv")
    df[cols].to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"  Salvo: {filepath} ({len(df)} cursos)")
    return filepath


def save_painel_escolas(escolas_por_campus, resumo_por_campus, modalidade, coleta_ts):
    """Salva escolas_{MOD}_{ts}.csv e escolas_resumo_{MOD}_{ts}.csv com coluna Campus."""
    timestamp = coleta_ts.strftime("%Y%m%d_%H%M")
    ts = coleta_ts

    linhas_escolas = []
    for campus, escolas in escolas_por_campus.items():
        for e in escolas:
            linhas_escolas.append({
                'Rank': e.get('Rank'),
                'Campus': campus,
                'Escola': e['Escola'],
                'Cidade': e['Cidade'],
                'Tipo': e['Tipo'],
                'Area': e['Area'],
                'Inscritos': e['Inscritos'],
                'Timestamp': ts,
                'Modalidade': modalidade,
            })
    df_escolas = pd.DataFrame(linhas_escolas)
    path_escolas = None
    if not df_escolas.empty:
        path_escolas = os.path.join(DOWNLOAD_DIR, f"escolas_{modalidade}_{timestamp}.csv")
        df_escolas[['Rank', 'Campus', 'Escola', 'Cidade', 'Tipo', 'Area', 'Inscritos', 'Timestamp', 'Modalidade']].to_csv(
            path_escolas, index=False, encoding="utf-8")
        logger.info(f"  Salvo: {path_escolas} ({len(df_escolas)} linhas)")

    linhas_resumo = []
    for campus, resumo in resumo_por_campus.items():
        for categoria, itens in resumo.items():
            for item in itens:
                linhas_resumo.append({
                    'Campus': campus,
                    'Categoria': categoria,
                    'Label': item['Label'],
                    'Valor': item['Valor'],
                    'Timestamp': ts,
                    'Modalidade': modalidade,
                })
    df_resumo = pd.DataFrame(linhas_resumo)
    path_resumo = None
    if not df_resumo.empty:
        path_resumo = os.path.join(DOWNLOAD_DIR, f"escolas_resumo_{modalidade}_{timestamp}.csv")
        df_resumo.to_csv(path_resumo, index=False, encoding="utf-8")
        logger.info(f"  Salvo: {path_resumo} ({len(df_resumo)} linhas)")

    return path_escolas, path_resumo


def save_cards(cards_por_modalidade, coleta_ts):
    """Salva cards_{ts}.csv a partir dos cards do painel de controle."""
    timestamp = coleta_ts.strftime("%Y%m%d_%H%M")
    rows = []
    for modalidade, cards in cards_por_modalidade.items():
        rows.append({
            'Modalidade': modalidade,
            'Inscricoes': cards.get('Inscrições', 0),
            'InscricoesPagas': cards.get('Inscrições Pagas', 0),
            'Isencao': cards.get('Solic. de Isenção', 0),
            'IsencaoDeferidas': cards.get('Solic. De Isenção Deferidas', 0),
            'CondicoesEspeciais': cards.get('Solic. de Condições Especiais', 0),
            'CondicoesDeferidas': cards.get('Solic. de Condições Especiais Deferidas', 0),
        })
    df_cards = pd.DataFrame(rows)
    filepath = os.path.join(DOWNLOAD_DIR, f"cards_{timestamp}.csv")
    df_cards.to_csv(filepath, index=False, encoding="utf-8")
    logger.info(f"Cards salvos: {filepath}")
    return filepath


def main():
    logger.info("=== Scraper v4 - Novo Layout (cursos + escolas por campus + cards) ===")
    driver = create_driver()
    cards_por_modalidade = {}
    try:
        session = do_login(driver)
        coleta_ts = datetime.now()

        for modalidade in PROCESSOS:
            logger.info(f"\n--- {modalidade} ---")
            session = select_processo(driver, session, modalidade)

            df_cursos = fetch_painel_cursos(driver)
            if df_cursos is not None and not df_cursos.empty:
                save_painel_cursos(df_cursos, modalidade, coleta_ts)
            else:
                logger.warning(f"Sem dados de cursos para {modalidade}")

            logger.info("Coletando escolas por unidade (todas + campi)...")
            escolas_por_campus = {}
            resumo_por_campus = {}
            for codigo in UNIDADES_ESCOLAS:
                try:
                    escolas, resumo = fetch_painel_escolas(session, codigo)
                    nome = UNIDADES_ESCOLAS[codigo]
                    escolas_por_campus[nome] = escolas
                    resumo_por_campus[nome] = resumo
                except Exception as e:
                    logger.error(f"Erro ao buscar escolas de {codigo}: {e}")
                    escolas_por_campus[UNIDADES_ESCOLAS[codigo]] = []
                    resumo_por_campus[UNIDADES_ESCOLAS[codigo]] = {'tipo': [], 'area': [], 'cidade': []}
                time.sleep(0.5)  # gentileza com o servidor

            save_painel_escolas(escolas_por_campus, resumo_por_campus, modalidade, coleta_ts)

            try:
                cards = fetch_painel_cards(driver)
                cards_por_modalidade[modalidade] = cards
                logger.info(f"  Cards {modalidade}: {cards}")
            except Exception as e:
                logger.error(f"Erro ao buscar cards para {modalidade}: {e}")

        if cards_por_modalidade:
            save_cards(cards_por_modalidade, coleta_ts)

    finally:
        driver.quit()
        logger.info("=== Fim ===")


if __name__ == "__main__":
    main()