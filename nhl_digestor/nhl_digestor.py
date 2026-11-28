"""
nhl_digestor.py

Local NHL goal-diff digestor.

Layout (run this file from inside nhl_digestor/):
    nhl_digestor/
        nhl_digestor.py          <-- this file
        games_YYYYMMDD.json      <-- drop new slates here
        nhl_team_data/
            ANA.csv ... WSH.csv  <-- one row per team-game
        processed_files/         <-- you move JSONs here after a good run

Usage:
    python nhl_digestor.py

What it does:
    - Reads every games_*.json in the same folder as this script
    - Checksums (p+ot+so == gf, cross GF/GA, OT/SO flags)
    - Computes goal-diff OHLC. SO is close-only (no wick). OT is a wick.
    - Appends one row per team-game to nhl_team_data/{CODE}.csv
    - Skips a row if that game_id is already in the team CSV (safe to re-run)
    - Does NOT move files. You move the JSON to processed_files/ when done.

Columns:
    game_num, date, opponent, game_id, home,
    Open, High, Low, Close, final_diff,
    gf, ga, result, win, win_by_2
"""

import json
import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "nhl_team_data"

NHL_CODES = [
    "ANA", "BOS", "BUF", "CAR", "CBJ", "CGY", "CHI", "COL",
    "DAL", "DET", "EDM", "FLA", "LAK", "MIN", "MTL", "NJD",
    "NSH", "NYI", "NYR", "OTT", "PHI", "PIT", "SEA", "SJS",
    "STL", "TBL", "TOR", "UTA", "VAN", "VGK", "WPG", "WSH",
]

COLUMNS = [
    "game_num", "date", "opponent", "game_id", "home",
    "Open", "High", "Low", "Close", "final_diff",
    "gf", "ga", "result", "win", "win_by_2",
]


def ensure_team_csvs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for code in NHL_CODES:
        path = DATA_DIR / f"{code}.csv"
        if not path.exists() or path.stat().st_size == 0:
            pd.DataFrame(columns=COLUMNS).to_csv(path, index=False)


def n(x):
    return 0 if x is None else int(x)


def period_ohlc(own_p, opp_p, own_ot, opp_ot, own_so, opp_so, prev_close):
    """Goal-diff path through regulation + OT. SO applied only to Close."""
    running = prev_close
    diffs = [running]
    for o, a in zip(own_p, opp_p):
        running += int(o) - int(a)
        diffs.append(running)
    if own_ot is not None or opp_ot is not None:
        running += n(own_ot) - n(opp_ot)
        diffs.append(running)
    close = running + (n(own_so) - n(opp_so))
    return {
        "Open": prev_close,
        "High": max(diffs),
        "Low": min(diffs),
        "Close": close,
        "final_diff": close,
    }


def validate_game(g):
    """Return list of error strings. Empty = good."""
    errs = []
    home, away = g.get("home"), g.get("away")
    teams = g.get("teams") or {}
    if home not in teams or away not in teams:
        return [f"{g.get('game_id')} missing home/away in teams"]
    H, A = teams[home], teams[away]
    for code, t in ((home, H), (away, A)):
        if len(t.get("p") or []) != 3:
            errs.append(f"{g['game_id']} {code} p length != 3")
        s = sum(t["p"]) + n(t.get("ot")) + n(t.get("so"))
        if s != t["gf"]:
            errs.append(f"{g['game_id']} {code} p+ot+so={s} != gf={t['gf']}")
    if A["gf"] != H["ga"] or H["gf"] != A["ga"]:
        errs.append(f"{g['game_id']} cross GF/GA mismatch")
    if g.get("result") == "so" and n(H.get("so")) + n(A.get("so")) != 1:
        errs.append(f"{g['game_id']} SO flags not 0/1")
    if g.get("result") == "ot" and n(H.get("ot")) + n(A.get("ot")) != 1:
        errs.append(f"{g['game_id']} OT goals not 0/1")
    return errs


def load_existing(code):
    path = DATA_DIR / f"{code}.csv"
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMNS)
    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=COLUMNS)
    if df.empty or "game_id" not in df.columns:
        return pd.DataFrame(columns=COLUMNS)
    return df


def append_row(code, row):
    path = DATA_DIR / f"{code}.csv"
    df = load_existing(code)
    if not df.empty and "game_id" in df.columns and (df["game_id"] == row["game_id"]).any():
        return False
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(path, index=False)
    return True


def process_json(path: Path):
    data = json.loads(path.read_text())
    date = data.get("date")
    games = data.get("games") or []
    skipped = data.get("skipped") or []
    print(f"\n📁 {path.name}  {date}  games={len(games)}  skipped={len(skipped)}")

    written = 0
    for g in games:
        errs = validate_game(g)
        if errs:
            for e in errs:
                print(f"  ⚠️  {e}")
            continue

        home, away = g["home"], g["away"]
        H, A = g["teams"][home], g["teams"][away]

        for code, side, opp_code, opp in (
            (away, A, home, H),
            (home, H, away, A),
        ):
            df = load_existing(code)
            prev = int(df["Close"].iloc[-1]) if not df.empty and "Close" in df.columns else 0
            ohlc = period_ohlc(
                side["p"], opp["p"],
                side.get("ot"), opp.get("ot"),
                side.get("so"), opp.get("so"),
                prev,
            )
            margin = side["gf"] - side["ga"]
            row = {
                "game_num": (0 if df.empty else int(df["game_num"].max())) + 1,
                "date": date,
                "opponent": opp_code,
                "game_id": g["game_id"],
                "home": 1 if code == home else 0,
                "Open": ohlc["Open"],
                "High": ohlc["High"],
                "Low": ohlc["Low"],
                "Close": ohlc["Close"],
                "final_diff": ohlc["final_diff"],
                "gf": side["gf"],
                "ga": side["ga"],
                "result": g.get("result"),
                "win": 1 if side["gf"] > side["ga"] else 0,
                "win_by_2": 1 if margin >= 2 else 0,
            }
            if append_row(code, row):
                written += 1
                print(
                    f"  ✅ {code} g{row['game_num']} vs {opp_code} "
                    f"O={row['Open']} H={row['High']} L={row['Low']} C={row['Close']} "
                    f"gf={row['gf']} ga={row['ga']} {row['result']}"
                )
            else:
                print(f"  · {code} {g['game_id']} already present")
    return written


def main():
    ensure_team_csvs()
    files = sorted(HERE.glob("games_*.json"))
    if not files:
        print(f"No games_*.json next to {Path(__file__).name}")
        print(f"Looking in: {HERE}")
        return
    total = 0
    for f in files:
        total += process_json(f)
    print(f"\n🎉 Done. {total} new team-game rows written to {DATA_DIR}")
    print("Move the JSON files you just digested into processed_files/ when you're happy.")


if __name__ == "__main__":
    main()
