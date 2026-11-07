"""Post the next due item from queue/ to X. Run every 15 minutes by launchd.

Usage:  .venv/bin/python tools/poster.py            # normal run (posts at most one item)
        .venv/bin/python tools/poster.py --dry-run  # show what would be posted, change nothing
        .venv/bin/python tools/poster.py --status   # show the queue and today's count

A post goes out only when ALL of these hold:
  - status is "ready" (mode: auto) or "approved" (mode: approve/auto)
  - post_at is now or in the past (but not more than 12 hours ago: stale posts are skipped)
  - it has waited min_lead_minutes since it was queued (your window to delete it or set hold)
  - today's count is under max_posts_per_day and the last post was min_gap_minutes ago
  - tools/check.py finds no problems (sources, length, images, no link in post 1)
"""
import csv
import datetime as dt
import fcntl
import json
import os
import shutil
import sys
import time

from dotenv import load_dotenv

from xlib import ANALYTICS, FAILED, LOGS, POSTED, ROOT, Post, load_config, now, queue_posts

STALE_HOURS = 12
KEYS = ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET")


def log(msg):
    LOGS.mkdir(exist_ok=True)
    line = f"{dt.datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line)
    with open(LOGS / "poster.log", "a") as f:
        f.write(line + "\n")


def history(kind="post"):
    """Times of items already published (from posted/*.json), for one kind: post or repost."""
    times = []
    for p in POSTED.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            if data.get("kind", "post") == kind:
                times.append(dt.datetime.fromisoformat(data["posted_at"]))
        except Exception:
            pass
    return sorted(times)


def limits(config, kind):
    if kind == "reply":
        return int(config.get("max_replies_per_day", 40)), 0
    if kind == "repost":
        return int(config.get("max_reposts_per_day", 2)), int(config.get("min_repost_gap_minutes", 60))
    return int(config.get("max_posts_per_day", 4)), int(config.get("min_gap_minutes", 120))


def blocked(config, kind, t):
    """Reason the daily cap or spacing blocks this kind right now, or None."""
    cap, gap = limits(config, kind)
    done = history(kind)
    if sum(d.date() == t.date() for d in done) >= cap:
        return f"daily {kind} limit {cap} reached"
    if done and t - done[-1] < dt.timedelta(minutes=gap):
        return f"last {kind} was under {gap} min ago"
    return None


def eligible(post, config, t):
    allowed = {"approved"} if config.get("mode") == "approve" else {"ready", "approved"}
    if post.status not in allowed:
        return f"status {post.status}"
    if post.post_at > t:
        return f"scheduled for {post.post_at:%Y-%m-%d %H:%M}"
    if t - post.post_at > dt.timedelta(hours=STALE_HOURS):
        return "stale"
    # Time-sensitive items (live smart-money signals) give up instead of going out late.
    if post.meta.get("max_delay_minutes") and t - post.post_at > dt.timedelta(minutes=int(post.meta["max_delay_minutes"])):
        return "stale"
    lead = dt.timedelta(minutes=int(config.get("min_lead_minutes", 60)))
    if not post.meta.get("fast") and t - post.queued_at < lead:
        return f"waiting for review window until {post.queued_at + lead:%H:%M}"
    return None


class XClient:
    def __init__(self):
        import tweepy
        from requests_oauthlib import OAuth1Session

        k = {name: os.environ[name] for name in KEYS}
        self.client = tweepy.Client(
            consumer_key=k["X_API_KEY"], consumer_secret=k["X_API_SECRET"],
            access_token=k["X_ACCESS_TOKEN"], access_token_secret=k["X_ACCESS_TOKEN_SECRET"])
        self.oauth = OAuth1Session(k["X_API_KEY"], k["X_API_SECRET"],
                                   k["X_ACCESS_TOKEN"], k["X_ACCESS_TOKEN_SECRET"])
        self.v1 = tweepy.API(tweepy.OAuth1UserHandler(
            k["X_API_KEY"], k["X_API_SECRET"], k["X_ACCESS_TOKEN"], k["X_ACCESS_TOKEN_SECRET"]))

    def upload(self, path):
        # v2 media upload first; fall back to the older v1.1 endpoint.
        with open(path, "rb") as f:
            r = self.oauth.post("https://api.x.com/2/media/upload",
                                files={"media": f}, data={"media_category": "tweet_image"})
        if r.ok:
            data = r.json().get("data", r.json())
            media_id = data.get("id") or data.get("media_id_string")
            if media_id:
                return str(media_id)
        log(f"  v2 media upload failed ({r.status_code}: {r.text[:200]}), trying v1.1")
        return str(self.v1.media_upload(filename=str(path)).media_id)

    def tweet(self, text, media_ids, reply_to, quote=None):
        resp = self.client.create_tweet(text=text, media_ids=media_ids or None,
                                        in_reply_to_tweet_id=reply_to, quote_tweet_id=quote,
                                        user_auth=True)
        return str(resp.data["id"])

    def repost(self, tweet_id):
        self.client.retweet(tweet_id, user_auth=True)
        return str(tweet_id)


def publish(post, client, dry):
    if post.kind == "repost":
        user, tid = post.target("repost")
        if dry:
            log(f"  [dry-run] repost @{user} {tid}")
            return []
        client.repost(tid)
        log(f"  reposted https://x.com/{user}/status/{tid}")
        return [tid]
    quote = post.target("quote")[1]
    # `continue_thread: <status id>` finishes a thread that broke midway: the first post
    # replies to the last post that went out.
    first = post.meta.get("continue_thread") or post.meta.get("reply_to")
    ids, reply_to = [], (str(first) if first else None)
    for n, t in enumerate(post.tweets, 1):
        imgs = [post.image_path(i) for i in t["images"]]
        if dry:
            log(f"  [dry-run] post {n}/{len(post.tweets)} ({len(imgs)} image(s)): "
                + t["text"].replace("\n", " / ")[:120])
            continue
        try:
            media = [client.upload(p) for p in imgs]
            reply_to = client.tweet(t["text"], media, reply_to, quote if n == 1 else None)
        except Exception as e:
            e.partial_ids = ids  # thread broke midway: keep what already went out
            raise
        ids.append(reply_to)
        log(f"  posted {n}/{len(post.tweets)} -> https://x.com/i/status/{reply_to}")
        if n < len(post.tweets):
            time.sleep(3)
    return ids


def record(post, ids, posted_at):
    POSTED.mkdir(exist_ok=True)
    dest = POSTED / post.path.name
    shutil.move(str(post.path), dest)
    meta = {k: (str(v) if isinstance(v, (dt.date, dt.datetime)) else v) for k, v in post.meta.items()}
    (POSTED / (post.path.stem + ".json")).write_text(json.dumps({
        "file": dest.name, "kind": post.kind, "posted_at": posted_at.isoformat(timespec="minutes"),
        "tweet_ids": ids, "url": f"https://x.com/i/status/{ids[0]}",
        "meta": meta, "first_text": post.tweets[0]["text"],
    }, indent=2, ensure_ascii=False))
    if post.kind in ("repost", "reply"):
        return
    ANALYTICS.mkdir(exist_ok=True)
    csv_path = ANALYTICS / "posts.csv"
    new = not csv_path.exists()
    with open(csv_path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["posted_at", "tweet_id", "pillar", "has_image", "thread_len",
                        "chars", "text", "views", "likes", "replies", "reposts",
                        "bookmarks", "checked_at"])
        w.writerow([posted_at.isoformat(timespec="minutes"), ids[0], post.meta.get("pillar", ""),
                    int(any(t["images"] for t in post.tweets)), len(post.tweets),
                    len(post.tweets[0]["text"]), post.tweets[0]["text"].replace("\n", " / "),
                    "", "", "", "", "", ""])


def fail(post, err):
    FAILED.mkdir(exist_ok=True)
    shutil.move(str(post.path), FAILED / post.path.name)
    (FAILED / (post.path.stem + ".error.txt")).write_text(str(err))
    log(f"  FAILED {post.path.name}: {err}  (moved to failed/)")


def status(config):
    t = now()
    for kind in ("post", "repost"):
        done = history(kind)
        cap, _ = limits(config, kind)
        today = sum(d.date() == t.date() for d in done)
        print(f"{kind}s today: {today}/{cap}  last: {done[-1] if done else 'never'}")
    print(f"mode={config.get('mode')}")
    for path in queue_posts():
        try:
            post = Post(path)
            why = (post.problems(config) or [eligible(post, config, t)
                   or blocked(config, post.kind, t) or "DUE NOW"])
        except Exception as e:
            why = [f"unreadable: {e}"]
        print(f"  {path.name}: {why[0]}")


def main():
    args = set(sys.argv[1:])
    config = load_config()
    load_dotenv(ROOT / ".env")
    if "--status" in args:
        return status(config)

    LOGS.mkdir(exist_ok=True)
    lock = open(LOGS / ".poster.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return log("another poster run is active, exiting")

    has_keys = all(os.environ.get(k) for k in KEYS)
    dry = "--dry-run" in args or bool(config.get("dry_run")) or not has_keys
    t = now()

    acted, replies = set(), 0
    for path in queue_posts():
        try:
            post = Post(path)
        except Exception as e:
            log(f"skip {path.name}: unreadable ({e})")
            continue
        if post.kind == "reply":
            # Answers to people who talk to us: up to 4 per run, no spacing, daily cap only.
            if replies >= 4 or eligible(post, config, t) or blocked(config, "reply", t):
                continue
            replies += 1
        elif post.kind in acted or eligible(post, config, t) or (
                not (post.meta.get("continue_thread") or post.meta.get("fast")) and blocked(config, post.kind, t)):
            continue
        errs = post.problems(config)
        if errs:
            log(f"skip {path.name}: " + "; ".join(errs))
            continue
        log(f"{'DRY-RUN ' if dry else ''}posting {path.name}"
            + ("" if has_keys else "  (no X keys in .env yet)"))
        if post.kind != "reply":
            acted.add(post.kind)
        if dry:
            publish(post, None, True)
            continue
        try:
            ids = publish(post, XClient(), False)
            record(post, ids, t)
        except Exception as e:
            partial = getattr(e, "partial_ids", None)
            if partial:
                log(f"  thread stopped after {len(partial)} post(s): {e}")
                record(post, partial, t)
            else:
                fail(post, e)
                acted.discard(post.kind)  # nothing went out: let the next due item try
        # at most one post and one repost per run


if __name__ == "__main__":
    main()
