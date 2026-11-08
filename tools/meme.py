"""Make original meme-style images for @issam0pc4u (no copyrighted templates needed).

Usage:  python tools/meme.py spec.json
Spec (JSON), "out" relative to the repo root:

  {"layout": "choice", "out": "charts/x.png",
   "title": "Meme coin traders this week",            # optional
   "no": "Reading the chart", "yes": "Reading who's selling"}

  {"layout": "versus", "out": "charts/x.png",
   "left_head": "What CT says", "left": "Bullish. Accumulate.",
   "right_head": "What ETF flows say", "right": "-$840M in 2 days",
   "source": "Farside, Nov 5-6"}                       # optional

  {"layout": "caption", "out": "charts/x.png", "bg": "images/photo.jpg",
   "top": "WHEN THE DEV SAYS", "bottom": "LIQUIDITY IS LOCKED",
   "credit": "Photo: Jane Doe, CC BY-SA 4.0, Wikimedia Commons"}   # required for others' photos

  {"layout": "nobody", "out": "charts/x.png",
   "lines": ["Nobody:", "", "Smart money at +173%:"], "punch": "thanks for the exit liquidity",
   "bg": "charts/some-chart.png"}                      # optional image under the text

  {"layout": "stages", "out": "charts/x.png", "title": "Every meme coin, ever",
   "steps": ["Launch", "\"Next 100x\"", "Insiders sell", "\"Community takeover\"", "-98%"]}

Images: our own charts, our own drawings, or Wikimedia Commons photos with a free licence
(tools/commons.py downloads them and writes the credit). Never random Google images: copyright
claims can get the account suspended.
"""
import json
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chart import BG, GREY, HANDLE, WHITE, font  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
W, H = 1600, 900
RED, GREEN, BLUE, YELLOW = (229, 72, 77), (48, 196, 120), (58, 136, 228), (245, 197, 66)
PANEL = (34, 37, 44)


def fit(draw, text, max_w, max_h, start=110, weight="Black", spacing=8, min_size=28):
    """Largest font size (and wrapped text) that fits the box."""
    for size in range(start, min_size - 1, -4):
        f = font(size, weight)
        avg = max(1, draw.textlength("abcdefghijklmnopqrstuvwxyz", font=f) / 26)
        cols = max(4, int(max_w / avg))
        wrapped = "\n".join(textwrap.fill(p, cols) if p else "" for p in text.split("\n"))
        box = draw.multiline_textbbox((0, 0), wrapped, font=f, spacing=spacing)
        if box[2] - box[0] <= max_w and box[3] - box[1] <= max_h:
            return f, wrapped
    f = font(min_size, weight)
    return f, textwrap.fill(text, 40)


def text_in_box(draw, text, box, color=WHITE, start=110, weight="Black", align="center", stroke=0):
    x0, y0, x1, y1 = box
    f, wrapped = fit(draw, text, x1 - x0, y1 - y0, start, weight)
    bb = draw.multiline_textbbox((0, 0), wrapped, font=f, spacing=8, stroke_width=stroke)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = x0 + ((x1 - x0) - tw) / 2 if align == "center" else x0
    y = y0 + ((y1 - y0) - th) / 2 - bb[1]
    draw.multiline_text((x, y), wrapped, font=f, fill=color, spacing=8, align=align,
                        stroke_width=stroke, stroke_fill=(0, 0, 0))


def footer(draw, source=None, credit=None, w=W, h=H, dark=True):
    col = GREY if dark else (90, 90, 90)
    f = font(24, "Medium")
    draw.text((40, h - 46), HANDLE, font=f, fill=col)
    note = " · ".join(x for x in (source, credit) if x)
    if note:
        draw.text((w - 40, h - 46), note, font=f, fill=col, anchor="ra")


def icon(draw, box, kind):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, 28, fill=RED if kind == "no" else GREEN)
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) * 0.26
    if kind == "no":
        draw.line((cx - r, cy - r, cx + r, cy + r), fill=WHITE, width=26)
        draw.line((cx - r, cy + r, cx + r, cy - r), fill=WHITE, width=26)
    else:
        draw.line((cx - r, cy + 2, cx - r * 0.25, cy + r * 0.8, cx + r * 1.05, cy - r * 0.8), fill=WHITE, width=26, joint="curve")


def choice(s):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    top = 70
    if s.get("title"):
        text_in_box(d, s["title"], (60, 30, W - 60, 130), start=64, weight="Bold")
        top = 150
    row = (H - top - 80) // 2
    for i, key in enumerate(("no", "yes")):
        y0 = top + i * row + 10
        d.rounded_rectangle((60, y0, W - 60, y0 + row - 20), 30, fill=PANEL)
        icon(d, (90, y0 + 30, 90 + row - 80, y0 + row - 50), key)
        text_in_box(d, s[key], (90 + row - 40, y0 + 25, W - 100, y0 + row - 45),
                    color=WHITE if key == "yes" else (200, 204, 210), start=86, weight="Heavy", align="left")
    footer(d, s.get("source"))
    return img


def versus(s):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    half = (W - 150) // 2
    for i, side in enumerate(("left", "right")):
        x0 = 60 + i * (half + 30)
        col = RED if i == 0 else GREEN
        d.rounded_rectangle((x0, 60, x0 + half, H - 90), 30, fill=PANEL)
        d.rounded_rectangle((x0, 60, x0 + half, 170), 30, fill=col)
        d.rectangle((x0, 140, x0 + half, 170), fill=col)
        text_in_box(d, s[f"{side}_head"], (x0 + 30, 70, x0 + half - 30, 160), start=56, weight="Bold")
        text_in_box(d, s[side], (x0 + 40, 200, x0 + half - 40, H - 130), start=120, weight="Black")
    footer(d, s.get("source"))
    return img


def cover(path, w, h):
    im = Image.open(ROOT / path).convert("RGB")
    return ImageOps.fit(im, (w, h), Image.LANCZOS)


def caption(s):
    img = cover(s["bg"], W, H)
    shade = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.blend(img, shade, float(s.get("darken", 0.15)))
    d = ImageDraw.Draw(img)
    if s.get("top"):
        text_in_box(d, s["top"].upper(), (60, 30, W - 60, 250), start=110, weight="Black", stroke=7)
    if s.get("bottom"):
        text_in_box(d, s["bottom"].upper(), (60, H - 290, W - 60, H - 70), start=110, weight="Black", stroke=7)
    d.rectangle((0, H - 52, W, H), fill=(0, 0, 0))
    footer(d, s.get("source"), s.get("credit"))
    return img


def nobody(s):
    w = 1200
    lines = "\n".join(s.get("lines", []))
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    f = font(54, "Medium")
    wrapped = "\n".join(textwrap.fill(p, 40) if p else "" for p in lines.split("\n"))
    tb = probe.multiline_textbbox((0, 0), wrapped, font=f, spacing=14)
    pf = font(62, "Heavy")
    punch = textwrap.fill(s.get("punch", ""), 34)
    pb = probe.multiline_textbbox((0, 0), punch, font=pf, spacing=12) if punch else (0, 0, 0, 0)
    pic_h = 0
    if s.get("bg"):
        pic = Image.open(ROOT / s["bg"]).convert("RGB")
        pic = ImageOps.contain(pic, (w - 80, 800))
        pic_h = pic.height + 40
    h = 70 + (tb[3] - tb[1]) + 40 + (pb[3] - pb[1]) + 50 + pic_h + 70
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    y = 60
    d.multiline_text((50, y), wrapped, font=f, fill=(15, 20, 25), spacing=14)
    y += tb[3] - tb[1] + 40
    if punch:
        d.multiline_text((50, y), punch, font=pf, fill=(15, 20, 25), spacing=12)
        y += pb[3] - pb[1] + 50
    if pic_h:
        img.paste(pic, ((w - pic.width) // 2, y))
    footer(d, s.get("source"), s.get("credit"), w=w, h=h, dark=False)
    return img


def stages(s):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text_in_box(d, s.get("title", ""), (60, 30, W - 60, 140), start=70, weight="Black")
    steps = s["steps"]
    n = len(steps)
    gap = 24
    bw = (W - 120 - gap * (n - 1)) / n
    for i, step in enumerate(steps):
        x0 = 60 + i * (bw + gap)
        rise = int((1 - abs(i - (n - 1) * 0.45) / n) * 160)
        col = GREEN if i < n // 2 else (YELLOW if i == n // 2 else RED)
        y0 = 250 - rise + 120
        d.rounded_rectangle((x0, y0, x0 + bw, H - 120), 24, fill=PANEL, outline=col, width=6)
        d.text((x0 + bw / 2, y0 + 40), str(i + 1), font=font(60, "Black"), fill=col, anchor="mt")
        text_in_box(d, step, (x0 + 18, y0 + 130, x0 + bw - 18, H - 150), start=58, weight="Heavy")
    footer(d, s.get("source"))
    return img


LAYOUTS = {"choice": choice, "versus": versus, "caption": caption, "nobody": nobody, "stages": stages}


def main():
    spec = json.loads(Path(sys.argv[1]).read_text())
    img = LAYOUTS[spec["layout"]](spec)
    out = ROOT / spec["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
