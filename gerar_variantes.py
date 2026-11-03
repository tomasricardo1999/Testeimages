#!/usr/bin/env python3
"""Gera três versões visuais do mesmo carrossel, sem alterar dados nem textos.

Uso:
    python gerar_variantes.py

As variantes são guardadas em:
    dados_amd/instagram/variantes/editorial/
    dados_amd/instagram/variantes/institucional/
    dados_amd/instagram/variantes/criativo/
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import gerar_carrossel as historico
import gerar_carrossel_finviz as finviz

ROOT = Path(__file__).resolve().parent
DADOS = ROOT / "dados_amd"
SAIDA = DADOS / "instagram" / "variantes"

TEMPLATES = {
    "editorial": {
        "descricao": "Editorial premium",
        "cores": {
            "FUNDO": "#101318", "PAINEL": "#191f27", "TEXTO": "#f3f5f7",
            "SECUNDARIO": "#aab3bf", "DESTAQUE": "#e21b2d",
            "VERDE": "#55c49a", "CINZENTO": "#596574",
        },
        "fonte": "DejaVu Sans",
    },
    "institucional": {
        "descricao": "Financeiro institucional",
        "cores": {
            "FUNDO": "#f4f6f8", "PAINEL": "#e7edf3", "TEXTO": "#172b43",
            "SECUNDARIO": "#536579", "DESTAQUE": "#244f78",
            "VERDE": "#16765b", "CINZENTO": "#bdc8d3",
        },
        "fonte": "DejaVu Sans",
    },
    "criativo": {
        "descricao": "Moderno e criativo",
        "cores": {
            "FUNDO": "#111827", "PAINEL": "#202c40", "TEXTO": "#f8fafc",
            "SECUNDARIO": "#c1cada", "DESTAQUE": "#ff6b6b",
            "VERDE": "#45d6b5", "CINZENTO": "#52627a",
        },
        "fonte": "DejaVu Sans",
    },
}


def aplicar_template(config: dict) -> None:
    """Aplica apenas estilo: paleta e tipografia; não toca nos dados/textos."""
    for nome, cor in config["cores"].items():
        setattr(historico, nome, cor)
        setattr(finviz, nome, cor)
    plt.rcParams["font.family"] = config["fonte"]
    plt.rcParams["figure.facecolor"] = config["cores"]["FUNDO"]
    plt.rcParams["savefig.facecolor"] = config["cores"]["FUNDO"]


def carregar_dados():
    historico_csv = DADOS / "amd_historico.csv"
    resultados_csv = DADOS / "amd_resultados_anuais.csv"
    finviz_json = DADOS / "amd_finviz.json"

    if not historico_csv.exists():
        raise FileNotFoundError(f"Falta o ficheiro {historico_csv}")
    if not resultados_csv.exists():
        raise FileNotFoundError(f"Falta o ficheiro {resultados_csv}")
    if not finviz_json.exists():
        raise FileNotFoundError(f"Falta o ficheiro {finviz_json}")

    precos = pd.read_csv(historico_csv, index_col=0, parse_dates=True)
    resultados = pd.read_csv(resultados_csv, index_col=0)
    with finviz_json.open("r", encoding="utf-8") as ficheiro:
        dados_finviz = json.load(ficheiro)
    return precos, resultados, dados_finviz


def main() -> None:
    precos, resultados, dados_finviz = carregar_dados()
    for nome, config in TEMPLATES.items():
        aplicar_template(config)
        pasta = SAIDA / nome
        pasta.mkdir(parents=True, exist_ok=True)
        historico.gerar_carrossel("AMD", precos, resultados, pasta, "5y")
        finviz.gerar_carrossel_finviz("AMD", dados_finviz, pasta)
        print(f"Template '{config['descricao']}' gerado em: {pasta}")

    print("\nConcluído: 3 templates × 11 slides. Os dados e textos de origem foram mantidos.")


if __name__ == "__main__":
    main()
