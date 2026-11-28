import streamlit as st

st.set_page_config(page_title="About", layout="wide")
st.title("About")

st.markdown("""
### Goal-differential analysis

Each NHL team is carried as a price series. The price is cumulative goal differential: goals scored minus goals allowed, added from the first game of the season. One game is one bar. The working chart is the same object used on equities and foreign exchange: open, high, low, close, a short moving average, an intermediate moving average, and a separate momentum reading on the recent windows.

A win in the standings is a binary. On this tape the path matters. A 4–1 win and a 2–1 win are different bars, and a team that wins while giving differential back prints differently from a team that is extending a trend.

### How a bar is built

The season opens at zero. Every later game opens at the previous close. The horizontal axis is game number, so the series is in event time. An off-night prints nothing, the way a trade chart prints only when a trade occurs.

Inside the game the running differential is marked period by period. That path is the intrabar tape.

| Print | Equities and FX | This series |
| --- | --- | --- |
| Open | Prior settlement, when the session does not gap | Previous cumulative goal differential |
| High | Best price of the session | Highest running differential through regulation and overtime |
| Low | Worst price of the session | Lowest running differential through regulation and overtime |
| Close | Official settlement | Cumulative differential after the final result |

Regulation is the continuous session. Each period adds that period's goal margin to the running total, the way successive prints build a daily candle. Overtime stays on the same path, so an overtime goal can set the high or the low and leave a wick.

A shootout is the settlement mark. It shifts the close by one goal. The high and the low stay on the regulation and overtime path. A scoreless game decided in a shootout is a flat bar at the open, with the close moved one goal. That is the same role as an FX fixing price or a closing auction: the continuous session has finished, and a discrete mark sets the official close.

The body and the wick then read in the ordinary way.

- A close at or above the open means the team added to its cumulative differential. The body is green.
- A close below the open means the team gave differential back. The body is red.
- A tall body is a wide goal margin. A small body is a one-goal game or a shootout decision.
- An upper wick is a lead that did not survive to the close. A lower wick is a deficit that was recovered before settlement.

Under the price pane, optional GF+GA bars measure activity. Total goals fill the role volume fills under a stock chart, or tick count under an FX chart. A high-event game is a high-range, high-activity bar even when the close barely changes.

### Trend and relative strength

Two simple moving averages sit on the close: three games and six games. They are ordinary SMAs of the settlement. The three-game average is the short trend. The six-game average is the intermediate trend. The stack is read the way a price is read against its averages.

- Close above both averages, with the three-game average above the six-game average, is bullish alignment. Short trend, intermediate trend, and level agree.
- Close below both averages, with the three-game average under the six-game average, is bearish alignment.
- A close between the averages, or a cross of the two averages, is a transition. Failed pushes and reversions to the mean show up in that band, as they do when a price re-enters its moving-average ribbon.

Every team is denominated in goals, so the levels compare directly. The Performance table, sorted by Close, is a relative-strength ranking: who has accumulated the most differential, in the same sense that a relative-strength table ranks markets by cumulative gain off a shared baseline. Last 3 and Last 6 are rolling net differentials, rate-of-change windows in the same family as an N-bar ROC. Win rate and win-by-two rate describe the distribution around the path: how often a bar closes positive, and how often the margin is two goals or more.

A matchup is a spread of those readings. One team's level, average stack, and recent rate of change against the opponent's. The chart book and the relative-strength book are reads of that spread. The chart stores the structure. A probability is assigned only when a book acts on it.

### Momentum reading

The momentum book converts the Performance table into one integer per team, so two teams can be subtracted. Each team is placed in a bucket from −5 to +5.

- Strict bull continuation requires Last 3 < Last 6 < Close, with Last 3 positive. The short window, the six-game window, and the season level are ordered and positive. A wide impulse, Last 3 of at least +8 and Last 6 of at least +12, scores +5. A narrower continuation scores +4.
- Strict bear continuation is the mirror image: Last 3 > Last 6 > Close, with Last 3 negative. A wide impulse scores −5. A narrower continuation scores −4.
- All three columns the same sign, with that order broken, scores in the inner band, +1 to +3 or −1 to −3, larger absolute readings scoring further from zero. The regime is intact. The alignment is loose.
- Mixed signs, or a flat reading, score 0. The team is in balance or in transition.

For each game the edge is a pair spread: delta equals one team's bucket minus the other's. The absolute value is the separation. The sign names the side. A wager requires a separation of 4 or more. At most three games are taken, largest separation first, on the side with the more extreme bucket. The posted price has to be +125 or longer on the moneyline, the −1.5 puck line, or an alternate line. When more than one of those prices qualifies, the puck line is the selection. The stake is one flat unit.

The buckets are discrete states of multi-window momentum. The delta is the spread between two states. The price rule keeps the book on plus-money prices, where the payout has to carry the miss rate of a trend rule.

### Books

Four books see the same games and are graded on separate equity curves. Bankrolls and Coach plot those curves.

| Book | Color | Reading |
| --- | --- | --- |
| User | Gold | Chart structure, relative strength and relative weakness |
| CandleStick Dan | Orange | Chart structure |
| Mo-Dan | Blue | Momentum buckets and the game delta |
| Degen Dan | Green | Control. An independent card, held outside the agreement scale |

System wagers are straight bets at +125 or longer. Agreement between the chart reading and the momentum reading is what the Coach page uses for size. Each graded day becomes a daily profit and a cumulative bankroll: the equity curve of that book.

### Measurement loop

1. The night's games arrive as structured JSON: three regulation periods, overtime, and a shootout mark.
2. The digestor checks that the periods, overtime, and shootout sum to the final score, then appends one OHLC row to each team's series.
3. Charts draw the candle, the two moving averages, and the optional activity bars. Performance ranks the league on Close, Last 3, Last 6, win rate, and win-by-two rate.
4. The books read that tape against the morning lines and record their cards.
5. Graded results rebuild the bankroll series.

The series is an accounting of differential already accumulated. The next game is a new bar.

Study and record-keeping only. Nothing here is a promise of profit.
""")
