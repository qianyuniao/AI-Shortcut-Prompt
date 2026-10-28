# -*- coding: utf-8 -*-
"""AiShort / AI Shortcut Prompt — lockup builder.

Rebuilds the horizontal and stacked lockups with the full project name
"AI Shortcut Prompt", measuring the real font metrics so the SVG textLength
and the PNG output agree.

Geometry is identical to mark.json:
  ring            circle r=36, stroke 12, structural
  left half solid pieslice r=20 (90deg -> 270deg), primary
  shortcut bar    round-capped bar x 58..72, thickness 11, structural
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = r"D:\02_MyWorkSpace\02_QYN Development Project\09Projects already tested\AI Shortcut Prompt\brand-logo-v2"
SVG_DIR = os.path.join(BASE, "svg")
ASSETS = os.path.join(BASE, "assets")
os.makedirs(SVG_DIR, exist_ok=True)
os.makedirs(ASSETS, exist_ok=True)

BRAND = "AI Shortcut Prompt"

PRIMARY = (62, 180, 137)
STRUCT = (67, 71, 74)
WHITE = (255, 255, 255)
PANEL = (243, 240, 232)

RING_R, RING_W = 36, 12
HALF_R = 20
BAR_X1, BAR_X2, BAR_T = 58, 72, 11

FONT_STACK = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif"

made = []


def font_for(size):
    for p in ("C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/segoeui.ttf",
              "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def render_mark(size, mode="color"):
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
    cap = BAR_T / 2.0
    d.rounded_rectangle([((BAR_X1 - cap) * s, (50 - cap) * s),
                         ((BAR_X2 + cap) * s, (50 + cap) * s)],
                        radius=cap * s, fill=struct + (255,))
    return img


# ---------------------------------------------------------------- horizontal
HW, HH = 2048, 256
MARK = 180
MARK_Y = 38
GAP = 56
FS = 168
BASELINE = 190

_probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
TEXT_W = _probe.textlength(BRAND, font=font_for(FS))
CONTENT_W = MARK + GAP + TEXT_W
X0 = (HW - CONTENT_W) / 2
MARK_X = X0
TEXT_X = X0 + MARK + GAP


def lockup(mode="color", bg=None, scale=1):
    W, H = HW * scale, HH * scale
    img = Image.new("RGBA", (W, H), bg + (255,) if bg else (0, 0, 0, 0))
    m = render_mark(MARK * 4, mode=mode).resize((MARK * scale, MARK * scale),
                                                Image.LANCZOS)
    img.alpha_composite(m, (int(MARK_X * scale), int(MARK_Y * scale)))
    d = ImageDraw.Draw(img)
    col = WHITE + (255,) if mode == "reverse" else STRUCT + (255,)
    d.text((TEXT_X * scale, BASELINE * scale), BRAND,
           font=font_for(FS * scale), fill=col, anchor="ls")
    return img


for name, mode, bg in (
    ("aishort-logo-horizontal-2048px.png", "color", None),
    ("aishort-logo-horizontal-white-2048px.png", "color", WHITE),
    ("aishort-logo-horizontal-mono-2048px.png", "mono", None),
    ("aishort-logo-horizontal-dark-2048px.png", "reverse", STRUCT),
):
    lockup(mode=mode, bg=bg).save(os.path.join(ASSETS, name))
    made.append(name)

# ------------------------------------------------------------------ stacked
SW, SH = 1024, 1024
SMARK = 480
SMARK_X = (SW - SMARK) / 2
SMARK_Y = 180
SFS = 92
SBASE = 790


def stacked(mode="color", bg=None):
    img = Image.new("RGBA", (SW, SH), bg + (255,) if bg else (0, 0, 0, 0))
    m = render_mark(SMARK * 2, mode=mode).resize((SMARK, SMARK), Image.LANCZOS)
    img.alpha_composite(m, (int(SMARK_X), SMARK_Y))
    d = ImageDraw.Draw(img)
    col = WHITE + (255,) if mode == "reverse" else STRUCT + (255,)
    d.text((SW / 2, SBASE), BRAND, font=font_for(SFS), fill=col, anchor="ms")
    return img


for name, mode, bg in (
    ("aishort-logo-stacked-1024px.png", "color", None),
    ("aishort-logo-stacked-dark-1024px.png", "reverse", STRUCT),
):
    stacked(mode=mode, bg=bg).save(os.path.join(ASSETS, name))
    made.append(name)

# ------------------------------------------------------------------- markup
MARK_SVG = """  <g transform="translate(%(mx).2f,%(my).2f) scale(%(scale).4f)">
    <circle cx="50" cy="50" r="36" fill="none" stroke="%(s)s" stroke-width="12"/>
    <path d="M 50 30 A 20 20 0 0 0 50 70 Z" fill="%(p)s"/>
    <rect x="52.5" y="44.5" width="25" height="11" rx="5.5" fill="%(s)s"/>
  </g>"""


def write(path, body):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)
    made.append(os.path.basename(path))


horiz_tpl = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(w)d %(h)d" width="%(w)d" height="%(h)d" role="img" aria-label="AI Shortcut Prompt">
%(mark)s
  <text x="%(tx).2f" y="%(by).2f" font-family="%(stack)s" font-size="%(fs)d" font-weight="650" textLength="%(tw).2f" lengthAdjust="spacingAndGlyphs" fill="%(s)s">%(brand)s</text>
</svg>
"""

for suffix, s, p in (("fullcolor", "#43474A", "#3EB489"),
                     ("mono", "#43474A", "#43474A"),
                     ("reverse", "#FFFFFF", "#FFFFFF")):
    body = horiz_tpl % dict(w=HW, h=HH, by=BASELINE, tx=TEXT_X, tw=TEXT_W, fs=FS,
                            brand=BRAND, stack=FONT_STACK, s=s, p=p,
                            mark=MARK_SVG % dict(mx=MARK_X, my=MARK_Y,
                                                 scale=MARK / 100.0, s=s, p=p))
    write(os.path.join(SVG_DIR, "aishort-logo-horizontal-%s.svg" % suffix), body)

stack_tpl = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %(w)d %(h)d" width="%(w)d" height="%(h)d" role="img" aria-label="AI Shortcut Prompt">
%(mark)s
  <text x="%(cx)d" y="%(by)d" text-anchor="middle" font-family="%(stack)s" font-size="%(sfs)d" font-weight="650" fill="%(s)s">%(brand)s</text>
</svg>
"""
_st = font_for(150)
_stacked_tw = _probe.textlength(BRAND, font=_st)

for suffix, s, p in (("fullcolor", "#43474A", "#3EB489"),
                     ("reverse", "#FFFFFF", "#FFFFFF")):
    body = stack_tpl % dict(w=SW, h=SH, cx=SW // 2, by=SBASE, sfs=SFS, brand=BRAND,
                            stack=FONT_STACK, s=s, p=p,
                            mark=MARK_SVG % dict(mx=SMARK_X, my=SMARK_Y,
                                                 scale=SMARK / 100.0, s=s, p=p))
    write(os.path.join(SVG_DIR, "aishort-logo-stacked-%s.svg" % suffix), body)

print("TEXT_W = %.2f  CONTENT_W = %.2f  X0 = %.2f  TEXT_X = %.2f"
      % (TEXT_W, CONTENT_W, X0, TEXT_X))
print("STACKED_TEXT_W = %.2f" % _stacked_tw)
for m in made:
    print("  ", m)
