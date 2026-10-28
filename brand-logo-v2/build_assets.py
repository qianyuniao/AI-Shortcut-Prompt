# -*- coding: utf-8 -*-
"""AiShort brand mark asset builder.

Renders the approved motif directly from the same geometry as mark.json /
mark-simplified.json, so PNG favicons match the SVG master exactly.

Geometry (100x100 canvas):
  ring            circle r=36, stroke 12, structural
  left half solid pieslice r=20 (90deg -> 270deg), primary
  shortcut bar    round-capped bar x 58..72, thickness 11, structural
                  (dropped in the simplified variant)
"""
import os
from PIL import Image, ImageDraw

BASE = r"D:\02_MyWorkSpace\02_QYN Development Project\09Projects already tested\AI Shortcut Prompt\brand-logo-v2"
OUT = os.path.join(BASE, "assets")
os.makedirs(OUT, exist_ok=True)

PRIMARY = (62, 180, 137)   # #3EB489
STRUCT = (67, 71, 74)      # #43474A
WHITE = (255, 255, 255)
PANEL = (243, 240, 232)    # #F3F0E8

RING_R, RING_W = 36, 12
HALF_R = 20
BAR_X1, BAR_X2, BAR_T = 58, 72, 11


def render(size, simplified=False, mode="color"):
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

    # outer ring
    d.ellipse([(50 - RING_R) * s, (50 - RING_R) * s,
               (50 + RING_R) * s, (50 + RING_R) * s],
              outline=struct + (255,), width=max(1, int(round(RING_W * s))))

    # left solid half
    d.pieslice([(50 - HALF_R) * s, (50 - HALF_R) * s,
                (50 + HALF_R) * s, (50 + HALF_R) * s],
               start=90, end=270, fill=prim + (255,))

    # round-capped shortcut bar
    if not simplified:
        cap = BAR_T / 2.0
        d.rounded_rectangle(
            [((BAR_X1 - cap) * s, (50 - cap) * s),
             ((BAR_X2 + cap) * s, (50 + cap) * s)],
            radius=cap * s, fill=struct + (255,))
    return img


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p)
    return p


made = []

# --- simplified variant only below 32px ---
for px in (16, 20, 24):
    save(render(px, simplified=True), "favicon-%d.png" % px)
    made.append("favicon-%d.png (simplified)" % px)

# --- full variant from 32px up ---
for px in (32, 48, 64, 128, 256, 512, 1024):
    save(render(px), "aishort-mark-%dpx.png" % px)
    made.append("aishort-mark-%dpx.png" % px)

# --- variant colourways at 512 ---
save(render(512, mode="mono"), "aishort-mark-mono-512px.png")
save(render(512, mode="reverse"), "aishort-mark-reverse-512px.png")
save(render(512, mode="grayscale"), "aishort-mark-grayscale-512px.png")
made += ["aishort-mark-mono-512px.png", "aishort-mark-reverse-512px.png",
         "aishort-mark-grayscale-512px.png"]

# --- platform icons ---
save(render(180), "apple-touch-icon-180.png")
save(render(512), "android-chrome-512.png")
save(render(432), "android-adaptive-foreground-432.png")
made += ["apple-touch-icon-180.png", "android-chrome-512.png",
         "android-adaptive-foreground-432.png"]

# --- favicon.ico : 16(simplified) + 32 + 48 ---
ico = render(16, simplified=True)
ico.save(os.path.join(OUT, "favicon.ico"),
         sizes=[(16, 16), (32, 32), (48, 48)])
made.append("favicon.ico (16/32/48)")

# --- objective 16px legibility check: nearest-neighbour blow-up ---
def blow(px, simplified, label):
    small = render(px, simplified=simplified, mode="mono")
    bg = Image.new("RGBA", small.size, PANEL + (255,))
    bg.alpha_composite(small)
    return bg.convert("RGB").resize((px * 8, px * 8), Image.NEAREST)

tiles = [blow(16, True, "16"), blow(24, True, "24"), blow(32, False, "32")]
h = max(t.size[1] for t in tiles)
gap = 24
W = sum(t.size[0] for t in tiles) + gap * (len(tiles) + 1)
board = Image.new("RGB", (W, h + gap * 2), PANEL)
x = gap
for t in tiles:
    board.paste(t.convert("RGB"), (x, gap))
    x += t.size[0] + gap
board.save(os.path.join(OUT, "legibility-check-16-24-32.png"))
made.append("legibility-check-16-24-32.png")

# --- horizontal lockup preview: verifies the SVG lockup layout and metrics ---
from PIL import ImageFont


def font_for(size):
    for p in ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_lockup(mode="color", W=1024, H=256):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = render(720, simplified=False, mode=mode).resize((180, 180), Image.LANCZOS)
    img.alpha_composite(m, (64, 38))
    d = ImageDraw.Draw(img)
    col = WHITE + (255,) if mode == "reverse" else STRUCT + (255,)
    d.text((300, 192), "AiShort", font=font_for(176), fill=col, anchor="ls")
    return img


MODES = (("color", PANEL), ("mono", PANEL), ("reverse", STRUCT))
LW, LH, PAD = 1024, 256, 32
board2 = Image.new("RGB", (LW + PAD * 2, (LH + PAD) * 3 + PAD), (220, 218, 210))
y = PAD
for mode, bg in MODES:
    tile_bg = Image.new("RGBA", (LW, LH), bg + (255,))
    tile_bg.alpha_composite(render_lockup(mode=mode))
    board2.paste(tile_bg.convert("RGB"), (PAD, y))
    y += LH + PAD
board2.save(os.path.join(OUT, "lockup-preview.png"))
made.append("lockup-preview.png")

print("OUTPUT:", OUT)
for m in made:
    print("  ", m)
