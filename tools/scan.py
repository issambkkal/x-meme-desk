"""Search X for fresh posts from the watchlist accounts and save them to scans/<date>.md.

Usage:  .venv/bin/python tools/scan.py            # one run (alternates between account groups)
        .venv/bin/python tools/scan.py --budget   # show today's API reads and cost

Costs $0.005 per post returned (X pay-per-use). Stops at scan_max_reads_per_day from config.yaml.
Read-only: never likes, follows, replies or posts.
"""
import csv
import datetime as dt
import json
import os
import sys

import yaml
from dotenv import load_dotenv

from xlib import LOGS, ROOT, load_config

SCANS = ROOT / "scans"
STATE = LOGS / "scan_state.json"
SPEND = LOGS / "api_spend.csv"
COST_PER_READ = 0.005
MAX_QUERY = 512
GROUPS = {
    # sleuths + on-chain trackers: everything they post is relevant, no keyword filter
    "alerts": {"sections": ["sleuths", "onchain"], "keywords": False},
    # news, platforms and big traders: only meme-related posts
    "news": {"sections": ["news", "platforms", "traders"], "keywords": True},
    # global economy, finance, industry and politics: only posts that touch crypto-moving topics
    # (2026-11-07: no keyword gate any more: economy and politics are topics in their own right)
    "macro": {"sections": ["macro"], "keywords": False},
    # politics, world events and big business news
    "world": {"sections": ["world"], "keywords": False},
}
# Weighted rotation (2026-11-08): news moves fastest in world/macro, so they get 2 of every 6 runs each.
ORDER = ["world", "macro", "alerts", "world", "macro", "news"]


def spent_today():
    if not SPEND.exists():
        return 0
    today = dt.date.today().isoformat()
    with open(SPEND) as f:
        return sum(int(r["reads"]) for r in csv.DictReader(f) if r["date"] == today)


def log_spend(kind, reads):
    new = not SPEND.exists()
    with open(SPEND, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["date", "time", "kind", "reads", "cost_usd"])
        w.writerow([dt.date.today().isoformat(), dt.datetime.now().strftime("%H:%M"), kind,
                    reads, f"{reads * COST_PER_READ:.3f}"])


def build_query(watch, group):
    handles = [a["handle"] for s in group["sections"] for a in watch.get(s, [])]
    q = "(" + " OR ".join(f"from:{h}" for h in handles) + ") -is:retweet -is:reply"
    if group["keywords"]:
        words = []
        for k in watch.get(group.get("keyword_list", "keywords"), []):
            term = f'"{k}"' if " " in k or "$" in k or "." in k else k
            trial = q + " (" + " OR ".join(words + [term]) + ")"
            if len(trial) > MAX_QUERY:
                break
            words.append(term)
        q += " (" + " OR ".join(words) + ")"
    return q[:MAX_QUERY]


def client():
    import tweepy
    k = {n: os.environ[n] for n in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET")}
    return tweepy.Client(consumer_key=k["X_API_KEY"], consumer_secret=k["X_API_SECRET"],
                         access_token=k["X_ACCESS_TOKEN"], access_token_secret=k["X_ACCESS_TOKEN_SECRET"])


def main():
    load_dotenv(ROOT / ".env")
    LOGS.mkdir(exist_ok=True)
    SCANS.mkdir(exist_ok=True)
    config = load_config()
    cap = int(config.get("scan_max_reads_per_day", 60))
    per_run = max(10, min(100, int(config.get("scan_reads_per_run", 10))))
    used = spent_today()
    if "--budget" in sys.argv:
        print(f"Reads today: {used}/{cap}  (${used * COST_PER_READ:.2f} of ${cap * COST_PER_READ:.2f})")
        return
    if used + per_run > cap:
        print(f"Daily read budget reached ({used}/{cap}); skipping scan.")
        return

    watch = yaml.safe_load((ROOT / "watchlist.yaml").read_text())
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    step = int(state.get("step", -1)) + 1
    name = ORDER[step % len(ORDER)]
    query = build_query(watch, GROUPS[name])

    kwargs = dict(query=query, max_results=per_run, user_auth=True,
                  tweet_fields=["created_at", "public_metrics", "author_id"],
                  expansions=["author_id"], user_fields=["username"])
    if state.get(f"since_{name}"):
        kwargs["since_id"] = state[f"since_{name}"]
    resp = client().search_recent_tweets(**kwargs)
    tweets = resp.data or []
    log_spend(f"scan:{name}", len(tweets))
    users = {u.id: u.username for u in (resp.includes or {}).get("users", [])}

    state["last_group"] = name
    state["step"] = step % len(ORDER)
    if tweets:
        state[f"since_{name}"] = str(max(int(t.id) for t in tweets))
    STATE.write_text(json.dumps(state, indent=2))

    out = SCANS / f"{dt.date.today().isoformat()}.md"
    tweets.sort(key=lambda t: -(t.public_metrics or {}).get("like_count", 0))
    with open(out, "a") as f:
        f.write(f"\n## {dt.datetime.now():%H:%M} scan: {name} ({len(tweets)} new)\n\n")
        for t in tweets:
            m = t.public_metrics or {}
            user = users.get(t.author_id, "?")
            f.write(f"- @{user} · {t.created_at:%Y-%m-%d %H:%M} UTC · "
                    f"{m.get('like_count', 0)} likes, {m.get('retweet_count', 0)} reposts, "
                    f"{m.get('reply_count', 0)} replies, {m.get('impression_count', 0)} views\n"
                    f"  https://x.com/{user}/status/{t.id}\n"
                    f"  > " + t.text.replace("\n", "\n  > ") + "\n\n")
    print(f"{name}: {len(tweets)} new posts -> {out.relative_to(ROOT)}  "
          f"(reads today {used + len(tweets)}/{cap}, ${(used + len(tweets)) * COST_PER_READ:.2f})")


if __name__ == "__main__":
    main()
