import streamlit as st

st.title("About")

st.markdown("""
### NHL Goal-Diff Project

Candlestick charts of cumulative goal differential + momentum buckets + system bets.

**Books**
- **User** (gold) — Chart System , Realative Strength Weakness 
- **Degen Dan** (green) — Control
- **CandleStick Dan** (orange) — Chart System
- **Mo-Dan** (blue) — Momentum System

**How it works**
1. Data Dan supplies nightly JSON.
2. Digestor builds team CSVs and the Streamlit tape.
3. Morning meeting: lines in → bots pick → results logged.
4. Bankrolls update from the graded CSVs.

All picks are for entertainment / educational purposes. No guarantees. Bet at your own risk.

Built with Streamlit + pandas + plotly.
""")