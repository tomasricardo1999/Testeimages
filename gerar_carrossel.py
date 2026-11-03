#!/usr/bin/env python3
"""Gera um carrossel editorial para Instagram a partir dos dados financeiros."""
from __future__ import annotations

from pathlib import Path
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

LOG = logging.getLogger("carrossel")
FUNDO = "#101318"
PAINEL = "#191f27"
TEXTO = "#f3f5f7"
SECUNDARIO = "#aab3bf"
DESTAQUE = "#e21b2d"
VERDE = "#55c49a"
CINZENTO = "#596574"


def _base(titulo: str, numero: int, subtitulo: str = ""):
    fig = plt.figure(figsize=(8, 10), facecolor=FUNDO)
    fig.text(0.075, 0.94, "MERCADOS  /  ANÁLISE DE EMPRESA",
             color=DESTAQUE, fontsize=10, weight="bold")
    fig.text(0.075, 0.875, titulo, color=TEXTO, fontsize=25,
             weight="bold", va="top", wrap=True)
    if subtitulo:
        fig.text(0.075, 0.79, subtitulo, color=SECUNDARIO, fontsize=11, va="top")
    fig.text(0.075, 0.045, "AMD  •  DADOS DE MERCADO  •  FONTE: YAHOO FINANCE",
             color=SECUNDARIO, fontsize=7.5)
    fig.text(0.925, 0.045, f"{numero:02d} / 06", color=DESTAQUE,
             fontsize=9, weight="bold", ha="right")
    return fig


def _eixo_escuro(ax):
    ax.set_facecolor(PAINEL)
    ax.tick_params(colors=SECUNDARIO, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(CINZENTO)
    ax.grid(True, color=CINZENTO, alpha=0.25, linewidth=0.7)
    ax.xaxis.label.set_color(SECUNDARIO)
    ax.yaxis.label.set_color(SECUNDARIO)
    ax.title.set_color(TEXTO)


def gerar_carrossel(ticker: str, precos: pd.DataFrame, resultados: pd.DataFrame,
                     pasta: Path, periodo: str = "5y") -> None:
    """Cria seis PNGs 4:5 e um texto-base para a legenda."""
    pasta.mkdir(parents=True, exist_ok=True)
    if precos is None or precos.empty or "Close" not in precos:
        LOG.warning("Sem dados de preço: carrossel não gerado.")
        return

    close = pd.to_numeric(precos["Close"], errors="coerce").dropna()
    if close.empty:
        LOG.warning("Sem preços válidos: carrossel não gerado.")
        return
    primeiro, ultimo = float(close.iloc[0]), float(close.iloc[-1])
    variacao = (ultimo / primeiro - 1) * 100 if primeiro else 0
    datas = close.index
    data_final = pd.Timestamp(datas[-1]).strftime("%d/%m/%Y")
    moeda = "USD"

    # 1 — Capa
    fig = _base(f"{ticker}: uma leitura dos números", 1,
                f"Desempenho de mercado e indicadores financeiros  •  período {periodo}")
    fig.text(0.085, 0.61, "ANÁLISE FUNDAMENTAL E DE MERCADO",
             color=SECUNDARIO, fontsize=10)
    fig.text(0.08, 0.48, f"{variacao:+.1f}%", color=VERDE if variacao >= 0 else DESTAQUE,
             fontsize=48, weight="bold")
    fig.text(0.085, 0.41, "variação do preço de fecho no período observado",
             color=SECUNDARIO, fontsize=11)
    fig.text(0.085, 0.25, f"Último fecho: {ultimo:,.2f} {moeda}",
             color=TEXTO, fontsize=17, weight="bold")
    fig.text(0.085, 0.19, f"Dados de mercado até {data_final}",
             color=SECUNDARIO, fontsize=10)
    fig.savefig(pasta / "slide_01_capa.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)

    # 2 — Preço
    fig = _base("Como evoluiu a cotação?", 2,
                "Preço de fecho ajustado? Não — preço de fecho reportado pelo Yahoo Finance.")
    ax = fig.add_axes([0.10, 0.25, 0.82, 0.43])
    _eixo_escuro(ax)
    ax.plot(datas, close.values, color=DESTAQUE, linewidth=2)
    ax.fill_between(datas, close.values, close.min(), color=DESTAQUE, alpha=0.12)
    ax.set_ylabel("Preço (USD)")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    fig.text(0.10, 0.16, f"{primeiro:,.2f} USD  →  {ultimo:,.2f} USD",
             color=TEXTO, fontsize=14, weight="bold")
    fig.savefig(pasta / "slide_02_preco.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)

    # 3 — Volume
    fig = _base("Atividade de negociação", 3,
                "O volume ajuda a contextualizar a intensidade da negociação.")
    if "Volume" in precos:
        volume = pd.to_numeric(precos["Volume"], errors="coerce").dropna()
        ax = fig.add_axes([0.10, 0.25, 0.82, 0.43])
        _eixo_escuro(ax)
        ax.bar(volume.index, volume.values, color=DESTAQUE, width=1.0, alpha=0.85)
        ax.set_ylabel("Ações negociadas")
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        mediana = float(volume.median()) if not volume.empty else 0
        fig.text(0.10, 0.16, f"Volume mediano por sessão: {mediana:,.0f}",
                 color=TEXTO, fontsize=13, weight="bold")
    else:
        fig.text(0.10, 0.48, "Dados de volume indisponíveis nesta consulta.",
                 color=SECUNDARIO, fontsize=13)
    fig.savefig(pasta / "slide_03_volume.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)

    # Extrair receita e lucro anual (quando disponíveis)
    receita = lucro = None
    periodos = []
    if resultados is not None and not resultados.empty:
        idx = {str(i).lower(): i for i in resultados.index}
        rk = next((v for k, v in idx.items() if "total revenue" in k or k == "revenue"), None)
        lk = next((v for k, v in idx.items() if "net income" in k), None)
        if rk is not None:
            receita = pd.to_numeric(resultados.loc[rk], errors="coerce")
        if lk is not None:
            lucro = pd.to_numeric(resultados.loc[lk], errors="coerce")
        if receita is not None or lucro is not None:
            financeiro = pd.DataFrame({"Receita": receita, "Lucro líquido": lucro})
            financeiro = financeiro.dropna(how="all").sort_index()
            periodos = list(financeiro.index)
        else:
            financeiro = pd.DataFrame()
    else:
        financeiro = pd.DataFrame()

    # 4 — Receita e lucro
    fig = _base("Receita e lucro", 4,
                "Indicadores anuais reportados pela empresa; valores em milhares/milhões conforme a fonte.")
    if not financeiro.empty:
        ax = fig.add_axes([0.10, 0.26, 0.82, 0.42])
        _eixo_escuro(ax)
        financeiro.plot(kind="bar", ax=ax, color=[DESTAQUE, VERDE], alpha=0.9)
        ax.set_ylabel("Valor reportado (USD)")
        ax.set_xlabel("Exercício")
        ax.tick_params(axis="x", rotation=0)
        ax.legend(facecolor=PAINEL, labelcolor=TEXTO, fontsize=8)
    else:
        fig.text(0.10, 0.48, "A demonstração de resultados não forneceu\\nreceita/lucro para construir este gráfico.",
                 color=SECUNDARIO, fontsize=13)
    fig.savefig(pasta / "slide_04_receita_lucro.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)

    # 5 — Síntese objetiva, sem recomendação de investimento
    fig = _base("O que mostram os dados?", 5, "Resumo descritivo — não constitui recomendação de investimento.")
    fig.text(0.10, 0.62, "01", color=DESTAQUE, fontsize=15, weight="bold")
    fig.text(0.20, 0.62, f"Variação no período: {variacao:+.1f}%",
             color=TEXTO, fontsize=15, weight="bold")
    fig.text(0.10, 0.48, "02", color=DESTAQUE, fontsize=15, weight="bold")
    fig.text(0.20, 0.48, f"Último preço observado: {ultimo:,.2f} USD",
             color=TEXTO, fontsize=13, weight="bold")
    fig.text(0.10, 0.34, "03", color=DESTAQUE, fontsize=15, weight="bold")
    fig.text(0.20, 0.34, f"Histórico consultado até {data_final}",
             color=TEXTO, fontsize=13, weight="bold")
    fig.savefig(pasta / "slide_05_resumo.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)

    # 6 — Encerramento
    fig = _base("Investir começa por analisar.", 6,
                "Acompanhe os dados, compare períodos e forme a sua própria opinião.")
    fig.text(0.085, 0.56, f"{ticker}", color=DESTAQUE, fontsize=42, weight="bold")
    fig.text(0.085, 0.43, "Que indicador acompanharia a seguir?",
             color=TEXTO, fontsize=17, weight="bold")
    fig.text(0.085, 0.32, "Guarde este carrossel para consultar mais tarde.",
             color=SECUNDARIO, fontsize=11)
    fig.savefig(pasta / "slide_06_fecho.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)

    legenda = (
        f"{ticker} em análise: evolução do preço, volume negociado e indicadores financeiros.\n\n"
        f"Período consultado: {periodo}. Último dado de preço: {data_final}.\n"
        "Fonte: Yahoo Finance (via yfinance). Os dados podem ter atraso, alterações ou limitações.\n"
        "Conteúdo meramente informativo e educativo; não constitui aconselhamento financeiro "
        "nem recomendação de compra ou venda.\n\n"
        "#AMD #Semicondutores #MercadosFinanceiros #Investimento #AnáliseFinanceira"
    )
    (pasta / "legenda_instagram.txt").write_text(legenda, encoding="utf-8")
    LOG.info("Carrossel Instagram criado em %s", pasta)
