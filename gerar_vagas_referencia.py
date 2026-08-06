#!/usr/bin/env python3
"""
Gera dados/vagas_referencia.csv a partir dos dados dos editais IFMG 2027:
- Edital 853/2026: Cursos Técnicos Integrados (INT)
- Edital 854/2026: Cursos Técnicos Subsequentes (SUB)
- Edital 855/2026: Cursos de Graduação (SUP)

Colunas: Campus, Curso, Modalidade, FormaSelecao, Turno, TotalVagas
"""

import pandas as pd
import os

# ---------------------------------------------------------------
# EDITAL 853/2026 - CURSOS TÉCNICOS INTEGRADOS (INT)
# (Campus, Curso, TotalVagas, Turno)
# ---------------------------------------------------------------
INT = [
    ("ARCOS", "Técnico Integrado em Administração", 45, "Manhã e Tarde"),
    ("ARCOS", "Técnico Integrado em Mecânica", 45, "Manhã e Tarde"),
    ("BAMBUÍ", "Técnico Integrado em Administração", 40, "Manhã e Tarde"),
    ("BAMBUÍ", "Técnico Integrado em Agroindústria", 30, "Manhã e Tarde"),
    ("BAMBUÍ", "Técnico Integrado em Agropecuária", 90, "Manhã e Tarde"),
    ("BAMBUÍ", "Técnico Integrado em Biotecnologia", 30, "Manhã e Tarde"),
    ("BAMBUÍ", "Técnico Integrado em Eletromecânica", 32, "Manhã e Tarde"),
    ("BAMBUÍ", "Técnico Integrado em Informática", 35, "Manhã e Tarde"),
    ("BETIM", "Técnico Integrado em Automação Industrial", 60, "Manhã e Tarde"),
    ("BETIM", "Técnico Integrado em Mecânica", 60, "Manhã e Tarde"),
    ("BETIM", "Técnico Integrado em Química", 60, "Manhã e Tarde"),
    ("CONGONHAS", "Técnico Integrado em Edificações", 70, "Manhã e Tarde"),
    ("CONGONHAS", "Técnico Integrado em Mecânica", 35, "Manhã e Tarde"),
    ("CONGONHAS", "Técnico Integrado em Mineração", 35, "Manhã e Tarde"),
    ("CONSELHEIRO LAFAIETE", "Técnico Integrado em Eletrotécnica", 40, "Manhã e Tarde"),
    ("CONSELHEIRO LAFAIETE", "Técnico Integrado em Mecânica", 40, "Manhã e Tarde"),
    ("CONSELHEIRO LAFAIETE", "Técnico Integrado em Segurança do Trabalho", 40, "Manhã e Tarde"),
    ("FORMIGA", "Técnico Integrado em Administração", 40, "Manhã e Tarde"),
    ("FORMIGA", "Técnico Integrado em Eletrotécnica", 35, "Manhã e Tarde"),
    ("FORMIGA", "Técnico Integrado em Informática", 40, "Manhã e Tarde"),
    ("GOVERNADOR VALADARES", "Técnico Integrado em Edificações", 40, "Manhã e Tarde"),
    ("GOVERNADOR VALADARES", "Técnico Integrado em Meio Ambiente", 40, "Manhã e Tarde"),
    ("GOVERNADOR VALADARES", "Técnico Integrado em Segurança do Trabalho", 40, "Manhã e Tarde"),
    ("IBIRITÉ", "Técnico Integrado em Automação Industrial", 40, "Manhã e Tarde"),
    ("IBIRITÉ", "Técnico Integrado em Informática", 40, "Manhã e Tarde"),
    ("IBIRITÉ", "Técnico Integrado em Mecatrônica", 40, "Manhã e Tarde"),
    ("IBIRITÉ", "Técnico Integrado em Sistemas de Energia Renovável", 40, "Manhã e Tarde"),
    ("IPATINGA", "Técnico Integrado em Automação Industrial", 40, "Manhã e Tarde"),
    ("IPATINGA", "Técnico Integrado em Eletrotécnica", 40, "Manhã e Tarde"),
    ("ITABIRITO", "Técnico Integrado em Automação Industrial", 70, "Manhã e Tarde"),
    ("ITABIRITO", "Técnico Integrado em Desenvolvimento de Sistemas", 30, "Manhã e Tarde"),
    ("OURO BRANCO", "Técnico Integrado em Administração", 40, "Manhã e Tarde"),
    ("OURO BRANCO", "Técnico Integrado em Informática", 40, "Manhã e Tarde"),
    ("OURO BRANCO", "Técnico Integrado em Metalurgia", 40, "Manhã e Tarde"),
    ("OURO PRETO", "Técnico Integrado em Administração", 60, "Manhã e Tarde"),
    ("OURO PRETO", "Técnico Integrado em Automação Industrial", 80, "Manhã e Tarde"),
    ("OURO PRETO", "Técnico Integrado em Edificações", 90, "Manhã e Tarde"),
    ("OURO PRETO", "Técnico Integrado em Metalurgia", 90, "Manhã e Tarde"),
    ("OURO PRETO", "Técnico Integrado em Mineração", 90, "Manhã e Tarde"),
    ("PIUMHI", "Técnico Integrado em Edificações", 80, "Manhã e Tarde"),
    ("PONTE NOVA", "Técnico Integrado em Administração", 40, "Manhã e Tarde"),
    ("PONTE NOVA", "Técnico Integrado em Informática", 35, "Manhã e Tarde"),
    ("RIBEIRÃO DAS NEVES", "Técnico Integrado em Administração", 60, "Manhã e Tarde"),
    ("RIBEIRÃO DAS NEVES", "Técnico Integrado em Eletroeletrônica", 35, "Manhã e Tarde"),
    ("RIBEIRÃO DAS NEVES", "Técnico Integrado em Informática", 60, "Manhã e Tarde"),
    ("SABARÁ", "Técnico Integrado em Administração", 35, "Manhã e Tarde"),
    ("SABARÁ", "Técnico Integrado em Eletrônica", 70, "Manhã e Tarde"),
    ("SABARÁ", "Técnico Integrado em Informática", 35, "Manhã e Tarde"),
    ("SANTA LUZIA", "Técnico Integrado em Edificações", 80, "Manhã e Tarde"),
    ("SANTA LUZIA", "Técnico Integrado em Meio Ambiente", 40, "Manhã e Tarde"),
    ("SANTA LUZIA", "Técnico Integrado em Segurança do Trabalho", 40, "Manhã e Tarde"),
    ("SÃO JOÃO EVANGELISTA", "Técnico Integrado em Agrimensura", 40, "Manhã e Tarde"),
    ("SÃO JOÃO EVANGELISTA", "Técnico Integrado em Agropecuária", 70, "Manhã e Tarde"),
    ("SÃO JOÃO EVANGELISTA", "Técnico Integrado em Informática", 70, "Manhã e Tarde"),
    ("SÃO JOÃO EVANGELISTA", "Técnico Integrado em Nutrição e Dietética", 70, "Manhã e Tarde"),
]

# ---------------------------------------------------------------
# EDITAL 854/2026 - CURSOS TÉCNICOS SUBSEQUENTES (SUB)
# (Campus, Curso, TotalVagas, Turno)
# ---------------------------------------------------------------
SUB = [
    ("BAMBUÍ", "Técnico Subsequente em Agropecuária", 30, "Manhã e Tarde"),
    ("CONGONHAS", "Técnico Subsequente em Mecânica", 35, "Noite"),
    ("CONGONHAS", "Técnico Subsequente em Mineração", 35, "Noite"),
    ("CONSELHEIRO LAFAIETE", "Técnico Subsequente em Eletrotécnica", 40, "Noite"),
    ("CONSELHEIRO LAFAIETE", "Técnico Subsequente em Mecânica", 40, "Noite"),
    ("GOVERNADOR VALADARES", "Técnico Subsequente em Segurança do Trabalho", 40, "Noite"),
    ("IPATINGA", "Técnico Subsequente em Eletrotécnica", 40, "Noite"),
    ("OURO PRETO", "Técnico Subsequente em Edificações", 30, "Noite"),
    ("OURO PRETO", "Técnico Subsequente em Joalheria", 12, "Noite"),
    ("OURO PRETO", "Técnico Subsequente em Metalurgia", 20, "Noite"),
    ("OURO PRETO", "Técnico Subsequente em Meio Ambiente", 30, "Noite"),
    ("OURO PRETO", "Técnico Subsequente em Mineração", 30, "Noite"),
    ("OURO PRETO", "Técnico Subsequente em Segurança do Trabalho", 70, "Noite"),
    ("PIUMHI", "Técnico Subsequente em Enfermagem", 30, "Noite"),
    ("RIBEIRÃO DAS NEVES", "Técnico Subsequente em Logística", 120, "100% EAD"),
    ("SANTA LUZIA", "Técnico Subsequente em Segurança do Trabalho", 40, "Noite"),
    ("SANTA LUZIA", "Técnico Subsequente em Defesa Civil", 60, "80% EAD"),
]

# ---------------------------------------------------------------
# EDITAL 855/2026 - CURSOS DE GRADUAÇÃO (SUP)
# (Campus, Curso, TotalVagas, Turno, FormaSelecao)
# FormaSelecao: ENEM | Histórico e Redação
# ---------------------------------------------------------------
SUP = [
    ("ARCOS", "Engenharia Mecânica", 20, "Noite", "ENEM"),
    ("ARCOS", "Engenharia Mecânica", 15, "Noite", "Histórico e Redação"),
    ("ARCOS", "Direito", 15, "Noite", "Histórico e Redação"),
    ("BAMBUÍ", "Administração", 20, "Noite", "ENEM"),
    ("BAMBUÍ", "Agronomia", 30, "Manhã e Tarde", "ENEM"),
    ("BAMBUÍ", "Ciências Biológicas", 13, "Noite", "ENEM"),
    ("BAMBUÍ", "Ciências Biológicas", 12, "Noite", "Histórico e Redação"),
    ("BAMBUÍ", "Educação Física", 14, "Noite", "ENEM"),
    ("BAMBUÍ", "Educação Física", 12, "Noite", "Histórico e Redação"),
    ("BAMBUÍ", "Inteligência Artificial", 25, "Manhã e Tarde", "ENEM"),
    ("BAMBUÍ", "Engenharia de Produção", 20, "Manhã e Tarde", "ENEM"),
    ("BAMBUÍ", "Engenharia de Produção", 5, "Manhã e Tarde", "Histórico e Redação"),
    ("BAMBUÍ", "Física", 14, "Noite", "ENEM"),
    ("BAMBUÍ", "Física", 12, "Noite", "Histórico e Redação"),
    ("BAMBUÍ", "Medicina Veterinária", 25, "Manhã e Tarde", "ENEM"),
    ("BAMBUÍ", "Zootecnia", 20, "Manhã e Tarde", "ENEM"),
    ("BAMBUÍ", "Zootecnia", 4, "Manhã e Tarde", "Histórico e Redação"),
    ("BETIM", "Engenharia de Controle e Automação", 18, "Noite", "ENEM"),
    ("BETIM", "Engenharia Mecânica", 18, "Noite", "ENEM"),
    ("BETIM", "Química", 20, "Noite", "ENEM"),
    ("CONGONHAS", "Engenharia de Produção", 20, "Noite", "ENEM"),
    ("CONGONHAS", "Física", 10, "Noite", "ENEM"),
    ("CONGONHAS", "Física", 10, "Noite", "Histórico e Redação"),
    ("CONGONHAS", "Letras (Português/Inglês)", 10, "Noite", "ENEM"),
    ("CONGONHAS", "Letras (Português/Inglês)", 10, "Noite", "Histórico e Redação"),
    ("FORMIGA", "Administração", 15, "Noite", "ENEM"),
    ("FORMIGA", "Administração", 15, "Noite", "Histórico e Redação"),
    ("FORMIGA", "Ciência da Computação", 20, "Manhã e Tarde", "ENEM"),
    ("FORMIGA", "Ciência da Computação", 8, "Manhã e Tarde", "Histórico e Redação"),
    ("FORMIGA", "Engenharia Elétrica", 12, "Noite", "ENEM"),
    ("FORMIGA", "Engenharia Elétrica", 14, "Noite", "Histórico e Redação"),
    ("FORMIGA", "Matemática", 15, "Noite", "ENEM"),
    ("FORMIGA", "Matemática", 10, "Noite", "Histórico e Redação"),
    ("GOVERNADOR VALADARES", "Engenharia Ambiental e Sanitária", 17, "Manhã e Noite", "ENEM"),
    ("GOVERNADOR VALADARES", "Engenharia Ambiental e Sanitária", 17, "Manhã e Noite", "Histórico e Redação"),
    ("GOVERNADOR VALADARES", "Engenharia Civil", 17, "Noite", "ENEM"),
    ("GOVERNADOR VALADARES", "Engenharia Civil", 17, "Noite", "Histórico e Redação"),
    ("GOVERNADOR VALADARES", "Engenharia de Produção", 17, "Noite", "ENEM"),
    ("GOVERNADOR VALADARES", "Engenharia de Produção", 17, "Noite", "Histórico e Redação"),
    ("GOVERNADOR VALADARES", "Gestão Ambiental", 17, "Noite", "ENEM"),
    ("GOVERNADOR VALADARES", "Gestão Ambiental", 17, "Noite", "Histórico e Redação"),
    ("IBIRITÉ", "Ciência da Computação", 20, "Noite", "ENEM"),
    ("IBIRITÉ", "Engenharia de Controle e Automação", 20, "Noite", "ENEM"),
    ("IPATINGA", "Engenharia Elétrica", 15, "Manhã, Tarde e Noite", "ENEM"),
    ("IPATINGA", "Engenharia Elétrica", 10, "Manhã, Tarde e Noite", "Histórico e Redação"),
    ("ITABIRITO", "Engenharia Elétrica", 10, "Noite", "ENEM"),
    ("ITABIRITO", "Engenharia Elétrica", 10, "Noite", "Histórico e Redação"),
    ("OURO BRANCO", "Administração", 20, "Noite", "ENEM"),
    ("OURO BRANCO", "Administração", 20, "Noite", "Histórico e Redação"),
    ("OURO BRANCO", "Engenharia Metalúrgica", 10, "Noite", "ENEM"),
    ("OURO BRANCO", "Engenharia Metalúrgica", 25, "Noite", "Histórico e Redação"),
    ("OURO BRANCO", "Pedagogia", 20, "Noite", "ENEM"),
    ("OURO BRANCO", "Pedagogia", 20, "Noite", "Histórico e Redação"),
    ("OURO BRANCO", "Sistemas de Informação", 15, "Noite", "ENEM"),
    ("OURO BRANCO", "Sistemas de Informação", 25, "Noite", "Histórico e Redação"),
    ("OURO PRETO", "Análise e Desenvolvimento de Sistemas", 15, "Noite", "ENEM"),
    ("OURO PRETO", "Análise e Desenvolvimento de Sistemas", 5, "Noite", "Histórico e Redação"),
    ("OURO PRETO", "Conservação e Restauro", 15, "Noite", "ENEM"),
    ("OURO PRETO", "Conservação e Restauro", 15, "Noite", "Histórico e Redação"),
    ("OURO PRETO", "Física", 10, "Noite", "ENEM"),
    ("OURO PRETO", "Física", 5, "Noite", "Histórico e Redação"),
    ("OURO PRETO", "Geografia", 15, "Noite", "ENEM"),
    ("OURO PRETO", "Geografia", 15, "Noite", "Histórico e Redação"),
    ("OURO PRETO", "Gestão da Qualidade", 18, "Noite", "ENEM"),
    ("PIUMHI", "Engenharia Civil", 20, "Noite", "ENEM"),
    ("PONTE NOVA", "Processos Gerenciais", 20, "Noite", "ENEM"),
    ("PONTE NOVA", "Processos Gerenciais", 20, "Noite", "Histórico e Redação"),
    ("RIBEIRÃO DAS NEVES", "Administração", 20, "Noite", "ENEM"),
    ("RIBEIRÃO DAS NEVES", "Análise e Desenvolvimento de Sistemas", 18, "Noite", "ENEM"),
    ("RIBEIRÃO DAS NEVES", "Processos Gerenciais", 20, "Noite", "ENEM"),
    ("SABARÁ", "Administração", 15, "Noite", "ENEM"),
    ("SABARÁ", "Administração", 15, "Noite", "Histórico e Redação"),
    ("SABARÁ", "Engenharia de Controle e Automação", 16, "Noite", "ENEM"),
    ("SABARÁ", "Engenharia de Controle e Automação", 12, "Noite", "Histórico e Redação"),
    ("SABARÁ", "Logística", 10, "Noite", "ENEM"),
    ("SABARÁ", "Logística", 30, "Noite", "Histórico e Redação"),
    ("SABARÁ", "Sistemas de Informação", 15, "Manhã", "ENEM"),
    ("SABARÁ", "Sistemas de Informação", 10, "Manhã", "Histórico e Redação"),
    ("SANTA LUZIA", "Arquitetura e Urbanismo", 20, "Tarde", "ENEM"),
    ("SANTA LUZIA", "Arquitetura e Urbanismo", 10, "Tarde", "Histórico e Redação"),
    ("SANTA LUZIA", "Design de Interiores", 20, "Noite", "ENEM"),
    ("SANTA LUZIA", "Design de Interiores", 10, "Noite", "Histórico e Redação"),
    ("SANTA LUZIA", "Engenharia Civil", 20, "Noite", "ENEM"),
    ("SANTA LUZIA", "Engenharia Civil", 10, "Noite", "Histórico e Redação"),
    ("SÃO JOÃO EVANGELISTA", "Administração", 15, "Noite", "ENEM"),
    ("SÃO JOÃO EVANGELISTA", "Administração", 15, "Noite", "Histórico e Redação"),
    ("SÃO JOÃO EVANGELISTA", "Agronomia", 15, "Manhã e Tarde", "ENEM"),
    ("SÃO JOÃO EVANGELISTA", "Agronomia", 15, "Manhã e Tarde", "Histórico e Redação"),
    ("SÃO JOÃO EVANGELISTA", "Ciências Biológicas", 15, "Noite", "ENEM"),
    ("SÃO JOÃO EVANGELISTA", "Ciências Biológicas", 15, "Noite", "Histórico e Redação"),
    ("SÃO JOÃO EVANGELISTA", "Engenharia Florestal", 15, "Manhã e Tarde", "ENEM"),
    ("SÃO JOÃO EVANGELISTA", "Engenharia Florestal", 15, "Manhã e Tarde", "Histórico e Redação"),
    ("SÃO JOÃO EVANGELISTA", "Matemática", 15, "Noite", "ENEM"),
    ("SÃO JOÃO EVANGELISTA", "Matemática", 15, "Noite", "Histórico e Redação"),
    ("SÃO JOÃO EVANGELISTA", "Pedagogia", 15, "Noite", "ENEM"),
    ("SÃO JOÃO EVANGELISTA", "Pedagogia", 15, "Noite", "Histórico e Redação"),
    ("SÃO JOÃO EVANGELISTA", "Sistemas de Informação", 15, "Manhã e Tarde", "ENEM"),
    ("SÃO JOÃO EVANGELISTA", "Sistemas de Informação", 15, "Manhã e Tarde", "Histórico e Redação"),
]


def main():
    rows = []
    # INT
    for campus, curso, vagas, turno in INT:
        rows.append({"Campus": campus, "Curso": curso, "Modalidade": "INT",
                     "FormaSelecao": "", "Turno": turno, "TotalVagas": vagas})
    # SUB
    for campus, curso, vagas, turno in SUB:
        rows.append({"Campus": campus, "Curso": curso, "Modalidade": "SUB",
                     "FormaSelecao": "", "Turno": turno, "TotalVagas": vagas})
    # SUP
    for campus, curso, vagas, turno, forma in SUP:
        rows.append({"Campus": campus, "Curso": curso, "Modalidade": "SUP",
                     "FormaSelecao": forma, "Turno": turno, "TotalVagas": vagas})

    df = pd.DataFrame(rows, columns=["Campus", "Curso", "Modalidade", "FormaSelecao", "Turno", "TotalVagas"])

    # Garante pasta dados
    os.makedirs("dados", exist_ok=True)
    out = "dados/vagas_referencia.csv"
    df.to_csv(out, index=False, encoding="utf-8")

    print(f"Gerado: {out}")
    print(f"Total de linhas: {len(df)}")
    print(f"Por modalidade: {df.groupby('Modalidade')['TotalVagas'].sum().to_dict()}")
    print(f"Por modalidade (linhas): {df.groupby('Modalidade').size().to_dict()}")


if __name__ == "__main__":
    main()