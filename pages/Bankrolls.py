import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="NHL Bets", layout="wide")
st.title("Bankrolls")

# Load
bankroll_dir = Path("bankrolls")  # adjust if needed
files = {
    "user": bankroll_dir / "bankroll_user.csv",
    "degen": bankroll_dir / "bankroll_degen.csv",
    "candlestick": bankroll_dir / "bankroll_candlestick.csv",
    "momentum": bankroll_dir / "bankroll_momentum.csv",
}

colors = {
    "user": "#FFD700",        # gold
    "degen": "#00C853",       # green
    "candlestick": "#FF6D00", # orange
    "momentum": "#2979FF",    # blue
}

dfs = []
for source, path in files.items():
    if path.exists():
        df = pd.read_csv(path, parse_dates=["date"])
        df["source"] = source
        dfs.append(df)

if not dfs:
    st.warning("No bankroll CSVs found.")
    st.stop()

all_df = pd.concat(dfs, ignore_index=True)

# Cumulative line chart
fig = px.line(
    all_df,
    x="date",
    y="cumulative",
    color="source",
    color_discrete_map=colors,
    title="Cumulative Bankroll",
    markers=True,
)
fig.update_layout(hovermode="x unified", legend_title="Book")
st.plotly_chart(fig, use_container_width=True)

# Optional daily bars
if st.checkbox("Show daily P&L bars"):
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

# Summary table
summary = (
    all_df.groupby("source")
    .agg(
        days=("date", "nunique"),
        bets=("n_bets", "sum"),
        final=("cumulative", "last"),
    )
    .reset_index()
)
st.dataframe(summary, use_container_width=True)