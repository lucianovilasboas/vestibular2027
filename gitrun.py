import git
from pathlib import Path
from log import logger
import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Commit and push changes to a git repository.')
    parser.add_argument("-m","--message", type=str, help='Commit message', required=True)
    args = parser.parse_args()

    # Caminho para o diretório do repositório Git
    repo_path = './'
    repo = git.Repo(repo_path)

    # Verifica se existem modificações no repositório
    if repo.is_dirty(untracked_files=True):
        # Adiciona todos os arquivos modificados e não rastreados
        # repo.git.add(all=True)

        # command: git add ./dados/processed/all_data.csv
        repo.git.add([
            "./dados/processed/all_data.csv",
            "./dados/processed/cards.csv",
            "./dados/vagas_referencia.csv",
        ])

        # Faz o commit
        # command: git commit -m "Data update using git 
        commit = repo.index.commit(args.message)

        # Opcional: Push para o repositório remoto
        origin = repo.remote(name='origin')

        # command: git push origin main
        origin.push("main")

        # Obtém os arquivos que foram comitados
        comitados = list(commit.stats.files.keys())

        # Printar os arquivos comitados após o push
        if comitados:
            for file in comitados:
                logger.info("Arquivo comitado: %s", file)    

    else:
        logger.info("Não há mudanças para comitar.")
        print("Não há mudanças para comitar.")
