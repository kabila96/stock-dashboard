import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Tech Stocks Analysis Dashboard", layout="wide")
st.title("📊 Tech Stocks Analysis Dashboard")

DATA_DIR = Path("data")
files = list(DATA_DIR.glob("*_data.csv"))

# Fallback: allow uploads if data folder missing
uploaded = st.file_uploader("Upload one or more stock CSVs", type="csv", accept_multiple_files=True)

dfs = []

if files:
    for f in files:
        df = pd.read_csv(f)
        if "Name" not in df.columns:
            df["Name"] = f.stem.split("_")[0]  # infer ticker from filename
        dfs.append(df)

if uploaded:
    for uf in uploaded:
        df = pd.read_csv(uf)
        if "Name" not in df.columns:
            df["Name"] = uf.name.split("_")[0]
        dfs.append(df)

if not dfs:
    st.warning("No data found. Add CSVs in a `data/` folder in your repo or upload them above.")
    st.stop()

all_data = pd.concat(dfs, ignore_index=True)
all_data["date"] = pd.to_datetime(all_data["date"], errors="coerce")
all_data = all_data.dropna(subset=["date"])

# ——— sidebar
st.sidebar.header("Filters")
companies = sorted(all_data["Name"].unique().tolist())
ticker = st.sidebar.selectbox("Company", companies)
metric = st.sidebar.selectbox("Metric", ["close", "open", "high", "low", "volume"])

# ——— filter
dfc = all_data[all_data["Name"] == ticker].sort_values("date")

# ——— chart
st.subheader(f"📈 {ticker} — {metric.capitalize()} over time")
st.line_chart(dfc.set_index("date")[metric])

# ——— stats
st.subheader("📊 Summary stats")
st.dataframe(dfc[["open","high","low","close","volume"]].describe().T)

# ——— download
st.download_button(
    "⬇️ Download combined data (CSV)",
    all_data.to_csv(index=False).encode("utf-8"),
    "combined_stocks.csv",
    "text/csv",
)
