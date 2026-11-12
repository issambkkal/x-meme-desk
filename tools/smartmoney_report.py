"""Daily smart-money report: what the tracked wallets bought and dumped in the last 24h.

Builds a chart (charts/YYYY-MM-DD-smartmoney.png) and a queued X thread
(queue/YYYY-MM-DD-HHMM-smartmoney-report.md). Research only: no buy calls.

Usage: python tools/smartmoney_report.py [--post-at "YYYY-MM-DD HH:MM"] [--extra-trades file.jsonl ...]
"""
import argparse
import datetime as dt
import json
import sys
from collections import defaultdict
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from chart import render  # noqa: E402
from smartmoney import WSOL, dexscreener, sol_usd  # noqa: E402


def load(paths, hours=24):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    seen, out = set(), []
    for p in paths:
        for line in Path(p).read_text().splitlines():
            try:
                t = json.loads(line)
            except ValueError:
                continue
            if t["sig"] in seen or dt.datetime.fromisoformat(t["time"]) < cutoff:
                continue
            seen.add(t["sig"])
            out.append(t)
    return out


def usd(x):
    if x >= 1e6:
        return f"${x / 1e6:.1f}M"
    if x >= 1e3:
        return f"${x / 1e3:.1f}K"
    return f"${x:,.0f}"


def report_day(post_at):
    """The day a report belongs to. Reports go out ~18:30 Doha; a run that fires late (after midnight,
    up to 08:00 Doha) still belongs to the previous evening's report."""
    return (post_at - dt.timedelta(hours=8)).date()


def already_reported(post_at):
    """The queue/posted report file that already covers this report day, if any. GitHub sometimes fires
    the daily cron 4-10 h late, after keepalive already started the report: that made two threads a day."""
    day = report_day(post_at)
    for folder in ("queue", "posted"):
        for f in (ROOT / folder).glob("*-smartmoney-report.md"):
            try:
                at = dt.datetime.strptime(f.name[:15], "%Y-%m-%d-%H%M").replace(tzinfo=post_at.tzinfo)
            except ValueError:
                continue
            if folder == "queue" and "\nstatus: hold" in f.read_text():
                continue
            if report_day(at) == day:
                return f
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-at")
    ap.add_argument("--extra-trades", nargs="*", default=[])
    ap.add_argument("--force", action="store_true", help="build even if this report day already has a report")
    a = ap.parse_args()
    if not a.force and not a.post_at:
        prev = already_reported(dt.datetime.now(dt.timezone(dt.timedelta(hours=3))) + dt.timedelta(minutes=70))
        if prev:
            print(f"report already queued/posted recently ({prev.relative_to(ROOT)}); skipping")
            return
    files = sorted((ROOT / "smartmoney" / "trades").glob("*.jsonl"))[-2:] + [Path(p) for p in a.extra_trades]
    trades = load(files)
    price = sol_usd() or 0
    wallets = {t["wallet"] for t in trades}
    agg = defaultdict(lambda: {"buyers": set(), "sellers": set(), "in": 0.0, "out": 0.0})
    for t in trades:
        v = t["quote_usd"] + t["quote_sol"] * price
        g = agg[t["mint"]]
        if t["side"] == "BUY":
            g["buyers"].add(t["wallet"]); g["in"] += v
        else:
            g["sellers"].add(t["wallet"]); g["out"] += v
    info = dexscreener([m for m in agg if m != WSOL][:90])
    rows = []
    for m, g in agg.items():
        sym = ((info.get(m) or {}).get("baseToken") or {}).get("symbol")
        if not sym or m == WSOL:
            continue
        rows.append({"sym": sym, "buyers": len(g["buyers"]), "sellers": len(g["sellers"]),
                     "in": g["in"], "out": g["out"],
                     "mc": (info[m].get("marketCap") or info[m].get("fdv") or 0),
                     "chg24": ((info[m].get("priceChange") or {}).get("h24"))})
    buys = sum(t["side"] == "BUY" for t in trades)
    total_in = sum(r["in"] for r in rows)
    total_out = sum(r["out"] for r in rows)
    most_bought = sorted(rows, key=lambda r: (-r["buyers"], -r["in"]))[:5]
    most_dumped = sorted(rows, key=lambda r: (-r["out"]))[:3]
    tokens_touched = len(rows)

    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))
    chart_path = f"charts/{today:%Y-%m-%d}-smartmoney.png"
    render({"type": "bars", "title": "What 42 smart-money wallets bought today",
            "subtitle": "Tokens bought by the most tracked wallets, last 24h (number of wallets)",
            "source": f"Data: on-chain swaps of {len(wallets)} active GMGN smart-money wallets, tracked by @issam0pc4u",
            "out": chart_path,
            "items": [{"label": f"${r['sym']}", "value": r["buyers"],
                       "text": f"{r['buyers']} wallets · {usd(r['in'])} in", "highlight": i == 0}
                      for i, r in enumerate(most_bought)]})

    top = most_bought[0] if most_bought else None
    dump = most_dumped[0] if most_dumped else None
    def chg(r):
        return f"{r['chg24']:+.0f}% in 24h" if r.get("chg24") is not None else "24h change n/a"
    posts = [
        f"I track 42 of the most profitable meme coin wallets on Solana. Here's what they did in the last 24h 🧵\n\n"
        f"{buys} buys, {len(trades) - buys} sells, {tokens_touched} different tokens.\n\n"
        f"Smart money in: {usd(total_in)}. Out: {usd(total_out)}.",
    ]
    if top:
        posts.append(f"Most bought: ${top['sym']}\n\n{top['buyers']} tracked wallets bought it, {usd(top['in'])} in total. "
                     f"Market cap {usd(top['mc'])}, {chg(top)}.\n\n"
                     f"{top['sellers']} of them have already sold some. Watch that number.")
    if dump:
        posts.append(f"Most dumped: ${dump['sym']}\n\n{usd(dump['out'])} sold by {dump['sellers']} tracked wallet{'s' if dump['sellers'] != 1 else ''}. "
                     f"{chg(dump)}.\n\nWhen the smart money leaves, the late buyers become the exit.")
    posts.append("The lesson from 24h of their trades: they buy small, take profit fast, and dump losers within hours.\n\n"
                 "Most of their 'wins' are trades, not holds.\n\nResearch, not advice.")
    posts.append("I post every smart-money signal and every trap the moment the bot sees it, free, in my Telegram "
                 "group imbi MOON. Link is in my pinned post.")
    post_at = a.post_at or (today + dt.timedelta(minutes=70)).strftime("%Y-%m-%d %H:%M")
    slug = post_at.replace("-", "").replace(":", "").replace(" ", "-")
    qpath = ROOT / "queue" / f"{post_at[:10]}-{post_at[11:13]}{post_at[14:16]}-smartmoney-report.md"
    body = "\n===\n".join(posts)
    qpath.write_text(f"""---
post_at: {post_at}
status: ready
pillar: data
image: {chart_path}
queued_at: {today:%Y-%m-%d %H:%M}
sources:
  - https://github.com/issambkkal/x-meme-desk/tree/main/smartmoney
  - https://gmgn.ai/trade?chain=sol&tab=smart_degen
---
{body}
""")
    print(qpath.relative_to(ROOT), "|", chart_path)
    print(body)


if __name__ == "__main__":
    main()
