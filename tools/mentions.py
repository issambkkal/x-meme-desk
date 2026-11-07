"""Read new mentions/replies to @issam0pc4u and keep the conversation going 24/7.

- Simple asks under our posts ("CA?", "link?", "telegram?") get an instant varied answer
  pointing to the free Telegram (link in bio).
- Everything genuine that needs a real answer goes to mentions/inbox.json, which the
  3-hour cloud drafting routine answers (queue files with `type: reply`).
- Spam, bots, giveaways and promo pitches are ignored.

Only people who mention us or reply to our posts are answered: X allows automated replies
to users who interact with you, and the API refuses anything else.

Run from the poster loop (needs the X keys in .env). Cheap: one owned-read call per run,
billed per returned post.
"""
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "mentions"
STATE = DIR / "state.json"
INBOX = DIR / "inbox.json"
QUEUE = ROOT / "queue"
DOHA = dt.timezone(dt.timedelta(hours=3))
INSTANT_PER_DAY = 25

SPAM = re.compile(r"whatsapp|wa\.me|giveaway|airdrop|dm me|dm for|inbox me|promo|promotion|collab|"
                  r"shill|send (me )?\$|t\.me/(?!\+o9SNT45tLN8zODE0)|pump it|100x gem|join my|"
                  r"follow back|f4f|recovery|hacked|fund(s)? recover", re.I)
ASK_TG = re.compile(r"\b(ca|contract|address|mint|link|tg|telegram|group|join|where can|how (do|to) (i )?join|signals?)\b", re.I)
PRAISE = re.compile(r"^(thanks?|thank you|thx|ty|great|nice|good (one|stuff|call|work)|fire|facts|true|agreed|"
                    r"based|love (this|it)|solid|valuable|helpful|this is gold|underrated|great thread|"
                    r"🔥|💯|🙏|👏|💪)[\s!.🔥💯🙏👏💪]*$", re.I)

ANSWERS_TG = [
    "The CA, chart and live updates are in my free Telegram, imbi MOON. Link is in my bio 🌕",
    "Everything's in the free Telegram (link in bio): CA, entry vs now, red flags, updates as wallets sell.",
    "I keep the contract and live updates in the Telegram so they don't go stale here. Free, link in my bio.",
    "Link's in my bio: imbi MOON on Telegram. The bot posts the CA and the moment the smart wallets start selling.",
    "Free Telegram, link in bio. CA + live tracking there. Always check holders before touching anything.",
]
ANSWERS_THANKS = [
    "Appreciate it 🙏 More of these every day, and the live ones go to Telegram first.",
    "Thanks! I post what the smart wallets actually do, receipts included.",
    "Glad it helped. Follow along, the tracker never sleeps 🌕",
    "🙏 Data over vibes. More coming.",
    "Thank you! If you want them live, the Telegram link is in my bio.",
]


def load(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def pick(options, key):
    return options[int(hashlib.sha1(key.encode()).hexdigest(), 16) % len(options)]


def clean(text):
    return re.sub(r"(^|\s)@\w+", " ", text).strip()


def classify(text, author, my_id, convo_is_ours):
    body = clean(text)
    if SPAM.search(text) or not body:
        return "spam"
    if convo_is_ours and len(body) <= 120 and ASK_TG.search(body) and "?" in body or (
            convo_is_ours and re.fullmatch(r"(ca|link|tg|telegram|contract)\s*\??", body, re.I)):
        return "ask_tg"
    if convo_is_ours and PRAISE.match(body):
        return "thanks"
    return "inbox"


def queue_reply(tid, text, now):
    name = f"{now:%Y-%m-%d-%H%M}-reply-{tid}.md"
    (QUEUE / name).write_text(
        "---\n"
        f"type: reply\nreply_to: {tid}\npost_at: {now:%Y-%m-%d %H:%M}\nstatus: ready\nfast: true\n"
        f"max_delay_minutes: 240\nqueued_at: {now:%Y-%m-%d %H:%M}\n"
        "---\n" + text + "\n")
    return name


def main():
    load_dotenv(ROOT / ".env")
    keys = [os.environ.get(k) for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET")]
    if not all(keys):
        return print("mentions: no X keys, skipping")
    import tweepy
    client = tweepy.Client(consumer_key=keys[0], consumer_secret=keys[1],
                           access_token=keys[2], access_token_secret=keys[3])
    DIR.mkdir(exist_ok=True)
    state = load(STATE, {})
    if not state.get("my_id"):
        me = client.get_me(user_auth=True).data
        state["my_id"], state["username"] = str(me.id), me.username
    my_id = state["my_id"]
    kwargs = dict(id=my_id, max_results=50, user_auth=True,
                  tweet_fields=["created_at", "conversation_id", "author_id", "in_reply_to_user_id", "referenced_tweets"],
                  expansions=["author_id", "referenced_tweets.id"], user_fields=["username", "public_metrics"])
    if state.get("since_id"):
        kwargs["since_id"] = state["since_id"]
    else:
        kwargs["start_time"] = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
    resp = client.get_users_mentions(**kwargs)
    tweets = resp.data or []
    users = {str(u.id): u for u in (resp.includes or {}).get("users", [])}
    refs = {str(t.id): t for t in (resp.includes or {}).get("tweets", [])}
    now = dt.datetime.now(DOHA).replace(second=0, microsecond=0, tzinfo=None)
    day = now.strftime("%Y-%m-%d")
    counts = state.setdefault("instant", {})
    inbox = load(INBOX, [])
    seen = {m["id"] for m in inbox}
    log = []
    for t in sorted(tweets, key=lambda t: t.id):
        tid, aid = str(t.id), str(t.author_id)
        state["since_id"] = tid
        if aid == my_id or tid in seen:
            continue
        u = users.get(aid)
        handle = u.username if u else aid
        followers = (u.public_metrics or {}).get("followers_count", 0) if u else 0
        parents = [refs.get(str(r.id)) for r in (getattr(t, "referenced_tweets", None) or []) if r.type == "replied_to"]
        convo_is_ours = str(getattr(t, "in_reply_to_user_id", "") or "") == my_id or any(
            p is not None and str(getattr(p, "author_id", "")) == my_id for p in parents)
        kind = classify(t.text, aid, my_id, convo_is_ours)
        action = kind
        if kind in ("ask_tg", "thanks") and counts.get(day, 0) < INSTANT_PER_DAY:
            text = pick(ANSWERS_TG if kind == "ask_tg" else ANSWERS_THANKS, tid)
            queue_reply(tid, text, now)
            counts[day] = counts.get(day, 0) + 1
            action = f"answered ({kind})"
        elif kind != "spam":
            inbox.append({"id": tid, "url": f"https://x.com/{handle}/status/{tid}", "author": handle,
                          "followers": followers, "text": t.text, "created_at": str(t.created_at),
                          "conversation_id": str(t.conversation_id), "replying_to_us": convo_is_ours,
                          "handled": False})
            action = "inbox"
        log.append(f"- {now:%H:%M} @{handle} ({followers} followers): {action} — {t.text[:140]!r}")
    inbox = [m for m in inbox if not m.get("handled")][-60:] + [m for m in inbox if m.get("handled")][-40:]
    INBOX.write_text(json.dumps(inbox, indent=1, ensure_ascii=False))
    state["instant"] = {d: c for d, c in counts.items() if d >= (now - dt.timedelta(days=3)).strftime("%Y-%m-%d")}
    STATE.write_text(json.dumps(state, indent=1))
    if log:
        with open(DIR / f"{day}.md", "a") as f:
            f.write("\n".join(log) + "\n")
    print(f"mentions: {len(tweets)} new, {sum('answered' in l for l in log)} answered instantly, "
          f"{sum(': inbox' in l for l in log)} to inbox")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # never break the poster loop
        print(f"mentions step skipped: {e}", file=sys.stderr)
