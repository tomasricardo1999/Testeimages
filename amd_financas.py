#!/usr/bin/env python3
"""
Análise financeira da AMD com gráficos guardados no próprio repositório.

Instalação:
    python -m pip install -r requirements.txt

Execução:
    python amd_financas.py
    python amd_financas.py --ticker NVDA --periodo 5y

Os dados são obtidos via yfinance (Yahoo Finance) e podem sofrer atrasos
ou alterações de disponibilidade. Uso informativo, não é aconselhamento financeiro.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import pandas as pd
import yfinance as yf

from gerar_carrossel import gerar_carrossel

LOG = logging.getLogger("analise_financeira")


def guardar_grafico(fig, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=160, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    LOG.info("Gráfico guardado: %s", caminho)


def gerar_graficos(ticker: str, periodo: str, precos: pd.DataFrame,
                    resultados: pd.DataFrame, pasta_graficos: Path) -> None:
    import matplotlib.pyplot as plt

    if precos is not None and not precos.empty:
        fig, ax = plt.subplots(figsize=(13, 5))
        ax.plot(precos.index, precos["Close"], label="Preço de fecho", color="#e21b2d")
        ax.set(title=f"{ticker} — preço de fecho ({periodo})",
               xlabel="Data", ylabel="Preço (USD)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        guardar_grafico(fig, pasta_graficos / f"{ticker.lower()}_preco_fecho.png")

        if "Volume" in precos.columns:
            fig, ax = plt.subplots(figsize=(13, 4))
            ax.bar(precos.index, precos["Volume"], width=1.0, color="#e21b2d")
            ax.set(title=f"{ticker} — volume negociado ({periodo})",
                   xlabel="Data", ylabel="Volume")
            ax.grid(True, axis="y", alpha=0.3)
            fig.tight_layout()
            guardar_grafico(fig, pasta_graficos / f"{ticker.lower()}_volume.png")

    if resultados is None or resultados.empty:
        LOG.warning("Sem demonstração de resultados para gerar o gráfico financeiro.")
        return

    linhas = {str(indice).strip().lower(): indice for indice in resultados.index}
    receita_key = next(
        (v for k, v in linhas.items() if "total revenue" in k or k == "revenue"), None
    )
    lucro_key = next((v for k, v in linhas.items() if "net income" in k), None)

    series = {}
    if receita_key is not None:
        series["Receita"] = pd.to_numeric(resultados.loc[receita_key], errors="coerce")
    if lucro_key is not None:
        series["Lucro líquido"] = pd.to_numeric(resultados.loc[lucro_key], errors="coerce")

    if not series:
        LOG.warning("Não foram encontradas linhas de receita ou lucro líquido.")
        return

    financeiro = pd.DataFrame(series).sort_index().dropna(how="all")
    financeiro.to_csv(pasta_graficos.parent / f"{ticker.lower()}_receita_lucro.csv")

    fig, ax1 = plt.subplots(figsize=(12, 5))
    if "Receita" in financeiro:
        ax1.plot(financeiro.index, financeiro["Receita"], marker="o",
                 label="Receita", linewidth=2, color="#e21b2d")
        ax1.set_ylabel("Receita (USD)")
    ax1.set_xlabel("Período")
    ax1.set_title(f"{ticker} — evolução anual da receita e do lucro líquido")
    ax1.grid(True, alpha=0.3)
    if "Lucro líquido" in financeiro:
        ax2 = ax1.twinx()
        ax2.plot(financeiro.index, financeiro["Lucro líquido"], marker="s",
                 label="Lucro líquido", linewidth=2, color="#55c49a")
        ax2.set_ylabel("Lucro líquido (USD)")
        linhas_grafico = ax1.get_lines() + ax2.get_lines()
    else:
        linhas_grafico = ax1.get_lines()
    ax1.legend(linhas_grafico, [linha.get_label() for linha in linhas_grafico],
               loc="best")
    fig.autofmt_xdate()
    fig.tight_layout()
    guardar_grafico(fig, pasta_graficos / f"{ticker.lower()}_receita_lucro.png")


def main() -> int:
    parser = argparse.ArgumentParser(description="Análise financeira e gráficos em PNG.")
    parser.add_argument("--ticker", default="AMD", help="Símbolo Yahoo Finance (default: AMD)")
    parser.add_argument("--periodo", default="5y", help="Período histórico (ex.: 1y, 5y, max)")
    parser.add_argument("--intervalo", default="1d",
                        choices=["1d", "5d", "1wk", "1mo", "3mo"])
    parser.add_argument("--saida", default="dados_amd", help="Pasta para CSVs e gráficos")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    ticker = args.ticker.upper()
    saida = Path(args.saida)
    pasta_graficos = saida / "graficos"
    pasta_graficos.mkdir(parents=True, exist_ok=True)
    saida.mkdir(parents=True, exist_ok=True)

    empresa = yf.Ticker(ticker)
    precos = empresa.history(period=args.periodo, interval=args.intervalo,
                             auto_adjust=False, actions=True)
    if precos.empty:
        LOG.error("Não foram encontrados preços para %s.", ticker)
        return 1
    precos.to_csv(saida / f"{ticker.lower()}_historico.csv", encoding="utf-8-sig")

    demonstracoes = {
        "resultados_anuais": empresa.income_stmt,
        "resultados_trimestrais": empresa.quarterly_income_stmt,
        "balanco_anual": empresa.balance_sheet,
        "balanco_trimestral": empresa.quarterly_balance_sheet,
        "fluxo_caixa_anual": empresa.cashflow,
        "fluxo_caixa_trimestral": empresa.quarterly_cashflow,
    }
    for nome, tabela in demonstracoes.items():
        if tabela is not None and not tabela.empty:
            tabela.to_csv(saida / f"{ticker.lower()}_{nome}.csv",
                          encoding="utf-8-sig")
            LOG.info("%s: %s linhas × %s períodos", nome, *tabela.shape)
        else:
            LOG.warning("%s: sem dados disponíveis", nome)

    gerar_graficos(ticker, args.periodo, precos,
                   demonstracoes["resultados_anuais"], pasta_graficos)
    gerar_carrossel(ticker, precos, demonstracoes["resultados_anuais"],
                    saida / "instagram", args.periodo)

    try:
        info = empresa.get_info()
        chaves = ["longName", "sector", "industry", "currency", "marketCap",
                  "trailingPE", "forwardPE", "priceToBook", "profitMargins",
                  "returnOnEquity", "dividendYield"]
        resumo = {chave: info.get(chave) for chave in chaves
                  if info.get(chave) is not None}
        pd.DataFrame(resumo.items(), columns=["Indicador", "Valor"]).to_csv(
            saida / f"{ticker.lower()}_resumo_empresa.csv",
            index=False, encoding="utf-8-sig")
    except Exception as exc:
        LOG.warning("Não foi possível obter os metadados da empresa: %s", exc)

    LOG.info("Concluído. Gráficos: %s | Carrossel: %s",
             pasta_graficos.resolve(), (saida / "instagram").resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
