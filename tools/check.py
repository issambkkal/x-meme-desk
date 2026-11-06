"""Validate queued posts and show what will go out when.

Usage:  .venv/bin/python tools/check.py            # all files in queue/
        .venv/bin/python tools/check.py FILE ...   # specific files
Exit code 1 if any post has a problem.
"""
import sys

from xlib import Post, load_config, queue_posts, x_length


def main(paths):
    config = load_config()
    bad = 0
    files = paths or queue_posts()
    if not files:
        print("Queue is empty.")
    for path in files:
        try:
            post = Post(path)
            errs = post.problems(config)
        except Exception as e:  # unreadable file
            post, errs = None, [f"cannot read file: {e}"]
        mark = "OK " if not errs else "BAD"
        when = post.meta.get("post_at", "?") if post else "?"
        status = post.status if post else "?"
        sizes = ",".join(str(x_length(t["text"])) for t in post.tweets) if post else ""
        print(f"[{mark}] {when}  {status:<8} chars[{sizes}]  {path if paths else path.name}")
        for e in errs:
            print(f"       - {e}")
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
