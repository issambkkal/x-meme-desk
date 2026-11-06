"""Make a 1600x900 chart image in the @issam0pc4u dark style.

Usage:  .venv/bin/python tools/chart.py spec.json
Spec (JSON):
{
  "type": "bars" | "progress" | "columns" | "stat",
  "title": "Most meme coins die on day one",
  "subtitle": "What happened to 8.98M Pump.fun coins, Nov 2025 to Oct 2026",
  "source": "Data: Bitquery, via crypto.news (Oct 20, 2026)",
  "out": "charts/2026-11-07-memecoins.png",          # relative to x-system/
  "items": [ {"label": "All coins", "value": 100, "text": "100%", "highlight": true}, ... ],
  "max": 100,                                         # optional scale maximum
  "big": "1.5%", "caption": "of meme coins ..."       # only for type "stat"
}
"text" is what is printed next to a bar (defaults to the value).
If any item has "highlight": true, the others are drawn dimmer.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1600, 900
BG = (24, 26, 31)
TRACK = (38, 42, 48)
BAR = (58, 136, 228)
BAR_DIM = (52, 72, 102)
WHITE = (240, 242, 245)
GREY = (150, 156, 164)
MARGIN = 80
# Inter (open font, bundled so charts look the same on the Mac and on cloud servers).
FONT_FILES = [ROOT / "fonts" / "Inter-Variable.ttf", Path("/System/Library/Fonts/SFNS.ttf")]
WEIGHTS = {"Regular": 400, "Medium": 500, "Semibold": 600, "Bold": 700, "Heavy": 800, "Black": 900}
HANDLE = "@issam0pc4u"


def font(size, weight="Regular"):
    for path in FONT_FILES:
        try:
            f = ImageFont.truetype(str(path), size)
        except OSError:
            continue
        axes = f.get_variation_axes()
        values = []
        for a in axes:
            name = a["name"].decode() if isinstance(a["name"], bytes) else a["name"]
            if name.lower() == "weight":
                values.append(WEIGHTS.get(weight, 400))
            elif name.lower().startswith("optical"):
                values.append(min(a["maximum"], max(a["minimum"], size)))
            else:
                values.append(a["default"])
        if axes:
            f.set_variation_by_axes(values)
        return f
    return ImageFont.load_default(size)


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def fit(draw, s, weight, size, max_w, min_size=18):
    """Shrink a font until the string fits max_w."""
    while size > min_size and text_w(draw, s, font(size, weight)) > max_w:
        size -= 2
    return font(size, weight)


def frame(spec):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    title_f = fit(d, spec["title"], "Bold", 64, W - 2 * MARGIN)
    d.text((MARGIN, 22), spec["title"], font=title_f, fill=WHITE)
    if spec.get("subtitle"):
        sub_f = fit(d, spec["subtitle"], "Regular", 30, W - 2 * MARGIN)
        d.text((MARGIN, 96), spec["subtitle"], font=sub_f, fill=GREY)
    handle_f = font(28, "Semibold")
    hw = text_w(d, HANDLE, handle_f)
    d.text((W - MARGIN - hw, 845), HANDLE, font=handle_f, fill=WHITE)
    if spec.get("source"):
        src_f = fit(d, spec["source"], "Regular", 22, W - 2 * MARGIN - hw - 40, 14)
        d.text((MARGIN, 850), spec["source"], font=src_f, fill=GREY)
    return img, d


def colour(item, any_highlight):
    return BAR if (not any_highlight or item.get("highlight")) else BAR_DIM


def scale_max(spec):
    return float(spec.get("max") or max(float(i["value"]) for i in spec["items"]) or 1)


def label_text(item):
    return str(item.get("text", item["value"]))


def draw_bars(spec, d):
    """Horizontal bars: label left, bar, value right."""
    items, top, bottom = spec["items"], 170, 800
    hl = any(i.get("highlight") for i in items)
    row = (bottom - top) / len(items)
    bar_h = min(56, row * 0.55)
    size = int(min(36, row * 0.45))
    lab_f, val_f = font(size, "Semibold"), font(size, "Semibold")
    lab_w = max(text_w(d, i["label"], lab_f) for i in items)
    val_w = max(text_w(d, label_text(i), val_f) for i in items)
    x0 = MARGIN + lab_w + 14
    span = W - MARGIN - x0 - val_w - 16
    m = scale_max(spec)
    for n, it in enumerate(items):
        cy = top + row * n + row / 2
        d.text((x0 - 14, cy), it["label"], font=lab_f, fill=WHITE, anchor="rm")
        bw = max(6, span * float(it["value"]) / m)
        d.rectangle([x0, cy - bar_h / 2, x0 + bw, cy + bar_h / 2], fill=colour(it, hl))
        d.text((x0 + bw + 14, cy), label_text(it), font=val_f, fill=WHITE, anchor="lm")


def draw_progress(spec, d):
    """Full-width tracks with the label above each bar."""
    items, top, bottom = spec["items"], 240, 790
    hl = any(i.get("highlight") for i in items)
    row = (bottom - top) / len(items)
    bar_h = min(78, row * 0.42)
    lab_f, val_f = font(int(min(36, row * 0.2)), "Semibold"), font(44, "Semibold")
    val_w = max(text_w(d, label_text(i), val_f) for i in items)
    x0, x1 = MARGIN, W - MARGIN - val_w - 24
    m = scale_max(spec)
    for n, it in enumerate(items):
        y = top + row * n
        d.text((x0, y), it["label"], font=lab_f, fill=WHITE, anchor="lt")
        by = y + row * 0.32
        d.rectangle([x0, by, x1, by + bar_h], fill=TRACK)
        bw = max(6, (x1 - x0) * float(it["value"]) / m)
        d.rectangle([x0, by, x0 + bw, by + bar_h], fill=colour(it, hl))
        d.text((x1 + 20, by + bar_h / 2), label_text(it), font=val_f, fill=WHITE, anchor="lm")


def draw_columns(spec, d):
    """Vertical columns, e.g. a value per year."""
    items, top, base = spec["items"], 200, 770
    hl = any(i.get("highlight") for i in items)
    n = len(items)
    slot = (W - 2 * MARGIN) / n
    col_w = min(150, slot * 0.62)
    lab_f = font(int(min(30, slot * 0.22)), "Semibold")
    val_f = font(int(min(34, slot * 0.24)), "Semibold")
    m = scale_max(spec)
    d.line([MARGIN, base, W - MARGIN, base], fill=TRACK, width=2)
    for k, it in enumerate(items):
        cx = MARGIN + slot * k + slot / 2
        h = max(4, (base - top - 50) * float(it["value"]) / m)
        d.rectangle([cx - col_w / 2, base - h, cx + col_w / 2, base], fill=colour(it, hl))
        d.text((cx, base - h - 12), label_text(it), font=val_f, fill=WHITE, anchor="ms")
        d.text((cx, base + 14), it["label"], font=lab_f, fill=GREY, anchor="mt")


def draw_stat(spec, d):
    """One huge number with a caption."""
    big_f = fit(d, spec["big"], "Heavy", 260, W - 2 * MARGIN)
    d.text((W / 2, 440), spec["big"], font=big_f, fill=BAR, anchor="mm")
    if spec.get("caption"):
        cap_f = fit(d, spec["caption"], "Semibold", 48, W - 2 * MARGIN)
        d.text((W / 2, 640), spec["caption"], font=cap_f, fill=WHITE, anchor="mm")


DRAW = {"bars": draw_bars, "progress": draw_progress, "columns": draw_columns, "stat": draw_stat}


def render(spec):
    kind = spec.get("type", "bars")
    if kind not in DRAW:
        raise SystemExit(f"unknown type {kind!r}; use one of {', '.join(DRAW)}")
    if kind != "stat" and not spec.get("items"):
        raise SystemExit("spec needs 'items'")
    img, d = frame(spec)
    DRAW[kind](spec, d)
    out = Path(spec.get("out", "charts/chart.png"))
    out = out if out.is_absolute() else ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(render(json.loads(Path(sys.argv[1]).read_text())))
