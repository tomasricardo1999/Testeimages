# AMD — análise financeira pronta para Google Colab
# Para usar: abre https://colab.research.google.com/ e cola este código numa célula.
# A primeira linha instala as bibliotecas necessárias.

%pip -q install yfinance pandas matplotlib

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from IPython.display import display

# Configuração
TICKER = "AMD"
PERIODO = "5y"       # exemplos: "1y", "2y", "5y", "max"
INTERVALO = "1d"     # exemplos: "1d", "1wk", "1mo"
PASTA = Path("dados_amd")
PASTA.mkdir(exist_ok=True)

amd = yf.Ticker(TICKER)

# 1. Preços históricos
precos = amd.history(period=PERIODO, interval=INTERVALO, auto_adjust=False)
if precos.empty:
    raise RuntimeError("Não foram encontrados preços. Confirma a ligação à internet e os parâmetros.")

display(precos.tail())
precos.to_csv(PASTA / "amd_historico.csv")

# Gráfico 1 — preço de fecho
plt.figure(figsize=(13, 5))
plt.plot(precos.index, precos["Close"], label="Fecho")
plt.title(f"{TICKER} — preço de fecho ({PERIODO})")
plt.xlabel("Data")
plt.ylabel("Preço (USD)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

# Gráfico 2 — volume negociado
if "Volume" in precos.columns:
    plt.figure(figsize=(13, 4))
    plt.plot(precos.index, precos["Volume"])
    plt.title(f"{TICKER} — volume negociado ({PERIODO})")
    plt.xlabel("Data")
    plt.ylabel("Volume")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

# 2. Demonstrações financeiras (dados anuais e trimestrais)
demonstracoes = {
    "resultados_anuais": amd.income_stmt,
    "resultados_trimestrais": amd.quarterly_income_stmt,
    "balanco_anual": amd.balance_sheet,
    "balanco_trimestral": amd.quarterly_balance_sheet,
    "fluxo_caixa_anual": amd.cashflow,
    "fluxo_caixa_trimestral": amd.quarterly_cashflow,
}

for nome, tabela in demonstracoes.items():
    if tabela is not None and not tabela.empty:
        tabela.to_csv(PASTA / f"amd_{nome}.csv")
        print(f"{nome}: {tabela.shape[0]} linhas × {tabela.shape[1]} períodos")
    else:
        print(f"{nome}: sem dados disponíveis")

# Gráfico 3 — receitas e lucro líquido, se esses indicadores existirem
resultados = amd.income_stmt
if resultados is not None and not resultados.empty:
    # As colunas são normalmente os períodos; as linhas, as métricas.
    linhas = {str(indice).lower(): indice for indice in resultados.index}
    receita_key = next((v for k, v in linhas.items() if "total revenue" in k or k == "revenue"), None)
    lucro_key = next((v for k, v in linhas.items() if "net income" in k), None)

    series = {}
    if receita_key is not None:
        series["Receita"] = pd.to_numeric(resultados.loc[receita_key], errors="coerce")
    if lucro_key is not None:
        series["Lucro líquido"] = pd.to_numeric(resultados.loc[lucro_key], errors="coerce")

    if series:
        financeiro = pd.DataFrame(series).sort_index()
        display(financeiro)
        financeiro.to_csv(PASTA / "amd_receita_lucro.csv")
        ax = financeiro.plot(kind="bar", figsize=(12, 5))
        ax.set_title(f"{TICKER} — receita e lucro líquido anual")
        ax.set_xlabel("Período")
        ax.set_ylabel("USD")
        ax.grid(axis="y", alpha=0.3)
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.show()
    else:
        print("Não foi possível identificar receita/lucro nas demonstrações disponíveis.")
else:
    print("Demonstração de resultados não disponível para criar o gráfico financeiro.")

# 3. Informação geral da empresa
try:
    info = amd.get_info()
    chaves = [
        "longName", "sector", "industry", "currency", "marketCap",
        "trailingPE", "forwardPE", "priceToBook", "profitMargins",
        "returnOnEquity", "dividendYield"
    ]
    resumo = {chave: info.get(chave) for chave in chaves if info.get(chave) is not None}
    display(pd.DataFrame(resumo.items(), columns=["Indicador", "Valor"]))
    pd.DataFrame(resumo.items(), columns=["Indicador", "Valor"]).to_csv(
        PASTA / "amd_resumo_empresa.csv", index=False
    )
except Exception as erro:
    print(f"Não foi possível obter os metadados da empresa: {erro}")

# 4. Descarregar resultados
print(f"\nFicheiros guardados na pasta: {PASTA.resolve()}")
print("No Colab, podes transferi-los com:")
print("from google.colab import files")
print("files.download('dados_amd/amd_historico.csv')")

# Nota: yfinance obtém dados do Yahoo Finance; a disponibilidade e o atraso variam.
# Este notebook é para análise informativa, não constitui aconselhamento financeiro.
