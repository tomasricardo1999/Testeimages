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
        "descricao": "Editorial — revista financeira",
        "cores": {
            "FUNDO": "#111318", "PAINEL": "#20232a", "TEXTO": "#f4f0e8",
            "SECUNDARIO": "#b8b1a5", "DESTAQUE": "#c74736",
            "VERDE": "#7fa58b", "CINZENTO": "#625e59",
        },
        "fonte": "DejaVu Serif",
    },
    "institucional": {
        "descricao": "Institucional — relatório corporativo",
        "cores": {
            "FUNDO": "#f4f6f8", "PAINEL": "#e7edf3", "TEXTO": "#172b43",
            "SECUNDARIO": "#536579", "DESTAQUE": "#244f78",
            "VERDE": "#16765b", "CINZENTO": "#bdc8d3",
        },
        "fonte": "DejaVu Sans",
    },
    "criativo": {
        "descricao": "Criativo — laboratório de dados",
        "cores": {
            "FUNDO": "#10152b", "PAINEL": "#202c49", "TEXTO": "#ffffff",
            "SECUNDARIO": "#c7d2ee", "DESTAQUE": "#ff5c8a",
            "VERDE": "#36e0c0", "CINZENTO": "#59698f",
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

    precos = pd.read_csv(historico_csv, index_col=0)
    # O CSV pode misturar datas com e sem fuso horário; normalizar para UTC
    # e remover o fuso mantém um DatetimeIndex consistente em todas as versões de pandas.
    precos.index = pd.to_datetime(precos.index, utc=True, errors="coerce").tz_convert(None)
    precos = precos.loc[~precos.index.isna()].sort_index()
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

def _font(nome: str, tamanho: int):
    caminhos = {
        "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    }
    ficheiro = caminhos[nome]
    try:
        return ImageFont.truetype(ficheiro, tamanho)
    except OSError:
        return ImageFont.load_default()


def aplicar_composicao(pasta: Path, template: str) -> None:
    """Cria uma moldura/layout próprio por template sem alterar pixels/textos do slide."""
    for caminho in sorted(pasta.glob("slide_*.png")):
        original = Image.open(caminho).convert("RGB")
        if template == "editorial":
            # Página de revista: papel quente, cabeçalho editorial, filete e imagem emoldurada.
            canvas = Image.new("RGB", original.size, "#e9e2d6")
            d = ImageDraw.Draw(canvas)
            d.text((58, 28), "THE AMD JOURNAL", font=_font("serif", 29), fill="#24211f")
            d.text((835, 39), "MARKET NOTES  /  2026", font=_font("bold", 12), fill="#62584f")
            d.line((58, 82, 1022, 82), fill="#c74736", width=4)
            img = original.resize((936, 1170), Image.Resampling.LANCZOS)
            canvas.paste(img, (72, 112))
            d.rectangle((71, 111, 1008, 1282), outline="#292522", width=2)
            d.line((58, 1302, 1022, 1302), fill="#b9afa1", width=2)
            d.text((58, 1310), "EQUITY RESEARCH  •  AMD", font=_font("bold", 12), fill="#62584f")
            d.text((945, 1308), "01—11", font=_font("serif", 15), fill="#c74736")
        elif template == "criativo":
            # Poster de dados: moldura assimétrica, formas diagonais e etiqueta de série.
            canvas = Image.new("RGB", original.size, "#10152b")
            d = ImageDraw.Draw(canvas)
            d.polygon([(0, 0), (1080, 0), (1080, 26), (0, 118)], fill="#ff5c8a")
            d.polygon([(0, 1350), (0, 1280), (1080, 1190), (1080, 1350)], fill="#36e0c0")
            d.rounded_rectangle((42, 42, 285, 91), radius=20, fill="#ff5c8a")
            d.text((62, 55), "DATA / VISUALS", font=_font("bold", 17), fill="#10152b")
            img = original.resize((984, 1230), Image.Resampling.LANCZOS)
            canvas.paste(img, (48, 100))
            d.rounded_rectangle((45, 97, 1035, 1333), radius=18, outline="#36e0c0", width=5)
            d.ellipse((965, 34, 1035, 104), fill="#36e0c0")
            d.ellipse((985, 54, 1015, 84), fill="#10152b")
            d.text((54, 1318), "AMD  /  SIGNALS & SYSTEMS", font=_font("bold", 12), fill="#c7d2ee")
        else:
            continue
        canvas.save(caminho, quality=95)

