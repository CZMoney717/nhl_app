import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Coach Analytics", layout="wide")
st.title("Coach Analytics")

# --- Load data ---
bankroll_dir = Path("bankrolls")
sources = ["user", "degen", "candlestick", "momentum"]
colors = {
    "user": "#FFD700",
    "degen": "#00C853",
    "candlestick": "#FF6D00",
    "momentum": "#2979FF",
}

dfs = []
for src in sources:
    path = bankroll_dir / f"bankroll_{src}.csv"
    if path.exists():
        df = pd.read_csv(path, parse_dates=["date"])
        df["source"] = src
        dfs.append(df)

if not dfs:
    st.warning("No bankroll CSVs found in bankrolls/")
    st.stop()

all_df = pd.concat(dfs, ignore_index=True)

# --- Filters ---
st.sidebar.header("Filters")
date_range = st.sidebar.selectbox("Date range", ["All","Last 3 days", "Last 7 days", "Last 30 days"])
if date_range == "Last 7 days":
    cutoff = all_df["date"].max() - pd.Timedelta(days=7)
    all_df = all_df[all_df["date"] >= cutoff]
if date_range == "Last 3 days":
    cutoff = all_df["date"].max() - pd.Timedelta(days=3)
    all_df = all_df[all_df["date"] >= cutoff]    
elif date_range == "Last 30 days":
    cutoff = all_df["date"].max() - pd.Timedelta(days=30)
    all_df = all_df[all_df["date"] >= cutoff]

# --- Watchlist table ---
st.subheader("Bettor Watchlist")

def calc_metrics(g):
    total_bets = g["n_bets"].sum()
    total_profit = g["daily_profit"].sum()
    final = g["cumulative"].iloc[-1] if not g.empty else 0
    roi = (final / (total_bets * 25)) * 100 if total_bets else 0  # rough, assumes $25 unit
    wins = (g["daily_profit"] > 0).sum()
    days = len(g)
    win_pct = (wins / days * 100) if days else 0
    return pd.Series({
        "Days": days,
        "Bets": int(total_bets),
        "Final": round(final, 2),
        "ROI %": round(roi, 1),
        "Win Days %": round(win_pct, 1),
    })

watchlist = all_df.groupby("source").apply(calc_metrics).reset_index()
watchlist = watchlist.rename(columns={"source": "Bettor"})
st.dataframe(watchlist, use_container_width=True, hide_index=True)

# --- Equity curves ---
st.subheader("Cumulative Bankrolls")
fig = px.line(
    all_df,
    x="date",
    y="cumulative",
    color="source",
    color_discrete_map=colors,
    markers=True,
    title="Equity Curves",
)
fig.update_layout(hovermode="x unified", legend_title="Bettor")
st.plotly_chart(fig, use_container_width=True)

# --- Daily P&L ---
if st.checkbox("Show daily P&L"):
    fig2 = px.bar(
        all_df,
        x="date",
        y="daily_profit",
        color="source",
        color_discrete_map=colors,
        barmode="group",
        title="Daily Profit",
    )
    st.plotly_chart(fig2, use_container_width=True)

# --- Consensus placeholder ---
st.subheader("Consensus Monitor (placeholder)")
st.info("Once the agreement layer writes a daily consensus file, this panel will show tonight's slate with agreement counts and a strength bar. For now it is a stub.")

# Example stub table
stub = pd.DataFrame({
    "Game": ["PHI@OTT", "MTL@CAR", "MIN@CGY"],
    "Pick": ["OTT -1.5", "CAR -2.5", "MIN -2.5"],
    "Agreement": [4, 2, 2],
    "Bettors": ["User, CS, Mo, Degen", "User, Mo", "User, Mo"],
})
st.dataframe(stub, use_container_width=True, hide_index=True)

# --- Notes ---
st.caption("Draft v1 — powered by bankroll CSVs. Individual bet logs and full consensus matrix come next.")
