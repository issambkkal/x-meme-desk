"""Turn the best smart-money signals into X posts that send people to the imbi MOON Telegram.

Reads smartmoney/signals.json (written by tools/smartmoney.py) and queues at most
GREEN_PER_DAY "signal" posts and TRAP_PER_DAY "trap watch" posts per Doha day, each token at
most once per 48h. Posts are queued with `fast: true` (no review wait) and
`max_delay_minutes` (dropped if they can't go out while still fresh).

No contract addresses on X (the X API refuses crypto addresses for the first 7 days after app
authorization, and the CA lives in Telegram anyway); one cashtag per post (X API limit).
Research, not advice: green posts always list the red flags and never say "buy".
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "smartmoney" / "signals.json"
STATE = ROOT / "smartmoney" / "x_signals_state.json"
QUEUE = ROOT / "queue"
DOHA = dt.timezone(dt.timedelta(hours=3))
GREEN_PER_DAY, TRAP_PER_DAY, REPEAT_HOURS = 0, 0, 48  # owner, Nov 13: no automatic signal/trap posts on X (Telegram keeps them)
DANGER = ("already selling", "micro cap", "late", "no DEX pair", "bonding curve")


def usd(x):
    if not x:
        return "?"
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if x >= div:
            return f"${x / div:.1f}{suf}"
    return f"${x:,.0f}"


def age(h):
    if h is None:
        return "age ?"
    return f"{h * 60:.0f} min old" if h < 1 else (f"{h:.0f}h old" if h < 48 else f"{h / 24:.0f} days old")


def sym(s):
    """Ticker for the post: a $cashtag when X can link it, otherwise the plain symbol."""
    raw = str(s.get("symbol") or "").strip()
    if not raw:
        return None
    return f"${raw}" if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,14}", raw) else raw


def selling(s):
    for f in s.get("red_flags") or []:
        m = re.search(r"(\d+) tracked wallet", f)
        if m and "selling" in f:
            return int(m.group(1))
    return 0


def classify(s):
    flags = s.get("red_flags") or []
    chg = s.get("change_since_entry_pct")
    liq, mc = s.get("liquidity_usd") or 0, s.get("market_cap") or 0
    if s.get("wallets", 0) < 3 or not sym(s):
        return None
    danger = any(any(k in f for k in DANGER) for f in flags) or (chg or 0) < -30
    if not danger and liq >= 30_000 and mc >= 100_000 and (s.get("pair_age_h") or 0) >= 1 and (chg or 0) <= 60:
        return "green"
    if danger and liq >= 20_000 and mc >= 100_000:
        return "trap"
    return None


def text(s, kind):
    t, w, chg = sym(s), s["wallets"], s.get("change_since_entry_pct") or 0
    if kind == "green":
        flags = [f for f in (s.get("red_flags") or []) if "top-10" not in f]
        return (f"🟢 Smart-money signal: {t}\n\n"
                f"{w} of the 42 profitable wallets I track bought it in the last 6h.\n"
                f"MC {usd(s.get('market_cap'))} · liquidity {usd(s.get('liquidity_usd'))} · {age(s.get('pair_age_h'))}\n"
                f"Price vs their entry: {chg:+.0f}%\n"
                f"⚠️ {flags[0] if flags else 'No red flags in my checks, still check holders'}\n\n"
                f"CA + live updates free in my Telegram (link in pinned post). Not advice.")
    n = selling(s)
    why = (f"Price is {chg:+.0f}% vs their entry" + (f" and {n} of them are already selling." if n else "."))
    return (f"🚩 Trap watch: {t}\n\n"
            f"{w} smart-money wallets I track bought it early. {why}\n\n"
            f"MC {usd(s.get('market_cap'))} · liquidity {usd(s.get('liquidity_usd'))}\n\n"
            f"Buying now = buying their exit. I post these live in my free Telegram (link in pinned post).")


def main():
    if not SIGNALS.exists():
        return print("no signals.json yet")
    data = json.loads(SIGNALS.read_text())
    state = json.loads(STATE.read_text()) if STATE.exists() else {"posted": {}, "days": {}}
    now = dt.datetime.now(DOHA)
    day = now.strftime("%Y-%m-%d")
    counts = state["days"].setdefault(day, {"green": 0, "trap": 0})
    limit = {"green": GREEN_PER_DAY, "trap": TRAP_PER_DAY}
    picked = []
    order = sorted(data.get("signals") or [], key=lambda s: (-s.get("score", 0), -(s.get("liquidity_usd") or 0)))
    for s in order:
        kind = classify(s)
        if not kind or counts[kind] >= limit[kind]:
            continue
        last = state["posted"].get(s["mint"])
        if last and (now - dt.datetime.fromisoformat(last)).total_seconds() < REPEAT_HOURS * 3600:
            continue
        picked.append((s, kind))
        counts[kind] += 1
        state["posted"][s["mint"]] = now.isoformat()
        if len(picked) >= 2:
            break
    for i, (s, kind) in enumerate(picked):
        at = now + dt.timedelta(minutes=i)
        slug = re.sub(r"[^a-z0-9]+", "", sym(s).lower()) or "token"
        name = f"{at:%Y-%m-%d-%H%M}-{kind}-{slug[:20]}.md"
        sources = [u for u in (s.get("dexscreener"), s.get("bubblemaps")) if u]
        sources.append("https://github.com/issambkkal/x-meme-desk/tree/main/smartmoney")
        front = "\n".join([
            "---", f"post_at: {at:%Y-%m-%d %H:%M}", "status: ready", f"pillar: {'scam' if kind == 'trap' else 'data'}",
            "fast: true", "max_delay_minutes: 120", f"queued_at: {at:%Y-%m-%d %H:%M}", "sources:",
            *[f"  - {u}" for u in sources], "---"])
        (QUEUE / name).write_text(front + "\n" + text(s, kind) + "\n")
        print("queued", name)
        print(text(s, kind), "\n")
    keep = (now - dt.timedelta(days=7)).isoformat()
    state["posted"] = {m: t for m, t in state["posted"].items() if t >= keep}
    state["days"] = {d: c for d, c in state["days"].items() if d >= (now - dt.timedelta(days=3)).strftime("%Y-%m-%d")}
    STATE.write_text(json.dumps(state, indent=1))
    if not picked:
        print("no new X-worthy signal")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never break the tracker run
        print(f"X signal step skipped: {e}", file=sys.stderr)
