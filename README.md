# nhl_app

# NHL Goal Differential Dashboard

Streamlit app that charts cumulative goal differential for every NHL team as candlesticks.
 
Each game is a candle, the close is the running goal differential, and short moving averages sit on top so the shape of a team is readable at a glance.

## What it shows

- **Charts** — pick a team, see OHLC candles of cumulative goal diff, SMA 3 and SMA 6. X-axis is game number (no calendar gaps). Hover shows opponent and score.
- **Performance** — all 32 teams ranked by current Close, with last 3 / last 6 / custom lookback from goals for minus goals against, plus win % and win-by-2 %.

## Data

Daily JSON score dumps are digested into one CSV per team:
