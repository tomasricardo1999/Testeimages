#!/usr/bin/env python3
"""Gera variantes editoriais para qualquer ticker a partir dos CSVs/JSON existentes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import gerar_carrossel as historico
import gerar_carrossel_finviz as finviz

TEMPLATES = {
    "editorial": {
        "descricao": "Editorial — revista financeira",
        "cores": {"FUNDO":"#111318","PAINEL":"#20232a","TEXTO":"#f4f0e8","SECUNDARIO":"#b8b1a5","DESTAQUE":"#c74736","VERDE":"#7fa58b","CINZENTO":"#625e59"},
        "fonte": "DejaVu Serif",
    },
    "institucional": {
        "descricao": "Institucional — relatório corporativo",
        "cores": {"FUNDO":"#f4f6f8","PAINEL":"#e7edf3","TEXTO":"#172b43","SECUNDARIO":"#536579","DESTAQUE":"#244f78","VERDE":"#16765b","CINZENTO":"#bdc8d3"},
        "fonte": "DejaVu Sans",
    },
    "criativo": {
        "descricao": "Criativo — laboratório de dados",
        "cores": {"FUNDO":"#10152b","PAINEL":"#202c49","TEXTO":"#ffffff","SECUNDARIO":"#c7d2ee","DESTAQUE":"#ff5c8a","VERDE":"#36e0c0","CINZENTO":"#59698f"},
        "fonte": "DejaVu Sans",
    },
}

def aplicar_template(config):
    for nome, cor in config["cores"].items():
        setattr(historico, nome, cor)
        setattr(finviz, nome, cor)
    plt.rcParams["font.family"] = config["fonte"]
    plt.rcParams["figure.facecolor"] = config["cores"]["FUNDO"]
    plt.rcParams["savefig.facecolor"] = config["cores"]["FUNDO"]

def _font(nome, tamanho):
    caminho = {
        "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    }[nome]
    try:
        return ImageFont.truetype(caminho, tamanho)
    except OSError:
        return ImageFont.load_default()

def aplicar_composicao(pasta: Path, template: str, ticker: str):
    for caminho in sorted(pasta.glob("slide_*.png")):
        original = Image.open(caminho).convert("RGB")
        largura, altura = original.size
        if template == "editorial":
            canvas = Image.new("RGB", (largura, altura), "#e9e2d6")
            d = ImageDraw.Draw(canvas)
            d.text((58, 24), f"{ticker} JOURNAL", font=_font("serif", 29), fill="#24211f")
            d.text((largura-340, 36), "MARKET NOTES  /  EQUITY RESEARCH", font=_font("bold", 12), fill="#62584f")
            d.line((58, 78, largura-58, 78), fill="#c74736", width=4)
            margem_x, topo, rodape = 72, 104, 64
            img = original.resize((largura-2*margem_x, altura-topo-rodape), Image.Resampling.LANCZOS)
            canvas.paste(img, (margem_x, topo))
            d.rectangle((margem_x-1, topo-1, largura-margem_x+1, altura-rodape), outline="#292522", width=2)
            d.line((58, altura-rodape+8, largura-58, altura-rodape+8), fill="#b9afa1", width=2)
            d.text((58, altura-rodape+17), f"INVESTMENT RESEARCH  •  {ticker}", font=_font("bold", 12), fill="#62584f")
            d.text((largura-120, altura-rodape+15), "01—11", font=_font("serif", 15), fill="#c74736")
        elif template == "criativo":
            canvas = Image.new("RGB", (largura, altura), "#10152b")
            d = ImageDraw.Draw(canvas)
            d.polygon([(0,0),(largura,0),(largura,26),(0,118)], fill="#ff5c8a")
            d.polygon([(0,altura),(0,altura-70),(largura,altura-160),(largura,altura)], fill="#36e0c0")
            d.rounded_rectangle((42,42,285,91), radius=20, fill="#ff5c8a")
            d.text((62,55), "DATA / VISUALS", font=_font("bold",17), fill="#10152b")
            img = original.resize((largura-96, altura-200), Image.Resampling.LANCZOS)
            canvas.paste(img, (48,100))
            d.rounded_rectangle((45,97,largura-45,altura-67), radius=18, outline="#36e0c0", width=5)
            d.ellipse((largura-115,34,largura-45,104), fill="#36e0c0")
            d.ellipse((largura-95,54,largura-65,84), fill="#10152b")
            d.text((54,altura-31), f"{ticker}  /  SIGNALS & SYSTEMS", font=_font("bold",12), fill="#c7d2ee")
        else:
            continue
        canvas.save(caminho)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ticker", default="AMD")
    parser.add_argument("--dados", default="dados_amd")
    args = parser.parse_args()
    ticker = args.ticker.upper()
    dados = Path(args.dados)
    csv_historico = dados / f"{ticker.lower()}_historico.csv"
    csv_resultados = dados / f"{ticker.lower()}_resultados_anuais.csv"
    json_finviz = dados / f"{ticker.lower()}_finviz.json"
    for p in (csv_historico, csv_resultados, json_finviz):
        if not p.exists():
            raise FileNotFoundError(f"Falta o ficheiro necessário: {p}")
    precos = pd.read_csv(csv_historico, index_col=0)
    precos.index = pd.to_datetime(precos.index, utc=True, errors="coerce").tz_convert(None)
    precos = precos.loc[~precos.index.isna()].sort_index()
    resultados = pd.read_csv(csv_resultados, index_col=0)
    with json_finviz.open(encoding="utf-8") as f:
        dados_finviz = json.load(f)
    saida = dados / "instagram" / "variantes"
    for nome, config in TEMPLATES.items():
        aplicar_template(config)
        pasta = saida / nome
        pasta.mkdir(parents=True, exist_ok=True)
        historico.gerar_carrossel(ticker, precos, resultados, pasta, "5y")
        finviz.gerar_carrossel_finviz(ticker, dados_finviz, pasta)
        aplicar_composicao(pasta, nome, ticker)
        print(f"{ticker}: template {config['descricao']} gerado em {pasta}")
    print(f"Concluído: {ticker}, 3 templates × 11 slides.")

if __name__ == "__main__":
    main()
