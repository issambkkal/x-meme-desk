"""Smart-money tracker: follow proven Solana meme coin wallets and flag convergence.

Every run:
  1. For each wallet in smartmoney/wallets.yaml (tiers core + watch), read its new
     transactions from a Solana RPC and turn them into BUY / SELL swaps by comparing the
     wallet's token and SOL balances before and after each transaction.
  2. Append new swaps to smartmoney/trades/YYYY-MM-DD.jsonl.
  3. Group recent buys (default last 6h) by token. When >= 2 distinct wallets bought the same
     token (core wallets count double), it's a convergence signal.
  4. Enrich signals with DexScreener (price, liquidity, market cap, age, volume) and on-chain
     holder concentration, compare the smart wallets' average entry with the price now,
     and list red flags.
  5. Write smartmoney/signals.md (human) and smartmoney/signals.json (machine).

This is research, not advice: it never trades and never says "buy".

Env: SOLANA_RPC_URL (default: public mainnet RPC; a Helius/QuickNode URL is faster),
     SM_WINDOW_HOURS (default 6), SM_MAX_TX_PER_WALLET (default 25).
"""
import datetime as dt
import json
import os
import sys
import time
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
SM = ROOT / "smartmoney"
STATE = SM / "state.json"
TRADES = SM / "trades"
RPC = os.environ.get("SOLANA_RPC_URL") or "https://api.mainnet-beta.solana.com"
WINDOW_H = float(os.environ.get("SM_WINDOW_HOURS", "6"))
MAX_TX = int(os.environ.get("SM_MAX_TX_PER_WALLET", "25"))
BACKFILL = os.environ.get("SM_BACKFILL") == "1"
MIN_USD = float(os.environ.get("SM_MIN_USD", "300"))      # ignore dust convergence
MIN_MC = float(os.environ.get("SM_MIN_MCAP", "50000"))    # flag micro caps below this
WSOL = "So11111111111111111111111111111111111111112"
USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
QUOTES = {WSOL, USDC, USDT}
session = requests.Session()


def rpc(method, params, tries=5):
    for i in range(tries):
        try:
            r = session.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30)
            if r.status_code == 429:
                time.sleep(2 + 2 * i)
                continue
            data = r.json()
            if "error" in data:
                if data["error"].get("code") in (-32429, 429, -32005):
                    time.sleep(2 + 2 * i)
                    continue
                raise RuntimeError(data["error"])
            return data["result"]
        except (requests.RequestException, ValueError):
            time.sleep(1 + i)
    raise RuntimeError(f"RPC {method} failed after {tries} tries")


def sol_usd():
    try:
        r = session.get(f"https://api.dexscreener.com/latest/dex/tokens/{WSOL}", timeout=20).json()
        pairs = [p for p in r.get("pairs") or [] if p.get("quoteToken", {}).get("symbol") in ("USDC", "USDT")]
        pairs.sort(key=lambda p: -(p.get("liquidity") or {}).get("usd", 0))
        return float(pairs[0]["priceUsd"]) if pairs else None
    except Exception:
        return None


def parse_swap(tx, wallet):
    """Return dict(side, mint, amount, quote_sol, quote_usd) for the wallet's swap, or None."""
    if not tx or (tx.get("meta") or {}).get("err"):
        return None
    meta, msg = tx["meta"], tx["transaction"]["message"]
    keys = [k["pubkey"] if isinstance(k, dict) else k for k in msg["accountKeys"]]
    keys += (meta.get("loadedAddresses") or {}).get("writable", []) + (meta.get("loadedAddresses") or {}).get("readonly", [])
    deltas = {}
    for side, sign in (("preTokenBalances", -1), ("postTokenBalances", 1)):
        for b in meta.get(side) or []:
            if b.get("owner") != wallet:
                continue
            amt = float(b["uiTokenAmount"].get("uiAmount") or 0)
            deltas[b["mint"]] = deltas.get(b["mint"], 0) + sign * amt
    sol = 0.0
    if wallet in keys:
        i = keys.index(wallet)
        sol = (meta["postBalances"][i] - meta["preBalances"][i]) / 1e9
        if i == 0:
            sol += meta.get("fee", 0) / 1e9  # don't count the network fee as trade cost
    quote_sol = sol + deltas.pop(WSOL, 0)
    quote_usd = deltas.pop(USDC, 0) + deltas.pop(USDT, 0)
    deltas = {m: d for m, d in deltas.items() if abs(d) > 0}
    if not deltas:
        return None
    mint, amt = max(deltas.items(), key=lambda kv: abs(kv[1]))
    if amt > 0 and (quote_sol < -0.001 or quote_usd < -0.01):
        side = "BUY"
    elif amt < 0 and (quote_sol > 0.001 or quote_usd > 0.01):
        side = "SELL"
    else:
        return None
    return {"side": side, "mint": mint, "amount": abs(amt), "quote_sol": abs(quote_sol), "quote_usd": abs(quote_usd)}


def scan_wallets(wallets, state):
    new = []
    for w in wallets:
        addr = w["address"]
        last = state.get(addr)
        params = {"limit": MAX_TX}
        if last:
            params["until"] = last
        try:
            sigs = rpc("getSignaturesForAddress", [addr, params])
        except Exception as e:
            print(f"  ! {addr[:6]} signatures failed: {e}")
            continue
        if not sigs:
            continue
        state[addr] = sigs[0]["signature"]
        if not last and not BACKFILL:  # first sight: just a few, unless backfilling
            sigs = sigs[:5]
        for s in reversed(sigs):
            if s.get("err"):
                continue
            try:
                tx = rpc("getTransaction", [s["signature"], {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 1}])
            except Exception as e:
                print(f"  ! tx {s['signature'][:8]} failed: {e}")
                continue
            sw = parse_swap(tx, addr)
            if sw:
                sw.update({"wallet": addr, "tier": w.get("tier", "watch"), "sig": s["signature"],
                           "time": dt.datetime.fromtimestamp(s.get("blockTime") or time.time(), dt.timezone.utc).isoformat()})
                new.append(sw)
            time.sleep(0.15)
        time.sleep(0.2)
    return new


def load_recent_trades(hours):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    out = []
    for f in sorted(TRADES.glob("*.jsonl"))[-3:]:
        for line in f.read_text().splitlines():
            try:
                t = json.loads(line)
            except ValueError:
                continue
            if dt.datetime.fromisoformat(t["time"]) >= cutoff:
                out.append(t)
    return out


def dexscreener(mints):
    info = {}
    for i in range(0, len(mints), 30):
        chunk = mints[i:i + 30]
        try:
            r = session.get("https://api.dexscreener.com/latest/dex/tokens/" + ",".join(chunk), timeout=30).json()
        except Exception:
            continue
        for p in r.get("pairs") or []:
            if p.get("chainId") != "solana":
                continue
            m = p["baseToken"]["address"]
            if m not in chunk:
                continue
            if m not in info or (p.get("liquidity") or {}).get("usd", 0) > (info[m].get("liquidity") or {}).get("usd", 0):
                info[m] = p
    return info


def top10_share(mint):
    try:
        largest = rpc("getTokenLargestAccounts", [mint])["value"][:10]
        supply = float(rpc("getTokenSupply", [mint])["value"]["uiAmount"] or 0)
        held = sum(float(a.get("uiAmount") or 0) for a in largest)
        return round(100 * held / supply, 1) if supply else None
    except Exception:
        return None


def build_signals(trades, sol_price):
    by_mint = {}
    for t in trades:
        if t["side"] != "BUY":
            continue
        g = by_mint.setdefault(t["mint"], {"wallets": {}, "first": t["time"], "sol": 0.0, "usd": 0.0, "tokens": 0.0})
        g["wallets"][t["wallet"]] = t["tier"]
        g["first"] = min(g["first"], t["time"])
        g["sol"] += t["quote_sol"]
        g["usd"] += t["quote_usd"]
        g["tokens"] += t["amount"]
    sells = {}
    for t in trades:
        if t["side"] == "SELL":
            sells.setdefault(t["mint"], set()).add(t["wallet"])
    cands = []
    for mint, g in by_mint.items():
        score = sum(2 if tier == "core" else 1 for tier in g["wallets"].values())
        approx_usd = g["usd"] + g["sol"] * (sol_price or 0)
        if len(g["wallets"]) >= 2 and approx_usd >= MIN_USD:
            cands.append((mint, g, score))
    info = dexscreener([m for m, _, _ in cands]) if cands else {}
    signals = []
    for mint, g, score in cands:
        p = info.get(mint, {})
        price = float(p["priceUsd"]) if p.get("priceUsd") else None
        cost_usd = g["usd"] + (g["sol"] * sol_price if sol_price else 0)
        entry = cost_usd / g["tokens"] if g["tokens"] else None
        since_entry = round(100 * (price / entry - 1), 1) if price and entry else None
        liq = (p.get("liquidity") or {}).get("usd")
        created = p.get("pairCreatedAt")
        age_h = round((time.time() * 1000 - created) / 3.6e6, 1) if created else None
        top10 = top10_share(mint)
        flags = []
        mc = p.get("marketCap") or p.get("fdv")
        if not p:
            flags.append("no DEX pair found")
        elif liq is None:
            flags.append("still on a launch bonding curve (no pool liquidity yet)")
        elif liq < 30000:
            flags.append(f"thin liquidity (${liq:,.0f})")
        if age_h is not None and age_h < 1:
            flags.append("pair younger than 1h")
        if top10 is not None and top10 > 40:
            flags.append(f"top-10 accounts hold {top10}% (includes pools; check on Bubblemaps)")
        if since_entry is not None and since_entry > 100:
            flags.append(f"already +{since_entry}% above smart entries (late)")
        if mc is not None and mc < MIN_MC:
            flags.append(f"micro cap (${mc:,.0f})")
        if mint in sells:
            flags.append(f"{len(sells[mint])} tracked wallet(s) already selling")
        signals.append({
            "mint": mint, "symbol": (p.get("baseToken") or {}).get("symbol"), "name": (p.get("baseToken") or {}).get("name"),
            "wallets": len(g["wallets"]), "core_wallets": sum(1 for t in g["wallets"].values() if t == "core"),
            "score": score, "smart_buy_usd": round(cost_usd, 2), "first_buy": g["first"],
            "avg_entry_usd": entry, "price_usd": price, "change_since_entry_pct": since_entry,
            "liquidity_usd": liq, "market_cap": p.get("marketCap") or p.get("fdv"), "pair_age_h": age_h,
            "volume_24h": (p.get("volume") or {}).get("h24"), "change_1h": (p.get("priceChange") or {}).get("h1"),
            "top10_pct": top10, "red_flags": flags, "dexscreener": p.get("url"),
            "bubblemaps": f"https://app.bubblemaps.io/sol/token/{mint}",
        })
    signals.sort(key=lambda s: (-s["score"], len(s["red_flags"])))
    return signals


def fmt_usd(x):
    if x is None:
        return "?"
    return f"${x:,.0f}" if x >= 1 else f"${x:.8f}".rstrip("0")


def write_outputs(signals, trades, sol_price):
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=3)))
    (SM / "signals.json").write_text(json.dumps({"generated": now.isoformat(timespec="minutes"),
                                                 "window_hours": WINDOW_H, "sol_usd": sol_price,
                                                 "signals": signals}, indent=2))
    buys = sum(t["side"] == "BUY" for t in trades)
    lines = [f"# Smart-money signals — {now:%Y-%m-%d %H:%M} Doha",
             "",
             f"Window: last {WINDOW_H:g}h · {buys} buys and {len(trades) - buys} sells by tracked wallets · "
             f"SOL ≈ {fmt_usd(sol_price)}",
             "",
             "Research only, not financial advice. Convergence = 2+ tracked wallets bought the same token "
             "(core wallets count double). Always check red flags and the Bubblemaps link before anything.",
             ""]
    if not signals:
        lines.append("_No convergence in this window._")
    for s in signals:
        lines += [f"## {s['symbol'] or '?'} — score {s['score']} ({s['wallets']} wallets, {s['core_wallets']} core)",
                  f"- Mint: `{s['mint']}`",
                  f"- Smart money in: {fmt_usd(s['smart_buy_usd'])} since {s['first_buy'][:16].replace('T', ' ')} UTC",
                  f"- Avg smart entry {fmt_usd(s['avg_entry_usd'])} → now {fmt_usd(s['price_usd'])}"
                  f" ({s['change_since_entry_pct'] if s['change_since_entry_pct'] is not None else '?'}% since entry)",
                  f"- Liquidity {fmt_usd(s['liquidity_usd'])} · MC {fmt_usd(s['market_cap'])} · "
                  f"age {s['pair_age_h']}h · 24h vol {fmt_usd(s['volume_24h'])} · 1h {s['change_1h']}% · top-10 {s['top10_pct']}%",
                  f"- Red flags: {', '.join(s['red_flags']) if s['red_flags'] else 'none found by the script'}",
                  f"- {s['dexscreener'] or ''} · {s['bubblemaps']}",
                  ""]
    (SM / "signals.md").write_text("\n".join(lines))


def main():
    SM.mkdir(exist_ok=True)
    TRADES.mkdir(exist_ok=True)
    wallets = [w for w in yaml.safe_load((SM / "wallets.yaml").read_text())["wallets"]
               if w.get("tier") in ("core", "watch")]
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    print(f"Scanning {len(wallets)} wallets via {RPC.split('?')[0]}")
    new = scan_wallets(wallets, state)
    STATE.write_text(json.dumps(state, indent=1))
    if new:
        day = TRADES / f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%d}.jsonl"
        with open(day, "a") as f:
            for t in new:
                f.write(json.dumps(t) + "\n")
    trades = load_recent_trades(WINDOW_H)
    price = sol_usd()
    signals = build_signals(trades, price)
    write_outputs(signals, trades, price)
    print(f"{len(new)} new swaps; {len(trades)} in window; {len(signals)} convergence signals")
    for s in signals[:5]:
        print(f"  {s['symbol']}: {s['wallets']} wallets, score {s['score']}, flags: {len(s['red_flags'])}")


if __name__ == "__main__":
    sys.exit(main())
