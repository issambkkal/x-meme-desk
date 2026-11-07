"""Post new smart-money signals from smartmoney/signals.json to the imbi MOON Telegram.

Each token is posted once per 24h (state in smartmoney/telegram_state.json). Tokens whose
red flags show the move is over (wallets selling, price far below entry, micro cap) are
posted as warnings, not as opportunities. Every message says it is research, not advice.

Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (e.g. @imbimoon or -100...). Missing → dry run.
"""
import datetime as dt
import html
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "smartmoney" / "signals.json"
STATE = ROOT / "smartmoney" / "telegram_state.json"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT = os.environ.get("TELEGRAM_CHAT_ID")
REPOST_HOURS = 24
DANGER = ("already selling", "micro cap", "late", "no DEX pair")


def usd(x):
    if x is None:
        return "?"
    return f"${x:,.0f}" if x >= 1 else f"${x:.8f}".rstrip("0")


def message(s):
    flags = s.get("red_flags") or []
    danger = any(any(k in f for k in DANGER) for f in flags) or (s.get("change_since_entry_pct") or 0) < -30
    head = "⚠️ <b>TRAP WATCH</b>" if danger else "🟢 <b>SMART-MONEY CONVERGENCE</b>"
    sym = html.escape(str(s.get("symbol") or "?"))
    lines = [
        f"{head} · ${sym}",
        "",
        f"👛 {s['wallets']} tracked wallets bought ({s['core_wallets']} top-tier)",
        f"💰 Smart money in: {usd(s.get('smart_buy_usd'))}",
        f"🎯 Their avg entry {usd(s.get('avg_entry_usd'))} → now {usd(s.get('price_usd'))}"
        + (f" ({s['change_since_entry_pct']:+.0f}%)" if s.get("change_since_entry_pct") is not None else ""),
        f"💧 Liquidity {usd(s.get('liquidity_usd'))} · MC {usd(s.get('market_cap'))} · age {s.get('pair_age_h')}h",
        "",
        "🚩 " + (html.escape("; ".join(flags)) if flags else "No red flags found by the script, still check it yourself"),
        "",
        f"<code>{s['mint']}</code>",
    ]
    links = []
    if s.get("dexscreener"):
        links.append(f'<a href="{s["dexscreener"]}">Chart</a>')
    links.append(f'<a href="{s["bubblemaps"]}">Bubblemaps</a>')
    lines += [" · ".join(links), "", "<i>Research, not financial advice. Smart wallets lose too. Never risk money you can't lose.</i>"]
    return "\n".join(lines)


CHAT_FILE = ROOT / "smartmoney" / "telegram_chat.json"
GROUP_TITLE = "imbi MOON"


def find_chat():
    """Use TELEGRAM_CHAT_ID, else the saved id, else find the group the bot was added to."""
    if CHAT:
        return CHAT
    if CHAT_FILE.exists():
        return json.loads(CHAT_FILE.read_text())["chat_id"]
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=20).json()
    if not r.get("ok"):
        raise RuntimeError(f"Telegram refused the token: {r.get('error_code')} {r.get('description')}")
    me = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=20).json().get("result", {})
    seen = sorted({((u.get(k) or {}).get("chat") or {}).get("title") or "?" for u in r["result"]
                   for k in ("my_chat_member", "message") if u.get(k)})
    print(f"bot @{me.get('username')}: {len(r['result'])} pending updates; chats seen: {seen}")
    for u in reversed(r.get("result", [])):
        for key in ("my_chat_member", "message", "channel_post"):
            chat = (u.get(key) or {}).get("chat") or {}
            if chat.get("title") == GROUP_TITLE and chat.get("type") in ("group", "supergroup"):
                CHAT_FILE.write_text(json.dumps({"chat_id": chat["id"], "title": chat["title"]}))
                return chat["id"]
    raise RuntimeError(f"Bot can't see the '{GROUP_TITLE}' group yet: post any message in the group, then rerun")


def send(chat, text):
    r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": chat, "text": text, "parse_mode": "HTML",
                            "disable_web_page_preview": True}, timeout=20)
    data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    new_id = (data.get("parameters") or {}).get("migrate_to_chat_id")
    if new_id:  # group was upgraded to a supergroup: remember the new id and retry once
        CHAT_FILE.write_text(json.dumps({"chat_id": new_id, "title": GROUP_TITLE}))
        return send(new_id, text)
    if not r.ok:
        raise RuntimeError(f"Telegram {r.status_code}: {r.text[:200]}")
    return chat


def main():
    if not SIGNALS.exists():
        print("no signals.json yet")
        return
    data = json.loads(SIGNALS.read_text())
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    now = time.time()
    sent = 0
    first_time = TOKEN and not CHAT_FILE.exists() and not CHAT
    chat = find_chat() if TOKEN else None
    if first_time and chat:
        chat = send(chat, "✅ <b>imbi MOON Signals bot is online.</b>\n\nI watch 42 proven meme coin wallets "
                          "around the clock and post here when several buy the same token, or when they start "
                          "dumping one.\n\n<i>Research, not financial advice.</i>")
    for s in data.get("signals", []):
        last = state.get(s["mint"], 0)
        if now - last < REPOST_HOURS * 3600:
            continue
        text = message(s)
        if not chat:
            print("[dry-run]\n" + text + "\n")
        else:
            chat = send(chat, text)
            time.sleep(1)
        state[s["mint"]] = now
        sent += 1
    state = {m: t for m, t in state.items() if now - t < 7 * 86400}
    STATE.write_text(json.dumps(state, indent=1))
    print(f"{sent} signal(s) {'sent' if chat else 'previewed'} at {dt.datetime.now():%H:%M}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never break the tracker run because of Telegram
        print(f"Telegram step skipped: {e}")
