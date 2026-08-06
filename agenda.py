import schedule
import subprocess
import time
import sys
from log import logger

PYTHON = "/mnt/DATA/Dev/python_projetos/vestibular2027/.venv/bin/python"

# Função para executar os scripts 
def executar():
    print("Executando agenda.py...")
    print("  Executando scraper_v3_final.py...")
    logger.info("Executando scraper_v3_final.py...")
    subprocess.run([PYTHON, "scraper_v3_final.py"])
    logger.info("Execução finalizada.")

    print("  Executando processa.py...")
    logger.info("Executando processa.py...")
    subprocess.run([PYTHON, "processa.py"])
    logger.info("Execução finalizada.")

    print("  Executando gitrun.py...")
    logger.info("Executando gitrun.py...")
    subprocess.run([PYTHON, "gitrun.py", "-m", "data update using git"])
    logger.info("Execução finalizada.")

    print("Aguardando próximo agendamento...")

if __name__ == "__main__":
    logger.info("Iniciando agendamento...")
    agendamentos = ["07:00", "12:00", "18:00" ,"22:00"] 
    for i, a in enumerate(agendamentos):
        text = f"{i+1}° agendamento para {a}"
        print(text)
        logger.info(text)
        # Agendar as tarefas
        schedule.every().day.at(a).do(executar)

    # Loop para manter o agendador rodando
    while True:
        schedule.run_pending()  # Executa tarefas agendadas
        time.sleep(10)  # Pausa para evitar alto consumo de CPU
    
    logger.info("Agendamento finalizado.")
