import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Sector Rotation Engine V3", layout="wide")

SPY = "SPY"

# -----------------------------
# REALISTIC SECTOR HOLDINGS (TOP DRIVERS)
# -----------------------------

SECTORS = {
    "Technology (XLK)": {
        "etf": "XLK",
        "stocks": ["MSFT", "AAPL", "NVDA", "AVGO", "ORCL", "ACN"]
    },
    "Semiconductors (SMH)": {
        "etf": "SMH",
        "stocks": ["NVDA", "AMD", "AVGO", "INTC", "TSM", "QCOM"]
    },
    "Financials (XLF)": {
        "etf": "XLF",
        "stocks": ["JPM", "BAC", "GS", "MS", "C", "WFC"]
    },
    "Energy (XLE)": {
        "etf": "XLE",
        "stocks": ["XOM", "CVX", "COP", "EOG", "SLB"]
    },
    "Healthcare (XLV)": {
        "etf": "XLV",
        "stocks": ["UNH", "LLY", "JNJ", "PFE", "ABBV"]
    },
}

# -----------------------------
# DATA
# -----------------------------

@st.cache_data
def get_price(ticker, period="6mo"):
    data = yf.download(ticker, period=period, progress=False)
    if data is None or data.empty:
        return None
    return data["Close"].dropna()

# -----------------------------
# CORE METRICS
# -----------------------------

def rs(sector, spy):
    return (sector.iloc[-1] / sector.mean()) / (spy.iloc[-1] / spy.mean()) * 100

def momentum(series):
    if len(series) < 10:
        return 0
    return (series.iloc[-1] / series.iloc[-10] - 1) * 100

def breadth(stock_list):
    above20 = 0
    above50 = 0
    valid = 0

    for s in stock_list:
        data = get_price(s)
        if data is None or len(data) < 60:
            continue

        ma20 = data.rolling(20).mean()
        ma50 = data.rolling(50).mean()

        if data.iloc[-1] > ma20.iloc[-1]:
            above20 += 1
        if data.iloc[-1] > ma50.iloc[-1]:
            above50 += 1

        valid += 1

    if valid == 0:
        return 0, 0

    return (above20 / valid) * 100, (above50 / valid) * 100

def leadership(stock_list):
    scores = []
    for s in stock_list:
        data = get_price(s)
        if data is None:
            continue
        scores.append(data.iloc[-1] / data.mean())
    return np.mean(scores) * 100 if scores else 0

# -----------------------------
# APP
# -----------------------------

st.title("📊 Sector Rotation Engine V3 (REAL BREADTH SYSTEM)")

spy = get_price(SPY)

results = []

for name, data in SECTORS.items():

    etf = data["etf"]
    stocks = data["stocks"]

    sector = get_price(etf)

    if sector is None or spy is None:
        continue

    rs_score = rs(sector, spy)
    mom_score = momentum(sector)

    b20, b50 = breadth(stocks)

    lead_score = leadership(stocks)

    breadth_score = (b20 + b50) / 2

    score = (
        0.30 * rs_score +
        0.25 * breadth_score +
        0.15 * mom_score +
        0.30 * lead_score
    )

    results.append([
        name,
        etf,
        round(score, 2),
        round(rs_score, 2),
        round(b20, 2),
        round(b50, 2),
        round(mom_score, 2),
        round(lead_score, 2)
    ])

df = pd.DataFrame(results, columns=[
    "Sector", "ETF", "Score",
    "RS", "Breadth 20DMA", "Breadth 50DMA",
    "Momentum", "Leadership"
])

df = df.sort_values("Score", ascending=False)

st.subheader("🏆 Sector Rotation Ranking (REAL BREADTH ENGINE)")
st.dataframe(df, use_container_width=True)

st.subheader("🔥 Top Emerging Sectors")
st.write(df.head(3))

st.subheader("⚠️ Weak / Distribution Sectors")
st.write(df.tail(2))
