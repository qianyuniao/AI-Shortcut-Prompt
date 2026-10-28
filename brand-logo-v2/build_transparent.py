# -*- coding: utf-8 -*-
"""Export a transparent-background PNG pack for AI Shortcut Prompt.

The mark PNGs in assets/ are already RGBA with alpha=0 background; what users
perceive as "white" is either the viewer filling the transparent area or the
brand sheet's old `figure img{background:#fff}`. This script re-exports an
explicitly named, verified-alpha set plus a checkerboard proof sheet.

Geometry (100x100 canvas) - identical to mark.json / build_assets.py:
  ring            circle r=36, stroke 12, structural
  left half solid pieslice r=20 (90deg -> 270deg), primary
  shortcut bar    round-capped bar x 58..72, thickness 11, structural
                  (dropped in the simplified variant)
Mark outer extent: r=36 + stroke/2 = 42  ->  bbox 8..92 (84 units of 100).
"""
import os
from PIL import Image, ImageDraw

BASE = r"D:\02_MyWorkSpace\02_QYN Development Project\09Projects already tested\AI Shortcut Prompt\brand-logo-v2"
ASSETS = os.path.join(BASE, "assets")
OUT = os.path.join(BASE, "png-transparent")
os.makedirs(OUT, exist_ok=True)

PRIMARY = (62, 180, 137)   # #3EB489
STRUCT = (67, 71, 74)      # #43474A
WHITE = (255, 255, 255)

RING_R, RING_W = 36, 12
HALF_R = 20
BAR_X1, BAR_X2, BAR_T = 58, 72, 11
PAD = 8.0                  # transparent margin on each side, in 100-unit canvas


def render(size, simplified=False, mode="color"):
    """Transparent RGBA mark. mode: color | mono | reverse | grayscale."""
    if mode == "mono":
        struct, prim = STRUCT, STRUCT
    elif mode == "reverse":
        struct, prim = WHITE, WHITE
    elif mode == "grayscale":
        struct, prim = STRUCT, (140, 140, 140)
    else:
        struct, prim = STRUCT, PRIMARY

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size / 100.0

    d.ellipse([(50 - RING_R) * s, (50 - RING_R) * s,
               (50 + RING_R) * s, (50 + RING_R) * s],
              outline=struct + (255,), width=max(1, int(round(RING_W * s))))

    d.pieslice([(50 - HALF_R) * s, (50 - HALF_R) * s,
                (50 + HALF_R) * s, (50 + HALF_R) * s],
               start=90, end=270, fill=prim + (255,))

    if not simplified:
        cap = BAR_T / 2.0
        d.rounded_rectangle(
            [((BAR_X1 - cap) * s, (50 - cap) * s),
             ((BAR_X2 + cap) * s, (50 + cap) * s)],
            radius=cap * s, fill=struct + (255,))
    return img


def render_tight(size, simplified=False, mode="color"):
    """Same mark, canvas trimmed to the artwork itself - zero transparent margin.

    The trim box is measured from the real alpha bbox, not assumed: Pillow
    draws the ring stroke inwards, so the artwork is 72 units wide, not 84.
    """
    big = max(size * 3, 240)
    art = render(big, simplified, mode)
    bb = art.getchannel("A").getbbox()
    art = art.crop(bb)
    scale = size / float(max(art.size))
    art = art.resize((max(1, int(round(art.width * scale))),
                      max(1, int(round(art.height * scale)))), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
    return out


made = []


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, optimize=True)
    a = img.getchannel("A")
    made.append((name, img.size, a.getextrema()))
    return p


# --- mark, transparent, padded (recommended: keeps the safe zone) ---
for px in (256, 512, 1024, 2048):
    save(render(px), "aishort-mark-transparent-%dpx.png" % px)

# --- mark, transparent, tight-cropped to the artwork ---
for px in (512, 1024):
    save(render_tight(px), "aishort-mark-transparent-tight-%dpx.png" % px)

# --- colourways ---
save(render(1024, mode="mono"), "aishort-mark-mono-dark-transparent-1024px.png")
save(render(1024, mode="reverse"), "aishort-mark-white-transparent-1024px.png")
save(render(1024, simplified=True), "aishort-mark-simplified-transparent-1024px.png")

# --- lockups (already RGBA; re-exported under an explicit name) ---
for src, dst in (("aishort-logo-horizontal-2048px.png",
                  "aishort-logo-horizontal-transparent-2048px.png"),
                 ("aishort-logo-stacked-1024px.png",
                  "aishort-logo-stacked-transparent-1024px.png")):
    p = os.path.join(ASSETS, src)
    if os.path.exists(p):
        im = Image.open(p).convert("RGBA")
        save(im, dst)


# --- checkerboard proof sheet: proves there is no white plate behind the art ---
def checker(w, h, cell=18, a=(233, 230, 222), b=(255, 255, 255)):
    bg = Image.new("RGB", (w, h), b)
    d = ImageDraw.Draw(bg)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if (x // cell + y // cell) % 2 == 0:
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=a)
    return bg


TILE = 300
PAD2 = 28
variants = [("全彩", render(TILE), None),
            ("单色深灰", render(TILE, mode="mono"), None),
            ("反白", render(TILE, mode="reverse"), (67, 71, 74)),
            ("简化版", render(TILE, simplified=True), None)]
PW = PAD2 + (TILE + PAD2) * len(variants)
board = checker(PW, TILE + PAD2 * 2).convert("RGBA")
x = PAD2
for label, im, plate in variants:
    if plate:
        d = ImageDraw.Draw(board)
        d.rounded_rectangle([x, PAD2, x + TILE - 1, PAD2 + TILE - 1],
                            radius=12, fill=plate + (255,))
    board.alpha_composite(im, (x, PAD2))
    x += TILE + PAD2
board.convert("RGB").save(os.path.join(OUT, "transparency-proof.png"))
made.append(("transparency-proof.png", board.size, "RGB proof (checkerboard)"))

print("OUTPUT:", OUT)
for name, size, alpha in made:
    print("  %-52s %-14s alpha=%s" % (name, "%dx%d" % size, alpha))
