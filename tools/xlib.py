"""Shared helpers: paths, config, queue file parsing, X character counting."""
import datetime as dt
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "queue"
POSTED = ROOT / "posted"
FAILED = ROOT / "failed"
LOGS = ROOT / "logs"
ANALYTICS = ROOT / "analytics"

TWEET_SPLIT = re.compile(r"^\s*===\s*$", re.M)
IMAGE_TAG = re.compile(r"^\s*\[image:\s*(.+?)\s*\]\s*$", re.M)
URL = re.compile(r"https?://\S+")
CASHTAG = re.compile(r"\$[A-Za-z][A-Za-z0-9_]*")
BARE_DOMAIN = re.compile(r"(?<![@\w$])[A-Za-z0-9-]+\.(?:fun|io|xyz|com|app|so|ai|net|org|gg|trade|finance|exchange|money|wtf|co|me|tv)\b", re.I)
TIME_FMT = "%Y-%m-%d %H:%M"


def one_cashtag(text):
    """The X API refuses posts with more than one cashtag: keep the first $TICKER, drop the $ on the rest."""
    seen = []
    def fix(m):
        seen.append(1)
        return m.group(0) if len(seen) == 1 else m.group(0)[1:]
    return CASHTAG.sub(fix, text)


def load_config():
    return yaml.safe_load((ROOT / "config.yaml").read_text())


def now():
    return dt.datetime.now().replace(second=0, microsecond=0)


def parse_time(value):
    if isinstance(value, dt.datetime):
        return value.replace(tzinfo=None)
    return dt.datetime.strptime(str(value).strip(), TIME_FMT)


def x_length(text):
    """Approximate X's weighted length: URLs = 23, most Latin chars = 1, emoji/CJK = 2."""
    total = 0
    text = URL.sub(lambda m: "u" * 23, text)
    for ch in text:
        cp = ord(ch)
        if cp == 0xFE0F:  # emoji variation selector adds nothing visible
            continue
        if (cp <= 0x10FF or 0x2000 <= cp <= 0x200D or 0x2010 <= cp <= 0x201F
                or 0x2032 <= cp <= 0x2037):
            total += 1
        else:
            total += 2
    return total


class Post:
    """A queue file: YAML front matter + tweets separated by a line '==='."""

    def __init__(self, path):
        self.path = Path(path)
        raw = self.path.read_text()
        if not raw.startswith("---"):
            raise ValueError("missing front matter (file must start with ---)")
        _, front, body = raw.split("---", 2)
        self.meta = yaml.safe_load(front) or {}
        self.tweets = []
        for i, chunk in enumerate(TWEET_SPLIT.split(body.strip())):
            images = [m.strip() for m in IMAGE_TAG.findall(chunk)]
            text = IMAGE_TAG.sub("", chunk).strip()
            if i == 0 and self.meta.get("image"):
                images.insert(0, self.meta["image"])
            # X turns bare domains like "Pump.fun" into links (less reach, $0.20 API price).
            # Fix them instead of blocking the post: "Pump.fun" -> "Pump fun".
            if not self.meta.get("allow_links"):
                text = BARE_DOMAIN.sub(lambda m: m.group(0).replace(".", " "), text)
            text = one_cashtag(text)
            # X turns bare domains like "Pump.fun" into links (less reach, $0.20 API price).
            # Fix them instead of blocking the post: "Pump.fun" -> "Pump fun".
            if not self.meta.get("allow_links"):
                text = BARE_DOMAIN.sub(lambda m: m.group(0).replace(".", " "), text)
            self.tweets.append({"text": text, "images": images})
        # `tip: true` (or a deep-dive thread with `article:`) adds the tip post from
        # config.yaml as the last post of the thread.
        # X API refuses crypto addresses for the first 7 days after an app is authorized,
        # so config `tip_pause_until: YYYY-MM-DD` holds the tip post back until then.
        cfg = load_config() if (self.meta.get("tip") or self.meta.get("article")) else {}
        paused = str(cfg.get("tip_pause_until") or "") > dt.date.today().isoformat()
        if (self.meta.get("tip") or self.meta.get("article")) and self.kind == "post" and not paused:
            tip = str(cfg.get("tip_post") or "").strip()
            if tip and not any(tip in t["text"] for t in self.tweets):
                self.tweets.append({"text": tip, "images": []})

    @property
    def status(self):
        return str(self.meta.get("status", "draft")).lower()

    @property
    def post_at(self):
        return parse_time(self.meta["post_at"])

    @property
    def queued_at(self):
        q = self.meta.get("queued_at")
        if q:
            return parse_time(q)
        return dt.datetime.fromtimestamp(self.path.stat().st_mtime)

    def image_path(self, rel):
        p = Path(rel).expanduser()
        return p if p.is_absolute() else ROOT / p

    @property
    def kind(self):
        t = str(self.meta.get("type", "post")).lower()
        return t if t in ("repost", "reply") else "post"

    def target(self, key):
        """(username, tweet_id) from a front-matter x.com status URL, or (None, None)."""
        m = STATUS_URL.search(str(self.meta.get(key) or ""))
        return (m.group(1), m.group(2)) if m else (None, None)

    def problems(self, config):
        """Return a list of reasons this post must not go out."""
        errs = []
        if self.meta.get("quote"):
            # X API (pay-per-use) answers 403: "You can only reply to or quote posts where
            # you are mentioned or are the author." Credit the source with an @mention instead.
            errs.append("quote posts are blocked by the X API; remove 'quote:' and credit the "
                        "source in the text (e.g. 'per @bubblemaps')")
        for key in ("repost",):
            if self.meta.get(key):
                user, tid = self.target(key)
                if not tid:
                    errs.append(f"'{key}' must be a full post URL like https://x.com/user/status/123")
                elif user.lower() not in repost_ok_handles():
                    errs.append(f"@{user} is not repost_ok in watchlist.yaml, so it can't be {'quoted' if key == 'quote' else 'reposted'}")
        if self.kind == "reply":
            # A reply to someone who mentioned us or replied to our post (the X API refuses
            # replies to anyone else).
            if not re.fullmatch(r"\d{5,25}", str(self.meta.get("reply_to") or "")):
                errs.append("type: reply needs 'reply_to: <status id>'")
            if self.status not in ("draft", "ready", "approved", "hold"):
                errs.append(f"status must be draft, ready, approved or hold (got {self.status!r})")
            try:
                self.post_at
            except Exception:
                errs.append("post_at must look like 2026-11-07 10:00")
            if len(self.tweets) != 1 or not self.tweets[0]["text"]:
                errs.append("a reply is exactly one non-empty post")
            elif x_length(self.tweets[0]["text"]) > int(config.get("max_chars", 280)):
                errs.append(f"reply is {x_length(self.tweets[0]['text'])} chars")
            if not self.meta.get("allow_links") and any(URL.search(t["text"]) for t in self.tweets):
                errs.append("reply contains a link ($0.20 via the API)")
            return errs
        if self.kind == "repost":
            if not self.meta.get("repost"):
                errs.append("type: repost needs 'repost: <post URL>'")
            if self.status not in ("draft", "ready", "approved", "hold"):
                errs.append(f"status must be draft, ready, approved or hold (got {self.status!r})")
            try:
                self.post_at
            except Exception:
                errs.append("post_at must look like 2026-11-07 10:00")
            return errs
        for key in ("post_at", "status", "sources"):
            if key not in self.meta:
                errs.append(f"missing '{key}' in front matter")
        try:
            self.post_at
        except Exception:
            errs.append(f"post_at must look like 2026-11-07 10:00 (got {self.meta.get('post_at')!r})")
        sources = self.meta.get("sources") or []
        if not sources or not all(URL.match(str(s)) for s in sources):
            errs.append("every post needs 'sources': a list of http(s) URLs backing its numbers")
        if self.status not in ("draft", "ready", "approved", "hold"):
            errs.append(f"status must be draft, ready, approved or hold (got {self.status!r})")
        if not self.tweets or not self.tweets[0]["text"]:
            errs.append("post text is empty")
        if len(self.tweets) > 15:
            errs.append("thread longer than 15 posts")
        limit = int(config.get("max_chars", 280))
        for n, t in enumerate(self.tweets, 1):
            length = x_length(t["text"])
            if length > limit:
                errs.append(f"post {n} is {length} chars (limit {limit})")
            if not t["text"]:
                errs.append(f"post {n} is empty")
            if len(t["images"]) > 4:
                errs.append(f"post {n} has more than 4 images")
            for img in t["images"]:
                if not self.image_path(img).exists():
                    errs.append(f"image not found: {img}")
        if self.tweets and URL.search(self.tweets[0]["text"]):
            errs.append("no links in the first post (put them in a reply under it)")
        # Bare domains like "Pump.fun" are auto-linked by X: the post becomes a link post
        # (less reach, $0.20 API price). Write "Pump fun" / "Pumpfun" instead.
        for n, t in enumerate(self.tweets, 1):
            m = BARE_DOMAIN.search(t["text"])
            if m and not self.meta.get("allow_links"):
                errs.append(f"post {n} contains '{m.group(0)}', which X turns into a link; "
                            f"write it without the dot (e.g. 'Pump fun')")
        # X API bills a post containing a URL at $0.20 instead of $0.015 (13x).
        if not self.meta.get("allow_links") and any(URL.search(t["text"]) for t in self.tweets):
            errs.append("a post contains a link: costs $0.20 via the API instead of $0.015; "
                        "remove it or set allow_links: true")
        return errs


STATUS_URL = re.compile(r"(?:x|twitter)\.com/([A-Za-z0-9_]+)/status/(\d+)")


def repost_ok_handles():
    watch = yaml.safe_load((ROOT / "watchlist.yaml").read_text()) or {}
    return {a["handle"].lower() for section in watch.values() if isinstance(section, list)
            for a in section if isinstance(a, dict) and a.get("repost_ok")}


def queue_posts():
    QUEUE.mkdir(exist_ok=True)
    return sorted(p for p in QUEUE.glob("*.md") if not p.name.startswith("_"))
