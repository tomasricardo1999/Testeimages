#!/usr/bin/env python3
"""Cria cinco slides 4:5 adicionais com métricas fundamentais do Finviz."""
from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LOG = logging.getLogger("carrossel_finviz")
FUNDO = "#101318"
PAINEL = "#191f27"
TEXTO = "#f3f5f7"
SECUNDARIO = "#aab3bf"
DESTAQUE = "#e21b2d"
VERDE = "#55c49a"

def _base(ticker: str, numero: int, titulo: str, subtitulo: str, data: str):
    fig = plt.figure(figsize=(8, 10), facecolor=FUNDO)
    fig.text(.075, .94, "MERCADOS  /  ANÁLISE FUNDAMENTAL", color=DESTAQUE,
             fontsize=10, weight="bold")
    fig.text(.075, .865, titulo, color=TEXTO, fontsize=24, weight="bold", va="top", wrap=True)
    fig.text(.075, .77, subtitulo, color=SECUNDARIO, fontsize=10, va="top", wrap=True)
    fig.text(.075, .045, f"{ticker}  •  FINVIZ  •  SNAPSHOT: {data} UTC",
             color=SECUNDARIO, fontsize=7)
    fig.text(.925, .045, f"{numero:02d} / 11", color=DESTAQUE,
             fontsize=9, weight="bold", ha="right")
    return fig

def _cartoes(fig, linhas):
    y = .66
    for rotulo, valor, nota in linhas:
        fig.text(.09, y, rotulo.upper(), color=SECUNDARIO, fontsize=8.5, weight="bold")
        fig.text(.09, y-.06, valor, color=TEXTO, fontsize=22, weight="bold")
        if nota:
            fig.text(.09, y-.10, nota, color=SECUNDARIO, fontsize=8)
        y -= .155

def gerar_carrossel_finviz(ticker: str, dados: dict, pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    m = dados.get("metricas", {}) if dados else {}
    ok = dados.get("estado") == "ok" and bool(m)
    capturado = str(dados.get("capturado_em_utc", "sem dados"))
    fonte = "Métricas recolhidas do Finviz" if ok else "Finviz indisponível nesta execução; métricas não apresentadas"
    grupos = [
        (("Dividendos e distribuição" if ticker.upper()=="MAIN" else "Avaliação bolsista"), ([
            ("Dividendos TTM", "dividendo_ttm", "Montante por ação reportado pelo Finviz; snapshot, não previsão"),
            ("Payout", "payout", "Definição/metodologia do fornecedor; não substitui cobertura por NII"),
            ("P/E (TTM)", "pe_trailing", "Múltiplo de avaliação no snapshot"),
            ("Dividend yield", "dividend_yield", "Yield do snapshot; pode variar com preço e dividendos"),
        ] if ticker.upper()=="MAIN" else [

            ("P/E (TTM)", "pe_trailing", "Preço do snapshot face ao EPS dos últimos 12 meses"),
            ("Forward P/E", "pe_forward", "Preço do snapshot face ao EPS estimado para o próximo exercício"),
            ("PEG", "peg", "Múltiplo de avaliação face ao crescimento esperado; snapshot"),
            ("P/S  •  P/B", None, "P/S usa vendas TTM; P/B usa valor contabilístico do último balanço; snapshot"),
        ])),
        ("Crescimento", [
            ("Crescimento EPS (ano atual)", "crescimento_eps_ano_atual", "Estimativa para o exercício corrente; snapshot Finviz"),
            ("Crescimento EPS (próximo ano)", "crescimento_eps_proximo_ano", "Estimativa para o exercício seguinte; snapshot Finviz"),
            ("Crescimento EPS (5 anos)", "crescimento_eps_5_anos", "Estimativa anualizada para os próximos 5 anos; snapshot Finviz"),
            ("Vendas Y/Y (TTM)", "crescimento_vendas_ttm", "Últimos 12 meses face aos 12 meses anteriores; snapshot Finviz"),
        ]),
        ("Rentabilidade", [
            ("Margem bruta", "margem_bruta", "TTM / últimos 12 meses; snapshot Finviz"),
            ("Margem operacional", "margem_operacional", "TTM / últimos 12 meses; snapshot Finviz"),
            ("Margem líquida", "margem_liquida", "TTM / últimos 12 meses; snapshot Finviz"),
            ("ROE  •  ROA  •  ROIC", None, "Retornos sobre capital próprio, ativos e capital investido; TTM / snapshot Finviz"),
        ]),
        ("Balanço e risco", [
            ("Debt / Equity", "divida_capital_proprio", "Último balanço disponível; Finviz não fornece aqui a data exata do balanço"),
            ("Current Ratio", "current_ratio", "Último balanço disponível; data-base exata não exposta pelo Finviz"),
            ("Quick Ratio", "quick_ratio", "Último balanço disponível; data-base exata não exposta pelo Finviz"),
            ("EV / EBITDA", "ev_ebitda", "Múltiplo de avaliação no snapshot Finviz; EBITDA TTM"),
        ]),
    ]

    if ticker.upper()=="MAIN":
        grupos = grupos[:1] + grupos[1:]
    for idx, (titulo, itens) in enumerate(grupos, start=1):
        fig = _base(ticker, idx + 6, titulo, fonte + f" | Snapshot: {capturado} UTC", capturado)
        linhas = []
        for label, key, nota in itens:
            if key:
                valor = m.get(key, "N/D")
            elif label == "P/S  •  P/B":
                valor = f'{m.get("ps", "N/D")}  •  {m.get("pb", "N/D")}'
            else:
                valor = f'ROE {m.get("roe", "N/D")}  |  ROA {m.get("roa", "N/D")}  |  ROIC {m.get("roic", "N/D")}'
            linhas.append((label, str(valor), nota))
        _cartoes(fig, linhas)
        fig.savefig(pasta / f"slide_{idx + 6:02d}_finviz.png", dpi=135, facecolor=FUNDO)
        plt.close(fig)

    fig = _base(ticker, 11, "Conclusão: olhar o conjunto", fonte + f" | Snapshot: {capturado} UTC", capturado)
    if ok:
        resumo = [
            ("Preço / lucro", f'P/E {m.get("pe_trailing", "N/D")}  |  Forward {m.get("pe_forward", "N/D")}', "Múltiplos diferentes: histórico vs. estimativa"),
            ("Crescimento", f'EPS 5Y {m.get("crescimento_eps_5_anos", "N/D")}', "Expectativas não são resultados garantidos"),
            ("Rentabilidade", f'Margem operacional {m.get("margem_operacional", "N/D")}', "Avaliar em conjunto com a margem líquida"),
            ("Endividamento", f'Debt/Equity {m.get("divida_capital_proprio", "N/D")}', "Comparar com empresas do mesmo setor"),
        ]
        # Layout compacto próprio: evita que a quarta métrica colida com a nota metodológica.
        y = .66
        for rotulo, valor, nota in resumo:
            fig.text(.09, y, rotulo.upper(), color=SECUNDARIO, fontsize=8, weight="bold")
            fig.text(.09, y-.042, valor, color=TEXTO, fontsize=16.5, weight="bold")
            fig.text(.09, y-.073, nota, color=SECUNDARIO, fontsize=7)
            y -= .15
    else:
        fig.text(.09, .55, "Os dados do Finviz não foram obtidos.", color=TEXTO, fontsize=17, weight="bold")
        fig.text(.09, .45, "O carrossel mantém os slides históricos; esta secção será preenchida numa execução futura.",
                 color=SECUNDARIO, fontsize=11, wrap=True)
    fig.text(.09, .105, "Snapshot: preço e múltiplos na data/hora acima; rácios de balanço no último balanço disponível (data exata não indicada pelo Finviz). Indicadores descritivos, não uma recomendação.",
             color=SECUNDARIO, fontsize=7, wrap=True)
    fig.savefig(pasta / "slide_11_conclusao.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)
    LOG.info("Cinco slides fundamentais guardados em %s", pasta)
