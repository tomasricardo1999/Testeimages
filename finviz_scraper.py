#!/usr/bin/env python3
"""Recolhe métricas fundamentais da página pública de cotação do Finviz.

Não contorna bloqueios, autenticação ou controlos anti-bot. Se o Finviz não
permitir a consulta, a análise histórica continua e as métricas ficam assinaladas
como indisponíveis.
"""
from __future__ import annotations

import csv
import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

LOG = logging.getLogger("finviz")

CAMPOS = {
    "Market Cap": "capitalizacao_mercado",
    "Enterprise Value": "enterprise_value",
    "P/E": "pe_trailing",
    "Forward P/E": "pe_forward",
    "PEG": "peg",
    "P/S": "ps",
    "P/B": "pb",
    "P/FCF": "p_fcf",
    "EV/EBITDA": "ev_ebitda",
    "EV/Sales": "ev_sales",
    "EPS (ttm)": "eps_ttm",
    "EPS next Y": "eps_proximo_ano",
    "EPS this Y": "crescimento_eps_ano_atual",
    "EPS next Y": "crescimento_eps_proximo_ano",
    "EPS next 5Y": "crescimento_eps_5_anos",
    "EPS Y/Y TTM": "crescimento_eps_ttm",
    "Sales Y/Y TTM": "crescimento_vendas_ttm",
    "Sales Q/Q": "crescimento_vendas_trimestre",
    "Gross Margin": "margem_bruta",
    "Oper. Margin": "margem_operacional",
    "Profit Margin": "margem_liquida",
    "ROA": "roa",
    "ROE": "roe",
    "ROIC": "roic",
    "Debt/Eq": "divida_capital_proprio",
    "LT Debt/Eq": "divida_longo_prazo_capital_proprio",
    "Current Ratio": "current_ratio",
    "Quick Ratio": "quick_ratio",
    "Payout": "payout",
    "Dividend TTM": "dividendo_ttm",
    "Short Float": "short_float",
    "Recom": "consenso_analistas",
    "Target Price": "preco_alvo_analistas",
    "Price": "preco",
    "52W High": "maximo_52_semanas",
    "52W Low": "minimo_52_semanas",
}

def _texto(celula: object) -> str:
    return re.sub(r"\\s+", " ", celula.get_text(" ", strip=True)).strip()

def _extrair_pares(soup: BeautifulSoup) -> dict[str, str]:
    encontrados: dict[str, str] = {}
    for linha in soup.find_all("tr"):
        celulas = linha.find_all(["td", "th"], recursive=False)
        textos = [_texto(c) for c in celulas]
        for i in range(0, len(textos) - 1, 2):
            chave, valor = textos[i], textos[i + 1]
            if chave in CAMPOS and valor and valor != "-":
                encontrados[CAMPOS[chave]] = valor
    return encontrados

def recolher_metricas(ticker: str, pasta_saida: Path) -> dict:
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}&p=d"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AMD-Financial-Dashboard/1.0; educational use)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }
    sessao = requests.Session()
    dados: dict[str, object] = {
        "ticker": ticker.upper(),
        "fonte": "Finviz",
        "url_fonte": url,
        "capturado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metricas": {},
        "estado": "indisponivel",
    }
    try:
        resposta = sessao.get(url, headers=headers, timeout=25)
        resposta.raise_for_status()
        if "captcha" in resposta.text.lower() or "access denied" in resposta.text.lower():
            raise RuntimeError("O Finviz não disponibilizou a página pública nesta execução.")
        soup = BeautifulSoup(resposta.text, "html.parser")
        metricas = _extrair_pares(soup)
        if not metricas:
            raise RuntimeError("A página foi recebida, mas não foi possível reconhecer a tabela de métricas.")
        dados["metricas"] = metricas
        dados["estado"] = "ok"
        LOG.info("Finviz: %s métricas recolhidas para %s.", len(metricas), ticker)
    except Exception as exc:
        dados["erro"] = str(exc)
        LOG.warning("Finviz indisponível (%s). O restante relatório continuará.", exc)
    finally:
        sessao.close()

    pasta_saida.mkdir(parents=True, exist_ok=True)
    (pasta_saida / f"{ticker.lower()}_finviz.json").write_text(
        json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if dados["metricas"]:
        with (pasta_saida / f"{ticker.lower()}_finviz.csv").open(
            "w", newline="", encoding="utf-8-sig"
        ) as ficheiro:
            writer = csv.writer(ficheiro)
            writer.writerow(["Indicador", "Valor", "Fonte", "Capturado em UTC"])
            for nome, valor in dados["metricas"].items():
                writer.writerow([nome, valor, "Finviz", dados["capturado_em_utc"]])
    return dados
