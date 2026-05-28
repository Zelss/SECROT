import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sector Rotation Dashboard", layout="wide")

SPY = "SPY"

SECTORS = {
    "Technology": "XLK",
    "Semiconductors": "SMH",
    "Financials": "XLF",
    "Energy": "XLE",
    "Healthcare": "XLV",
    "Industrials": "XLI",
    "Consumer": "XLY",
}

LEADERS = {
    "Technology": ["MSFT", "AAPL", "NVDA"],
    "Semiconductors": ["NVDA", "AMD", "AVGO"],
    "Financials": ["JPM", "BAC", "GS"],
    "Energy": ["XOM", "CVX"],
    "Healthcare": ["UNH", "LLY"],
    "Industrials": ["CAT", "BA"],
    "Consumer": ["AMZN", "TSLA", "HD"],
}

@st.cache_data
def get_data(ticker, period="6mo"):
    return yf.download(ticker, period=period)["Close"]

def rs_score(sector, spy):
    return (sector.iloc[-1] / sector.mean()) / (spy.iloc[-1] / spy.mean()) * 100

def momentum(series):
    return (series.iloc[-1] / series.iloc[-10] - 1) * 100

def leadership(stocks):
    scores = []
    for s in stocks:
        try:
            data = get_data(s)
            scores.append(data.iloc[-1] / data.mean())
        except:
            pass
    return np.mean(scores) * 100 if scores else 0

spy = get_data(SPY)

results = []

for name, etf in SECTORS.items():

    sector = get_data(etf)

    rs = rs_score(sector, spy)
    mom = momentum(sector)
    lead = leadership(LEADERS[name])

    score = (0.4 * rs) + (0.3 * mom) + (0.3 * lead)

    results.append([name, etf, score, rs, mom, lead])

df = pd.DataFrame(results, columns=[
    "Sector", "ETF", "Rotation Score", "RS", "Momentum", "Leadership"
])

df = df.sort_values("Rotation Score", ascending=False)

st.title("📊 Sector Rotation Dashboard (Cloud MVP)")

st.dataframe(df, use_container_width=True)

st.subheader("🔥 Top Rotating Sectors")
st.write(df.head(3))

st.subheader("⚠️ Weakest Sectors")
st.write(df.tail(2))
