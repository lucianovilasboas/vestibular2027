import schedule
import subprocess
import time
import sys
from log import logger

PYTHON = "/mnt/DATA/Dev/python_projetos/vestibular2027/.venv/bin/python"

# Função para executar os scripts 
def executar():
    print("  Executando scraper_v4.py (novo layout: cursos + escolas + cards)...")
    logger.info("  Executando scraper_v4.py...")
    subprocess.run([PYTHON, "scraper_v4.py"])
    logger.info("  Execução finalizada.")

    print("  Executando processa_v2.py...")
    logger.info("  Executando processa_v2.py...")
    subprocess.run([PYTHON, "processa_v2.py"])
    logger.info("  Execução finalizada.")

    print("  Executando gitrun.py...")
    logger.info("  Executando gitrun.py...")
    subprocess.run([PYTHON, "gitrun.py", "-m", "data update using git"])
    logger.info("  Execução finalizada.")


if __name__ == "__main__":
    logger.info(f"Execução via 'run.py' inicializada às {time.strftime('%d-%m-%Y %H:%M:%S')}")
    executar()
    logger.info(f"Execução via 'run.py' finalizada às {time.strftime('%d-%m-%Y %H:%M:%S')}")
