"""Find and download a freely licensed photo from Wikimedia Commons, with its credit line.

Usage:  python tools/commons.py "Warren Buffett" [--n 5] [--get N]
  Lists the top results with licence; --get N downloads result N to images/<slug>.jpg and
  writes images/<slug>.json with the credit to put in the meme spec ("credit").
Only public-domain, CC0, CC BY and CC BY-SA files are accepted. Needs internet access to
commons.wikimedia.org (works on the Mac and GitHub Actions; cloud routines may be blocked).
"""
import json
import re
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "x-meme-desk/1.0 (image credit tool)"}
OK = re.compile(r"^(public domain|pd|cc0|cc[ -]by(-sa)?[ -]?\d)", re.I)


def clean(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def search(q, n=8):
    r = requests.get(API, headers=UA, timeout=30, params={
        "action": "query", "format": "json", "generator": "search", "gsrsearch": f"filetype:bitmap {q}",
        "gsrnamespace": 6, "gsrlimit": n * 2, "prop": "imageinfo", "iiprop": "url|extmetadata|size",
        "iiurlwidth": 1600})
    pages = sorted((r.json().get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        lic = clean(meta.get("LicenseShortName", {}).get("value"))
        if not OK.match(lic):
            continue
        out.append({"title": p["title"], "url": ii.get("thumburl") or ii.get("url"), "license": lic,
                    "author": clean(meta.get("Artist", {}).get("value"))[:80] or "unknown",
                    "page": ii.get("descriptionurl"), "w": ii.get("width"), "h": ii.get("height")})
    return out[:n]


def main():
    q = sys.argv[1]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 6
    res = search(q, n)
    if "--get" not in sys.argv:
        for i, r in enumerate(res):
            print(f"{i}: {r['title']} | {r['license']} | {r['author']} | {r['w']}x{r['h']}")
        return
    r = res[int(sys.argv[sys.argv.index("--get") + 1])]
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
    (ROOT / "images").mkdir(exist_ok=True)
    out = ROOT / "images" / f"{slug}.jpg"
    out.write_bytes(requests.get(r["url"], headers=UA, timeout=60).content)
    credit = f"Photo: {r['author']}, {r['license']}, Wikimedia Commons"
    (ROOT / "images" / f"{slug}.json").write_text(json.dumps({**r, "credit": credit}, indent=1))
    print(out.relative_to(ROOT), "|", credit)


if __name__ == "__main__":
    main()
