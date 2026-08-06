#!/bin/bash

# Executa o script em segundo plano
flock -n ./run.lock /mnt/DATA/Dev/python_projetos/vestibular2027/.venv/bin/python /mnt/DATA/Dev/python_projetos/vestibular2027/run.py >/dev/null 2>&1
