#!/usr/bin/env python3
"""Gera os seis primeiros slides de um carrossel financeiro ordenado."""
from __future__ import annotations
import logging
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

LOG=logging.getLogger("carrossel")
FUNDO="#101318"; PAINEL="#191f27"; TEXTO="#f3f5f7"; SECUNDARIO="#aab3bf"; DESTAQUE="#e21b2d"; VERDE="#55c49a"; CINZENTO="#596574"

def _base(ticker, titulo, numero, subtitulo, inicio, fim):
    fig=plt.figure(figsize=(8,10),facecolor=FUNDO)
    fig.text(.075,.94,"MERCADOS  /  ANÁLISE DE EMPRESA",color=DESTAQUE,fontsize=10,weight="bold")
    fig.text(.075,.875,titulo,color=TEXTO,fontsize=24,weight="bold",va="top",wrap=True)
    fig.text(.075,.79,subtitulo,color=SECUNDARIO,fontsize=10,va="top",wrap=True)
    fig.text(.075,.045,f"{ticker}  •  YAHOO FINANCE  •  PREÇOS: {inicio} A {fim}",color=SECUNDARIO,fontsize=6.8)
    fig.text(.925,.045,f"{numero:02d} / 11",color=DESTAQUE,fontsize=9,weight="bold",ha="right")
    return fig

def _eixo(ax):
    ax.set_facecolor(PAINEL); ax.tick_params(colors=SECUNDARIO,labelsize=8)
    for s in ax.spines.values(): s.set_color(CINZENTO)
    ax.grid(True,color=CINZENTO,alpha=.25,linewidth=.7)
    ax.xaxis.label.set_color(SECUNDARIO); ax.yaxis.label.set_color(SECUNDARIO)

def gerar_carrossel(ticker, precos, resultados, pasta:Path, periodo="5y"):
    pasta.mkdir(parents=True,exist_ok=True)
    if precos is None or precos.empty or "Close" not in precos: 
        LOG.warning("Sem preços para carrossel."); return
    close=pd.to_numeric(precos["Close"],errors="coerce").dropna()
    if close.empty: return
    datas=pd.DatetimeIndex(close.index)
    inicio=pd.Timestamp(datas[0]).strftime("%d/%m/%Y"); fim=pd.Timestamp(datas[-1]).strftime("%d/%m/%Y")
    # Adj Close incorpora ajustamentos por dividendos/splits quando fornecido pelo Yahoo.
    serie_ret=pd.to_numeric(precos["Adj Close"],errors="coerce").dropna() if "Adj Close" in precos else close
    serie_ret=serie_ret.reindex(close.index).dropna()
    p0=float(serie_ret.iloc[0]); p1=float(serie_ret.iloc[-1])
    ret=(p1/p0-1)*100 if p0 else float("nan")
    dias=(pd.Timestamp(serie_ret.index[-1])-pd.Timestamp(serie_ret.index[0])).days
    anos=dias/365.2425
    cagr=((p1/p0)**(1/anos)-1)*100 if p0>0 and p1>0 and anos>0 else float("nan")
    moeda="USD"
    # 01 capa
    fig=_base(ticker,f"{ticker}: análise em 11 slides",1,"Mercado, desempenho histórico e fundamentos",inicio,fim)
    fig.text(.085,.61,"PERÍODO ANALISADO",color=SECUNDARIO,fontsize=10,weight="bold")
    fig.text(.085,.54,f"{inicio} — {fim}",color=TEXTO,fontsize=19,weight="bold")
    fig.text(.085,.39,"Retorno acumulado",color=SECUNDARIO,fontsize=11)
    fig.text(.085,.30,f"{ret:+.1f}%",color=VERDE if ret>=0 else DESTAQUE,fontsize=39,weight="bold")
    fig.text(.085,.21,f"Retorno anualizado (CAGR): {cagr:+.1f}% ao ano" if anos>=1 else "Período inferior a 1 ano: CAGR omitido",color=TEXTO,fontsize=11)
    fig.savefig(pasta/"slide_01_capa.png",dpi=135,facecolor=FUNDO); plt.close(fig)
    # 02 retorno e datas
    fig=_base(ticker,"Quanto rendeu no período?",2,"Retorno calculado com Adj Close quando disponível (ajustado); caso contrário, Close.",inicio,fim)
    fig.text(.10,.62,"VALOR INICIAL",color=SECUNDARIO,fontsize=9,weight="bold")
    fig.text(.10,.56,f"{p0:,.2f} USD  •  {pd.Timestamp(serie_ret.index[0]).strftime('%d/%m/%Y')}",color=TEXTO,fontsize=15,weight="bold")
    fig.text(.10,.42,"VALOR FINAL",color=SECUNDARIO,fontsize=9,weight="bold")
    fig.text(.10,.36,f"{p1:,.2f} USD  •  {pd.Timestamp(serie_ret.index[-1]).strftime('%d/%m/%Y')}",color=TEXTO,fontsize=15,weight="bold")
    fig.text(.10,.20,f"Retorno acumulado: {ret:+.2f}%",color=VERDE if ret>=0 else DESTAQUE,fontsize=18,weight="bold")
    if anos>=1: fig.text(.10,.13,f"CAGR ({inicio}–{fim}; {anos:.2f} anos): {cagr:+.2f}%/ano",color=SECUNDARIO,fontsize=10)
    fig.savefig(pasta/"slide_02_retorno_periodo.png",dpi=135,facecolor=FUNDO); plt.close(fig)
    # 03 preço
    fig=_base(ticker,"Evolução da cotação",3,"Preço de fecho não ajustado (Close); intervalo de observações indicado no rodapé.",inicio,fim)
    ax=fig.add_axes([.10,.24,.82,.44]); _eixo(ax)
    ax.plot(close.index,close.values,color=DESTAQUE,lw=2); ax.set_ylabel("Preço de fecho (USD)")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator()); ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    fig.text(.10,.15,f"Primeira sessão: {inicio}  |  Última sessão: {fim}",color=TEXTO,fontsize=10)
    fig.savefig(pasta/"slide_03_preco.png",dpi=135,facecolor=FUNDO); plt.close(fig)
    # 04 retornos por ano civil
    fig=_base(ticker,"Retornos por ano civil",4,"Variação entre o primeiro e o último fecho disponível em cada ano civil; não é média anual.",inicio,fim)
    anual=serie_ret.groupby(serie_ret.index.year).agg(["first","last"])
    anual["retorno"]=(anual["last"]/anual["first"]-1)*100
    ax=fig.add_axes([.12,.28,.78,.40]); _eixo(ax)
    cores=[VERDE if v>=0 else DESTAQUE for v in anual["retorno"]]
    ax.bar([str(y) for y in anual.index],anual["retorno"],color=cores)
    ax.axhline(0,color=SECUNDARIO,lw=.8); ax.set_ylabel("Retorno no ano (%)")
    for i,v in enumerate(anual["retorno"]): ax.text(i,v+(1 if v>=0 else -1),f"{v:+.1f}%",ha="center",va="bottom" if v>=0 else "top",color=TEXTO,fontsize=8)
    fig.text(.10,.16,"Anos incompletos no início/fim do intervalo usam apenas sessões disponíveis.",color=SECUNDARIO,fontsize=8)
    fig.savefig(pasta/"slide_04_retornos_anuais.png",dpi=135,facecolor=FUNDO); plt.close(fig)
    # 05 volume
    fig=_base(ticker,"Volume negociado",5,"Número de ações transacionadas por sessão; período integral no rodapé.",inicio,fim)
    if "Volume" in precos:
        vol=pd.to_numeric(precos["Volume"],errors="coerce").dropna()
        ax=fig.add_axes([.10,.25,.82,.43]); _eixo(ax); ax.bar(vol.index,vol.values,color=DESTAQUE,width=1)
        ax.set_ylabel("Ações por sessão")
        fig.text(.10,.16,f"Mediana por sessão: {vol.median():,.0f} ações",color=TEXTO,fontsize=12,weight="bold")
    else: fig.text(.10,.48,"Volume indisponível.",color=SECUNDARIO,fontsize=14)
    fig.savefig(pasta/"slide_05_volume.png",dpi=135,facecolor=FUNDO); plt.close(fig)
    # 06 resultados anuais
    fig=_base(ticker,"Receita e lucro reportados",6,"Demonstração anual: cada coluna representa um exercício fiscal (não uma data diária).",inicio,fim)
    fin=pd.DataFrame()
    if resultados is not None and not resultados.empty:
        idx={str(i).lower():i for i in resultados.index}
        rk=next((v for k,v in idx.items() if "total revenue" in k or k=="revenue"),None)
        lk=next((v for k,v in idx.items() if "net income" in k),None)
        if rk is not None: fin["Receita"]=pd.to_numeric(resultados.loc[rk],errors="coerce")
        if lk is not None: fin["Lucro líquido"]=pd.to_numeric(resultados.loc[lk],errors="coerce")
        fin=fin.dropna(how="all").sort_index()
    if not fin.empty:
        ax=fig.add_axes([.10,.25,.82,.43]); _eixo(ax)
        fin.plot(kind="bar",ax=ax,color=[DESTAQUE,VERDE][:len(fin.columns)])
        ax.set_ylabel("Valor reportado (USD)"); ax.set_xlabel("Fim do exercício fiscal")
        ax.tick_params(axis="x",rotation=20); ax.legend(facecolor=PAINEL,labelcolor=TEXTO,fontsize=8)
        fig.text(.10,.15,"A data no eixo corresponde ao período fiscal reportado pelo Yahoo Finance.",color=SECUNDARIO,fontsize=8)
    else: fig.text(.10,.48,"Demonstração anual indisponível.",color=SECUNDARIO,fontsize=14)
    fig.savefig(pasta/"slide_06_receita_lucro.png",dpi=135,facecolor=FUNDO); plt.close(fig)
    legenda=(f"{ticker} | período de mercado: {inicio} a {fim}. Retorno acumulado: {ret:+.2f}%. "+
             (f"CAGR: {cagr:+.2f}%/ano. " if anos>=1 else "")+
             "Retornos anuais calculados por ano civil, com sessões disponíveis. "+
             "Preço via Yahoo Finance/yfinance; Adj Close usado para retorno quando disponível. "+
             "Demonstrações anuais referem-se aos exercícios fiscais indicados nos dados. "+
             "Conteúdo informativo, não constitui aconselhamento financeiro. "+
             "#AMD #Semicondutores #MercadosFinanceiros #AnáliseFinanceira")
    (pasta/"legenda_instagram.txt").write_text(legenda,encoding="utf-8")
    LOG.info("Slides históricos 01-06 gerados (%s a %s).",inicio,fim)
