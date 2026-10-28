#!/usr/bin/env python3
"""
Extrai dados financeiros da Advanced Micro Devices (AMD) via yfinance.

Instalação:
    python -m pip install -r requirements.txt

Exemplos:
    python amd_financas.py
    python amd_financas.py --periodo 5y --intervalo 1mo
    python amd_financas.py --ticker AMD --saida dados_amd

Os dados são obtidos do Yahoo Finance através de yfinance; podem sofrer
atrasos, alterações de disponibilidade ou limitações do serviço. Uso para
pesquisa/análise, não como aconselhamento financeiro.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

LOG = logging.getLogger("amd_financas")


def json_seguro(value: Any) -> Any:
    """Converte valores comuns de pandas/numpy para JSON serializável."""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    if pd.isna(value):
        return None
    return str(value)


def guardar_dataframe(df: pd.DataFrame, caminho: Path) -> bool:
    """Guarda um DataFrame em CSV; devolve False se estiver vazio."""
    if df is None or df.empty:
        LOG.warning("Sem dados para %s; ficheiro não criado.", caminho.name)
        return False
    df.to_csv(caminho, encoding="utf-8-sig")
    LOG.info("Guardado: %s", caminho)
    return True


def extrair(ticker: str, periodo: str, intervalo: str, saida: Path) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    empresa = yf.Ticker(ticker)

    # Preços históricos e volume.
    historico = empresa.history(
        period=periodo,
        interval=intervalo,
        auto_adjust=False,
        actions=True,
    )
    guardar_dataframe(historico, saida / f"{ticker.lower()}_historico.csv")

    # Demonstrações financeiras anuais e trimestrais.
    tabelas = {
        "resultados_anuais": empresa.income_stmt,
        "resultados_trimestrais": empresa.quarterly_income_stmt,
        "balanco_anual": empresa.balance_sheet,
        "balanco_trimestral": empresa.quarterly_balance_sheet,
        "fluxo_caixa_anual": empresa.cashflow,
        "fluxo_caixa_trimestral": empresa.quarterly_cashflow,
    }
    for nome, tabela in tabelas.items():
        guardar_dataframe(tabela, saida / f"{ticker.lower()}_{nome}.csv")

    # Metadados: manter apenas campos simples para evitar JSON problemático.
    try:
        info = empresa.get_info()
        info_simples = {
            str(chave): json_seguro(valor)
            for chave, valor in info.items()
            if valor is None or isinstance(
                valor, (str, int, float, bool, pd.Timestamp)
            )
        }
        with (saida / f"{ticker.lower()}_empresa.json").open(
            "w", encoding="utf-8"
        ) as ficheiro:
            json.dump(info_simples, ficheiro, ensure_ascii=False, indent=2)
        LOG.info("Guardado: %s", saida / f"{ticker.lower()}_empresa.json")
    except Exception as exc:
        LOG.warning("Não foi possível obter os metadados da empresa: %s", exc)

    # Dividendos e desdobramentos (quando disponíveis).
    guardar_dataframe(
        empresa.dividends.to_frame("dividendos"),
        saida / f"{ticker.lower()}_dividendos.csv",
    )
    guardar_dataframe(
        empresa.splits.to_frame("desdobramentos"),
        saida / f"{ticker.lower()}_desdobramentos.csv",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extrai preços e demonstrações financeiras de uma ação."
    )
    parser.add_argument("--ticker", default="AMD", help="Símbolo Yahoo Finance (default: AMD)")
    parser.add_argument("--periodo", default="5y", help="Período histórico, ex.: 1y, 5y, max")
    parser.add_argument(
        "--intervalo",
        default="1d",
        choices=["1d", "5d", "1wk", "1mo", "3mo"],
        help="Intervalo dos preços históricos (default: 1d)",
    )
    parser.add_argument(
        "--saida", default="dados_financeiros", help="Diretório dos ficheiros de saída"
    )
    parser.add_argument("--verbose", action="store_true", help="Mostrar mensagens de diagnóstico")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )
    try:
        extrair(args.ticker.upper(), args.periodo, args.intervalo, Path(args.saida))
    except Exception as exc:
        LOG.error("Falha ao extrair dados de %s: %s", args.ticker.upper(), exc)
        return 1
    print(f"Extração concluída. Verifica a pasta: {args.saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
