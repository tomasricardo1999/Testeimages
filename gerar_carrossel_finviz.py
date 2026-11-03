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
    fig.text(.075, .045, f"{ticker}  •  FINVIZ  •  CAPTURA: {data}",
             color=SECUNDARIO, fontsize=7)
    fig.text(.925, .045, f"{numero:02d} / 05", color=DESTAQUE,
             fontsize=9, weight="bold", ha="right")
    return fig

def _cartoes(fig, linhas):
    y = .65
    for rotulo, valor, nota in linhas:
        fig.text(.09, y, rotulo.upper(), color=SECUNDARIO, fontsize=9, weight="bold")
        fig.text(.09, y-.075, valor, color=TEXTO, fontsize=25, weight="bold")
        if nota:
            fig.text(.09, y-.12, nota, color=SECUNDARIO, fontsize=9)
        y -= .205

def gerar_carrossel_finviz(ticker: str, dados: dict, pasta: Path) -> None:
    pasta.mkdir(parents=True, exist_ok=True)
    m = dados.get("metricas", {}) if dados else {}
    ok = dados.get("estado") == "ok" and bool(m)
    capturado = str(dados.get("capturado_em_utc", "sem dados"))[:10]
    fonte = "Métricas recolhidas do Finviz" if ok else "Finviz indisponível nesta execução; métricas não apresentadas"
    grupos = [
        ("Avaliação bolsista", [
            ("P/E (últimos 12 meses)", "pe_trailing", "Preço face ao lucro histórico"),
            ("Forward P/E", "pe_forward", "Preço face ao lucro estimado"),
            ("PEG", "peg", "Avaliação ajustada ao crescimento esperado"),
            ("P/S  •  P/B", None, "Múltiplos de vendas e valor contabilístico"),
        ]),
        ("Crescimento", [
            ("Crescimento EPS (ano atual)", "crescimento_eps_ano_atual", "Variação estimada do lucro por ação"),
            ("Crescimento EPS (próximo ano)", "crescimento_eps_proximo_ano", "Estimativa para o próximo exercício"),
            ("Crescimento EPS (5 anos)", "crescimento_eps_5_anos", "Projeção anualizada de longo prazo"),
            ("Vendas Y/Y (TTM)", "crescimento_vendas_ttm", "Crescimento das vendas nos últimos 12 meses"),
        ]),
        ("Rentabilidade", [
            ("Margem bruta", "margem_bruta", "Percentagem das vendas após custo direto"),
            ("Margem operacional", "margem_operacional", "Resultado operacional sobre vendas"),
            ("Margem líquida", "margem_liquida", "Lucro líquido sobre vendas"),
            ("ROE  •  ROA  •  ROIC", None, "Retorno sobre capital próprio, ativos e capital investido"),
        ]),
        ("Balanço e risco", [
            ("Debt / Equity", "divida_capital_proprio", "Dívida face ao capital próprio"),
            ("Current Ratio", "current_ratio", "Capacidade de cobrir obrigações correntes"),
            ("Quick Ratio", "quick_ratio", "Liquidez sem depender de inventário"),
            ("EV / EBITDA", "ev_ebitda", "Valor da empresa face ao EBITDA"),
        ]),
    ]

    for idx, (titulo, itens) in enumerate(grupos, start=1):
        fig = _base(ticker, idx, titulo, fonte, capturado)
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
        fig.savefig(pasta / f"finviz_slide_{idx:02d}.png", dpi=135, facecolor=FUNDO)
        plt.close(fig)

    fig = _base(ticker, 5, "O que fica desta análise?", fonte, capturado)
    if ok:
        resumo = [
            ("Preço / lucro", f'P/E {m.get("pe_trailing", "N/D")}  |  Forward {m.get("pe_forward", "N/D")}', "Múltiplos diferentes: histórico vs. estimativa"),
            ("Crescimento", f'EPS 5Y {m.get("crescimento_eps_5_anos", "N/D")}', "Expectativas não são resultados garantidos"),
            ("Rentabilidade", f'Margem operacional {m.get("margem_operacional", "N/D")}', "Avaliar em conjunto com a margem líquida"),
            ("Endividamento", f'Debt/Equity {m.get("divida_capital_proprio", "N/D")}', "Comparar com empresas do mesmo setor"),
        ]
        _cartoes(fig, resumo)
    else:
        fig.text(.09, .55, "Os dados do Finviz não foram obtidos.", color=TEXTO, fontsize=17, weight="bold")
        fig.text(.09, .45, "O carrossel mantém os slides históricos; esta secção será preenchida numa execução futura.",
                 color=SECUNDARIO, fontsize=11, wrap=True)
    fig.text(.09, .13, "Indicadores descritivos, não uma recomendação de compra ou venda.",
             color=SECUNDARIO, fontsize=9, wrap=True)
    fig.savefig(pasta / "finviz_slide_05.png", dpi=135, facecolor=FUNDO)
    plt.close(fig)

    legenda = (
        f"{ticker}: análise fundamentalista complementar com métricas do Finviz.\\n\\n"
        f"Captura dos dados: {capturado} (UTC). Fonte: Finviz — {dados.get('url_fonte', 'https://finviz.com')}.\\n"
        "P/E, Forward P/E e PEG dependem de resultados históricos e estimativas; "
        "as previsões podem mudar. Compare sempre empresas do mesmo setor.\\n"
        "Conteúdo educativo, não constitui aconselhamento financeiro."
    )
    (pasta / "legenda_finviz_instagram.txt").write_text(legenda, encoding="utf-8")
    LOG.info("Cinco slides fundamentais guardados em %s", pasta)
