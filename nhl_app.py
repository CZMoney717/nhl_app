"""
nhl_app.py

Streamlit dashboard for NHL goal-diff candlesticks.

Layout:
    NHL_PROJECT/
        nhl_app.py                  <-- this file
        nhl_digestor/
            nhl_team_data/
                ANA.csv ... WSH.csv

Run from NHL_PROJECT:
    streamlit run nhl_app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="NHL Goal Diff Dashboard", layout="wide")

DATA_DIR = Path(__file__).resolve().parent / "nhl_digestor" / "nhl_team_data"


@st.cache_data
def load_all_teams():
    teams = {}
    if not DATA_DIR.exists():
        return teams
    for path in sorted(DATA_DIR.glob("*.csv")):
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if df.empty or "Close" not in df.columns:
            continue
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("game_num").reset_index(drop=True)
        teams[path.stem] = df
    return teams


teams_data = load_all_teams()

st.sidebar.title("NHL Goal Diff")
page = st.sidebar.radio("Page", ["Charts", "Performance"], index=0)

if not teams_data:
    st.error(f"No team CSVs found in {DATA_DIR}")
    st.stop()


if page == "Charts":
    st.title("NHL Cumulative Goal Differential")

    team_list = sorted(teams_data.keys())
    selected = st.sidebar.selectbox("Team", team_list)
    x_mode = st.sidebar.radio("X axis", ["game_num"], index=0)
    show_volume = st.sidebar.checkbox("Show GF+GA bars", value=False)

    df = teams_data[selected].copy()
    df["SMA3"] = df["Close"].rolling(3).mean()
    df["SMA6"] = df["Close"].rolling(6).mean()
    x = df[x_mode]

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=x,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        name="OHLC",
        increasing_line_color="#00ff88",
        decreasing_line_color="#ff4444",
        text=[
            f"{r.opponent} {int(r.gf)}-{int(r.ga)} {r.result}"
            for r in df.itertuples()
        ],
        hovertext=[
            f"{r.opponent} {int(r.gf)}-{int(r.ga)} {r.result}"
            for r in df.itertuples()
        ],
    ))
    fig.add_trace(go.Scatter(
        x=x, y=df["SMA3"],
        name="SMA 3", line=dict(color="orange", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=x, y=df["SMA6"],
        name="SMA 6", line=dict(color="cyan", width=2),
    ))

    if show_volume:
        colors = ["#00ff88" if c >= o else "#ff4444" for o, c in zip(df["Open"], df["Close"])]
        fig.add_trace(go.Bar(
            x=x,
            y=df["gf"] + df["ga"],
            name="GF+GA",
            marker_color=colors,
            opacity=0.35,
            yaxis="y2",
        ))
        fig.update_layout(
            yaxis2=dict(overlaying="y", side="right", showgrid=False, title="GF+GA"),
        )

    fig.update_layout(
        title=f"{selected} — cumulative goal differential",
        xaxis_title=x_mode,
        yaxis_title="Goal Diff",
        height=650,
        template="plotly_dark",
        hovermode="x unified",
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    last = df.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Games", len(df))
    c2.metric("Close", int(last["Close"]))
    c3.metric("Last gf-ga", int(last["gf"] - last["ga"]))
    c4.metric("Win by 2", f"{df['win_by_2'].mean():.0%}")

    st.dataframe(
        df[["game_num", "date", "opponent", "Open", "High", "Low", "Close",
            "gf", "ga", "result", "win", "win_by_2"]].sort_values("game_num", ascending=False),
        use_container_width=True,
        hide_index=True,
    )


else:  # Performance
    st.title("Team Performance")

    lookback = st.number_input("Custom lookback (games)", min_value=1, value=6, step=1)

    rows = []
    for team, df in teams_data.items():
        if df.empty:
            continue
        last3 = int((df["gf"].iloc[-3:] - df["ga"].iloc[-3:]).sum()) if len(df) >= 1 else 0
        last6 = int((df["gf"].iloc[-6:] - df["ga"].iloc[-6:]).sum()) if len(df) >= 1 else 0
        custom = int((df["gf"].iloc[-lookback:] - df["ga"].iloc[-lookback:]).sum())
        row = {
            "Team": team,
            "Games": len(df),
            "Close": int(df["Close"].iloc[-1]),
            "Last 3": last3,
            "Last 6": last6,
            "Win %": f"{df['win'].mean():.0%}",
            "Win by 2 %": f"{df['win_by_2'].mean():.0%}",
        }
        # only add a custom column when it is not already Last 3 or Last 6
        if lookback not in (3, 6):
            row[f"Last {lookback}"] = custom
        rows.append(row)

    perf = pd.DataFrame(rows).sort_values("Close", ascending=False)

    gradient_cols = ["Close", "Last 3", "Last 6"]
    if lookback not in (3, 6):
        gradient_cols.append(f"Last {lookback}")

    st.dataframe(
        perf.style.background_gradient(subset=gradient_cols, cmap="RdYlGn"),
        use_container_width=True,
        hide_index=True,
    )
