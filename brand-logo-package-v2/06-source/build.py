# -*- coding: utf-8 -*-
"""
AiShort 标志 v2.0 ·「一格之距 One of Many」参数化构建脚本
================================================================
概念（全部回溯到产品截图读出的 High 空间事实）
  - 2x2 圆角卡片阵列   = 界面 4 列等宽卡片网格（重复单元）
  - 三格浅青 + 一格实色 = 「被选中/已复制」高亮描边态 → 抽象为明度差
  - 右下格点亮          = 5000+ 条里你要的那一条；读序终点落在答案上
  - 大间隙 G            = 负空间成为主角（留白纪律）

比例系统：整数比 + 8pt 模块网格（U = 8）
  B    = 320  = 40U   格边长
  G    = 160  = 20U   间隙
  R    = 80   = 10U   圆角      B:R = 4:1 , G:R = 2:1
  M    = 112  = 14U   边距      2M + 2B + G = 1024
  阵列 = 800  = 100U            B:G = 2:1
  画布 = 1024 = 128U
  四格占地 = 4B^2 / 1024^2 = 39.1%  → 留白 60.9%（pre-flight 要求 30-40% 落地）

输出：SVG 变体 / PNG 矩阵 / favicon 全套 / 缩放测试图 / 几何 JSON / 构建日志
依赖：Python 标准库（无 Pillow、无 cairosvg，自带 SDF 抗锯齿光栅器）
"""
import math, os, json, zlib, struct, io

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUB = {
    "svg":  os.path.join(BASE, "01-web-rgb", "svg"),
    "png":  os.path.join(BASE, "01-web-rgb", "png"),
    "fav":  os.path.join(BASE, "03-social-favicon"),
    "spec": os.path.join(BASE, "05-spec"),
    "src":  os.path.join(BASE, "06-source"),
}
for p in SUB.values():
    os.makedirs(p, exist_ok=True)

LOG = []
def log(s=""):
    LOG.append(s)
    print(s)

# ─────────────────────────── 比例常量 ───────────────────────────
U      = 8.0
CANVAS = 1024.0
B      = 320.0     # 40U
G      = 160.0     # 20U
R      = 80.0      # 10U
M      = 112.0     # 14U
GRID_W = 2.0 * B + G          # 800
assert abs(2 * M + 2 * B + G - CANVAS) < 1e-9, "边距/阵列未配平"

# 四格中心坐标（左上 / 右上 / 左下 / 右下）
CELL_X = [M, M + B + G]
CELL_Y = [M, M + B + G]
LIT    = (1, 1)    # 点亮格 = 右下

# ─────────────────────────── 色彩系统 ───────────────────────────
# 墨松绿（深阶 · 结构）+ 青绿（亮阶 · 点亮），同属 hsl(168-173) 家族
COL = {
    "pine":   "#0B6E62",   # 墨松绿  深阶 · 结构色 / 字标（vs 白 6.14:1）
    "teal":   "#10997F",   # 青绿    亮阶 · 点亮格主色（vs 白 3.57:1，过 WCAG 非文本 3:1）
    "mist":   "#A9DFD5",   # 浅青    未点亮格（vs 白 1.48:1；与 teal 差 2.41:1）
    "ink":    "#14171A",   # 炭黑
    "gray":   "#8A9296",   # 灰阶辅（与 ink 明度差 > 45%）
    "white":  "#FFFFFF",
    "paper":  "#FFFFFF",
    # 深底专用
    "teal_d": "#3FC2A9",   # 深底上的点亮色（提亮，vs #14171A 为 8.14:1）
    "mist_d": "#2F3839",   # 深底上的未点亮格
    "darkbg": "#14171A",
    # 实底图标专用（pine 底 + 白挖空）
    "icon_bg":  "#0B6E62",
    "icon_dim": "#6DA8A1",  # white @ 40% over pine（三层明度皆 >= 2.27:1）
    "icon_lit": "#FFFFFF",
}

FONT = ("Inter, 'Segoe UI', 'Helvetica Neue', Arial, "
        "'PingFang SC', 'Microsoft YaHei', sans-serif")


def hex2rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ─────────────────────────── 几何 ───────────────────────────
def rr_d(x, y, w, h, r):
    """圆角矩形 SVG path（绝对坐标）"""
    return (f"M {x + r} {y} L {x + w - r} {y} A {r} {r} 0 0 1 {x + w} {y + r} "
            f"L {x + w} {y + h - r} A {r} {r} 0 0 1 {x + w - r} {y + h} "
            f"L {x + r} {y + h} A {r} {r} 0 0 1 {x} {y + h - r} "
            f"L {x} {y + r} A {r} {r} 0 0 1 {x + r} {y} Z")


def cells():
    """返回 4 个格子的 (x, y, is_lit)"""
    out = []
    for j, cy in enumerate(CELL_Y):
        for i, cx in enumerate(CELL_X):
            out.append((cx, cy, (i == LIT[0] and j == LIT[1])))
    return out


# ─────────────────────────── SVG 生成 ───────────────────────────
def svg_mark(dim_bg, dim_lit, bg_op=1.0, lit_op=1.0, title="AiShort"):
    """纯图形 SVG。dim_bg / dim_lit 为色值字符串"""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
             f'width="1024" height="1024" role="img" aria-label="{title}">',
             f'  <!-- 一格之距 One of Many · B={B:.0f} G={G:.0f} R={R:.0f} M={M:.0f} '
             f'B:R=4:1 B:G=11:3 -->']
    for (x, y, lit) in cells():
        fill = dim_lit if lit else dim_bg
        op = lit_op if lit else bg_op
        o = f' fill-opacity="{op}"' if op < 1.0 else ""
        parts.append(f'  <path fill="{fill}"{o} d="{rr_d(x, y, B, B, R)}"/>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def svg_lockup_horizontal(mark_bg, mark_lit, text_fill, name="AiShort"):
    """横版组合：viewBox 1024x256，mark 180 @ (64,38)，字标基线 192"""
    MARK = 180.0
    mx, my = 64.0, 38.0
    s = MARK / CANVAS
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 256" '
             f'width="1024" height="256" role="img" aria-label="{name}">',
             f'  <!-- 横版 lockup · mark 180 · 图字间距 64 = 0.36x mark · 字标宽锁 652 -->',
             f'  <g>']
    for (x, y, lit) in cells():
        fill = (mark_lit if lit else mark_bg)
        parts.append(f'    <path fill="{fill}" transform="translate({mx},{my}) scale({s})" '
                     f'd="{rr_d(x, y, B, B, R)}"/>')
    parts.append("  </g>")
    parts.append(f'  <text x="308" y="192" font-family="{FONT}" font-size="176" '
                 f'font-weight="650" textLength="652" lengthAdjust="spacingAndGlyphs" '
                 f'fill="{text_fill}">{name}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def svg_lockup_stacked(mark_bg, mark_lit, text_fill, name="AiShort"):
    """竖版组合：viewBox 1024x1024，mark 448 @ (288,96)，字标基线 760"""
    MARK = 448.0
    mx, my = 288.0, 96.0
    s = MARK / CANVAS
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
             f'width="1024" height="1024" role="img" aria-label="{name}">',
             f'  <!-- 竖版 lockup · mark 448 居中 @ (288,96) · 字标宽锁 620 -->',
             f'  <g>']
    for (x, y, lit) in cells():
        fill = (mark_lit if lit else mark_bg)
        parts.append(f'    <path fill="{fill}" transform="translate({mx},{my}) scale({s})" '
                     f'd="{rr_d(x, y, B, B, R)}"/>')
    parts.append("  </g>")
    parts.append(f'  <text x="202" y="760" font-family="{FONT}" font-size="200" '
                 f'font-weight="650" textLength="620" lengthAdjust="spacingAndGlyphs" '
                 f'fill="{text_fill}">{name}</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


# ─────────────────────────── 光栅器 ───────────────────────────
def render(size, shapes, bg=None):
    """SDF 抗锯齿光栅器。shapes: [(x,y,w,h,r,(r,g,b))] 坐标系 0..1024"""
    s = size / CANVAS
    buf = bytearray(size * size * 4)
    if bg:
        br, bgc, bb = bg
        for i in range(size * size):
            buf[i * 4] = br; buf[i * 4 + 1] = bgc
            buf[i * 4 + 2] = bb; buf[i * 4 + 3] = 255
    for (x, y, w, h, r, rgb) in shapes:
        x0, y0 = x * s, y * s
        ww, hh = w * s, h * s
        rr = r * s
        cx, cy = x0 + ww / 2.0, y0 + hh / 2.0
        hww, hhh = ww / 2.0, hh / 2.0
        sr, sg, sb = rgb
        ia = max(0, int(math.floor(x0 - 2))); ib = min(size, int(math.ceil(x0 + ww + 2)))
        ja = max(0, int(math.floor(y0 - 2))); jb = min(size, int(math.ceil(y0 + hh + 2)))
        for j in range(ja, jb):
            py = j + 0.5
            qy = abs(py - cy) - hhh + rr
            row = j * size * 4
            for i in range(ia, ib):
                px = i + 0.5
                qx = abs(px - cx) - hww + rr
                ax = qx if qx > 0 else 0.0
                ay = qy if qy > 0 else 0.0
                if ax and ay:
                    ln = math.sqrt(ax * ax + ay * ay)
                else:
                    ln = ax + ay
                mx = qx if qx > qy else qy
                if mx > 0:
                    mx = 0.0
                d = ln + mx - rr
                a = 0.5 - d
                if a <= 0.0:
                    continue
                if a > 1.0:
                    a = 1.0
                idx = row + i * 4
                da = buf[idx + 3]
                if da == 0:
                    buf[idx] = sr; buf[idx + 1] = sg
                    buf[idx + 2] = sb; buf[idx + 3] = int(a * 255 + 0.5)
                else:
                    daf = da / 255.0
                    na = a + daf * (1.0 - a)
                    for k, sv in enumerate((sr, sg, sb)):
                        newp = sv * a + buf[idx + k] * daf * (1.0 - a)
                        v = int(newp / na + 0.5)
                        buf[idx + k] = 255 if v > 255 else (0 if v < 0 else v)
                    buf[idx + 3] = int(na * 255 + 0.5)
    return buf


def mark_shapes(off_rgb, lit_rgb):
    out = []
    for (x, y, lit) in cells():
        out.append((x, y, B, B, R, lit_rgb if lit else off_rgb))
    return out


def write_png(path, size, buf):
    raw = bytearray()
    stride = size * 4
    for j in range(size):
        raw.append(0)
        raw += buf[j * stride:(j + 1) * stride]
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def write_ico(path, entries):
    """entries: [(size, png_bytes)]，PNG 内嵌式 ICO"""
    n = len(entries)
    hdr = struct.pack("<HHH", 0, 1, n)
    off = 6 + 16 * n
    dirs = b""
    data = b""
    for (sz, png) in entries:
        dirs += struct.pack("<BBBBHHII",
                            sz if sz < 256 else 0, sz if sz < 256 else 0,
                            0, 0, 1, 32, len(png), off)
        off += len(png)
        data += png
    with open(path, "wb") as f:
        f.write(hdr + dirs + data)
    return 6 + 16 * n + len(data)


def nearest_up(src, ssrc, dst, ddst, scale, ox, oy, channels=4):
    """把 ssrc×ssrc 的 buf 最近邻放大 scale 倍贴到 dst 的 (ox,oy)"""
    for j in range(ssrc * scale):
        sj = j // scale
        for i in range(ssrc * scale):
            si = i // scale
            si4 = (sj * ssrc + si) * channels
            di = ((oy + j) * ddst + (ox + i)) * channels
            for c in range(channels):
                dst[di + c] = src[si4 + c]


# ═══════════════════════════ 主流程 ═══════════════════════════
log("AiShort 标志 v2.0「一格之距 One of Many」构建")
log("=" * 62)

# ── 比例校验 ──
checks = [
    ("B:R", B / R, 4.0),
    ("B:G", B / G, 2.0),
    ("G:R", G / R, 2.0),
    ("阵列:画布", GRID_W / CANVAS, 100.0 / 128.0),
    ("M:B", M / B, 14.0 / 40.0),
    ("CANVAS:U", CANVAS / U, 128.0),
]
log("\n[比例校验]")
for name, got, want in checks:
    err = abs(got - want) / want * 100 if want else 0
    log(f"  {name:<12} = {got:.4f} (期望 {want:.4f}) 误差 {err:.4f}%")

# ── 质心与光学配平 ──
lit_cells = [(x + B / 2, y + B / 2) for (x, y, lit) in cells() if lit]
tot_area = 4 * B * B
sx = sum(cx * B * B for (cx, _) in [(x + B / 2, y + B / 2) for (x, y, l) in cells()])
sy = sum(cy * B * B for (_, cy) in [(x + B / 2, y + B / 2) for (x, y, l) in cells()])
cx0, cy0 = sx / tot_area, sy / tot_area
log(f"\n[光学] 几何质心 = ({cx0:.1f}, {cy0:.1f})，画布中心 = 512.0 → 形态对称，无需配平偏移")
area_pct = tot_area / (CANVAS * CANVAS) * 100
white_pct = 100 - area_pct
log(f"[留白] 四格占地 {area_pct:.1f}% → 负空间 {white_pct:.1f}%")

# ── 1. SVG 变体 ──
VARIANTS = {
    "aishort-mark-only-fullcolor-rgb":   (COL["mist"], COL["teal"]),
    "aishort-mark-only-mono-black-rgb":  (COL["gray"], COL["ink"]),
    "aishort-mark-only-grayscale-rgb":   (COL["gray"], COL["ink"]),
    "aishort-mark-only-darkmode-rgb":    (COL["mist_d"], COL["teal_d"]),
    "aishort-mark-only-highcontrast-rgb": (COL["mist"], COL["pine"]),
}
count_svg = 0
for name, (bg, lit) in VARIANTS.items():
    with open(os.path.join(SUB["svg"], name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg_mark(bg, lit))
    count_svg += 1

# 反白版：前三格 white@30%，点亮格 white@100%
count_svg += 1
rev = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" '
       'height="1024" role="img" aria-label="AiShort">',
       '  <!-- 反白版 · 未点亮格 white@30% · 点亮格 white@100% -->']
for (x, y, lit) in cells():
    op = "1" if lit else "0.30"
    rev.append(f'  <path fill="#FFFFFF" fill-opacity="{op}" d="{rr_d(x, y, B, B, R)}"/>')
rev.append("</svg>")
with open(os.path.join(SUB["svg"], "aishort-mark-only-reversed-rgb.svg"), "w",
          encoding="utf-8") as f:
    f.write("\n".join(rev) + "\n")

# 横版 / 竖版 lockup
LOCKS = {
    "aishort-logo-primary-fullcolor-rgb": (COL["mist"], COL["teal"], COL["pine"]),
    "aishort-logo-primary-mono-black-rgb": (COL["gray"], COL["ink"], COL["ink"]),
    "aishort-logo-primary-reversed-rgb":  (COL["white"], COL["white"], COL["white"]),
    "aishort-logo-primary-darkmode-rgb":  (COL["mist_d"], COL["teal_d"], "#E8EDEF"),
}
for name, (bg, lit, txt) in LOCKS.items():
    with open(os.path.join(SUB["svg"], name + ".svg"), "w", encoding="utf-8") as f:
        f.write(svg_lockup_horizontal(bg, lit, txt))
    count_svg += 1

with open(os.path.join(SUB["svg"], "aishort-logo-stacked-fullcolor-rgb.svg"), "w",
          encoding="utf-8") as f:
    f.write(svg_lockup_stacked(COL["mist"], COL["teal"], COL["pine"]))
with open(os.path.join(SUB["svg"], "aishort-logo-stacked-mono-black-rgb.svg"), "w",
          encoding="utf-8") as f:
    f.write(svg_lockup_stacked(COL["gray"], COL["ink"], COL["ink"]))
count_svg += 2
log(f"\nSVG 变体 {count_svg} 个 → 01-web-rgb/svg/")

# ── 2. PNG 矩阵 ──
SH_FULL = mark_shapes(hex2rgb(COL["mist"]), hex2rgb(COL["teal"]))
SH_MONO = mark_shapes(hex2rgb(COL["gray"]), hex2rgb(COL["ink"]))
SH_HC   = mark_shapes(hex2rgb(COL["mist"]), hex2rgb(COL["pine"]))

png_sizes = [128, 256, 512, 1024, 2048]
for s in png_sizes:
    buf = render(s, SH_FULL)
    write_png(os.path.join(SUB["png"], f"aishort-mark-only-fullcolor-rgb-{s}px.png"), s, buf)
log(f"PNG 全彩梯队 {'/'.join(str(x) for x in png_sizes)} 已输出")

for tag, sh, bg in [("mono-black", SH_MONO, None),
                    ("grayscale", SH_MONO, None),
                    ("highcontrast", SH_HC, None),
                    ("reversed", mark_shapes((255, 255, 255), (255, 255, 255)), None)]:
    buf = render(512, sh, bg)
    write_png(os.path.join(SUB["png"], f"aishort-mark-only-{tag}-rgb-512px.png"), 512, buf)

# ── 3. 实底图标（favicon / App icon）全套 ──
# 透明底版本在 16px 下三格浅青会与白底糊在一起，故图标一律改用实底 tile：
# pine 底板 + 三格 white@26% + 一格纯白，16px 下三层明度依然分离。
FAV = SUB["fav"]
ICON_R = 224.0     # 28U 底板圆角 ≈ 边长 21.9%
ICON_K = 0.84      # 阵列 800 → 672，两侧内边距 176 (22U)


def cells_idx():
    for j in (0, 1):
        for i in (0, 1):
            yield i, j, (i == LIT[0] and j == LIT[1])


def icon_geom():
    BB, GG, RR = B * ICON_K, G * ICON_K, R * ICON_K
    MM = (CANVAS - (2 * BB + GG)) / 2.0
    return BB, GG, RR, MM


def svg_icon():
    BB, GG, RR, MM = icon_geom()
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
         f'width="1024" height="1024" role="img" aria-label="AiShort">',
         f'  <!-- 实底图标版 · pine 底板 R={ICON_R:.0f} · 阵列内缩 {ICON_K} -->',
         f'  <path fill="{COL["icon_bg"]}" d="{rr_d(0, 0, CANVAS, CANVAS, ICON_R)}"/>']
    for i, j, lit in cells_idx():
        p.append(f'  <path fill="{COL["icon_lit"] if lit else COL["icon_dim"]}" '
                 f'd="{rr_d(MM + i * (BB + GG), MM + j * (BB + GG), BB, BB, RR)}"/>')
    p.append("</svg>")
    return "\n".join(p) + "\n"


def icon_shapes():
    BB, GG, RR, MM = icon_geom()
    out = [(0.0, 0.0, CANVAS, CANVAS, ICON_R, hex2rgb(COL["icon_bg"]))]
    for i, j, lit in cells_idx():
        out.append((MM + i * (BB + GG), MM + j * (BB + GG), BB, BB, RR,
                    hex2rgb(COL["icon_lit"] if lit else COL["icon_dim"])))
    return out


def scale_shapes(shapes, s):
    off = CANVAS * (1 - s) / 2.0
    return [(off + x * s, off + y * s, w * s, h * s, r * s, c)
            for (x, y, w, h, r, c) in shapes]


with open(os.path.join(FAV, "favicon.svg"), "w", encoding="utf-8") as f:
    f.write(svg_icon())
SH_ICON = icon_shapes()
for s in (16, 32, 48, 64):
    write_png(os.path.join(FAV, f"favicon-{s}x{s}.png"), s, render(s, SH_ICON))
ico_entries = []
for s in (16, 32, 48):
    tmp = os.path.join(FAV, f"_tmp-{s}.png")
    write_png(tmp, s, render(s, SH_ICON))
    with open(tmp, "rb") as fh:
        ico_entries.append((s, fh.read()))
    os.remove(tmp)
write_ico(os.path.join(FAV, "favicon.ico"), ico_entries)

write_png(os.path.join(FAV, "apple-touch-icon-180.png"), 180, render(180, SH_ICON))
write_png(os.path.join(FAV, "android-chrome-512.png"), 512, render(512, SH_ICON))
write_png(os.path.join(FAV, "android-adaptive-foreground-432.png"), 432,
          render(432, scale_shapes(SH_ICON, 0.72)))
log("实底图标：favicon.ico(16/32/48) + favicon.svg + 16/32/48/64 + "
    "apple-touch-180 + android-chrome-512 + 自适应前景层 432 已输出")

# ── 4. 缩放测试图 scale-test.png ──
SIZES = [16, 24, 32, 48, 64]
SC = 4
GAP = 10
strip_w = sum(SIZES) + GAP * (len(SIZES) + 1)
strip_h = max(SIZES) + GAP * 2
# 真尺寸行 + 4x 最近邻放大行
sw = strip_w * SC
sh_h = (strip_h + GAP + strip_h) * SC
canvas = bytearray(sw * sh_h * 4)
for i in range(sw * sh_h):
    canvas[i * 4] = 255; canvas[i * 4 + 1] = 255
    canvas[i * 4 + 2] = 255; canvas[i * 4 + 3] = 255

def blit(dst, dw, src, ss, ox, oy, scale=1):
    for j in range(ss * scale):
        for i in range(ss * scale):
            si4 = (((j // scale) * ss) + (i // scale)) * 4
            di = ((oy + j) * dw + (ox + i)) * 4
            for c in range(4):
                a = src[si4 + 3] / 255.0
                dst[di + c] = int(src[si4 + c] * a + dst[di + c] * (1 - a) + 0.5)

# 第一行：真尺寸（在 strip 内的位置 ×SC 放大到画布）
x = GAP * SC
for s in SIZES:
    b = render(s, SH_MONO)
    blit(canvas, sw, b, s, x, GAP * SC, SC)
    x += (s + GAP) * SC
# 第二行：更大尺寸
x = GAP * SC
y = (strip_h + GAP * 2) * SC
for s in SIZES:
    b = render(s * 2, SH_MONO)
    blit(canvas, sw, b, s * 2, x, y, SC // 2 if SC // 2 else 1)
    x += (s + GAP) * SC
write_png(os.path.join(SUB["spec"], "scale-test.png"), sw, canvas)

# ── 5. 16px ASCII 实测 ──
log("\n--- 16px 单色实测（# = ink 点亮格, O = gray 未点亮格, . = 空）---")
b16 = render(16, SH_MONO)
for j in range(16):
    row = ""
    for i in range(16):
        idx = (j * 16 + i) * 4
        a = b16[idx + 3] / 255.0
        if a < 0.12:
            row += "."
        else:
            # 与白底合成后再判明度，避免半透明边缘被误读为实心
            lum = a * (b16[idx] * 0.299 + b16[idx + 1] * 0.587
                       + b16[idx + 2] * 0.114) + (1 - a) * 255
            row += ("#" if lum < 110 else ("O" if lum < 205
                                           else ("+" if lum < 248 else ".")))
    log("  " + row)

# ── 6. geometry.json ──
geo = {
    "concept": "一格之距 One of Many",
    "version": "2.0",
    "grid_unit": U,
    "canvas": CANVAS,
    "cell": {"B": B, "G": G, "R": R, "M": M},
    "grid_width": GRID_W,
    "ratios": {"B:R": B / R, "B:G": B / G, "G:R": G / R,
               "grid:canvas": GRID_W / CANVAS, "M:B": M / B},
    "lit_cell": "bottom-right",
    "area_coverage_pct": round(area_pct, 2),
    "negative_space_pct": round(white_pct, 2),
    "colors": COL,
    "cells": [{"x": x, "y": y, "lit": lit} for (x, y, lit) in cells()],
}
with open(os.path.join(SUB["src"], "geometry.json"), "w", encoding="utf-8") as f:
    json.dump(geo, f, ensure_ascii=False, indent=2)

# ── 7. safe-zone.svg ──
X  = G          # 净空单位 = 一个格间隙 G = 160
BOX = GRID_W + 2 * X          # 1120
SZW = BOX + 96                # 1216
OFF = 48 + X - M              # 96 —— 把 1024 坐标系平移到安全区画布
sz = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SZW:.0f} {SZW:.0f}" '
      f'width="{SZW:.0f}" height="{SZW:.0f}" role="img" aria-label="AiShort clear space">',
      f'  <!-- 净空区 X = G = {X:.0f} · 标志四周必须留出一个 X 的绝对净空 -->',
      f'  <rect x="48" y="48" width="{BOX:.0f}" height="{BOX:.0f}" fill="none" '
      f'stroke="#C9D2D6" stroke-width="4" stroke-dasharray="16 12"/>',
      f'  <g transform="translate({OFF:.0f},{OFF:.0f})">']
for (x, y, lit) in cells():
    sz.append(f'    <path fill="{COL["teal"] if lit else COL["mist"]}" '
              f'd="{rr_d(x, y, B, B, R)}"/>')
sz.append('  </g>')
# X 尺寸标记（顶部横向）
sz.append(f'  <rect x="{48 + (BOX - 56) / 2:.0f}" y="4" width="56" height="44" '
          f'fill="#C9D2D6"/>')
sz.append(f'  <text x="{48 + BOX / 2:.0f}" y="{44:.0f}" font-family="{FONT}" '
          f'font-size="34" fill="#5A666C" text-anchor="middle">X</text>')
sz.append("</svg>")
with open(os.path.join(SUB["spec"], "safe-zone.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(sz) + "\n")

# ── 8. blueprint.svg ──
bp = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" '
      'height="1024" role="img" aria-label="AiShort geometry blueprint">',
      '  <rect width="1024" height="1024" fill="#FFFFFF"/>',
      '  <g stroke="#B9C4C9" stroke-width="2" stroke-dasharray="6 6">']
for (x, y, lit) in cells():
    bp.append(f'    <line x1="{x}" y1="0" x2="{x}" y2="1024"/>')
    bp.append(f'    <line x1="{x + B}" y1="0" x2="{x + B}" y2="1024"/>')
    bp.append(f'    <line x1="0" y1="{y}" x2="1024" y2="{y}"/>')
    bp.append(f'    <line x1="0" y1="{y + B}" x2="1024" y2="{y + B}"/>')
bp.append('  </g>')
for (x, y, lit) in cells():
    bp.append(f'  <path fill="{"#17A88C" if lit else "#DCEBE7"}" '
              f'd="{rr_d(x, y, B, B, R)}"/>')
# 尺寸标注
bp.append(f'  <g stroke="#0B6E62" stroke-width="3" fill="none">')
bp.append(f'    <line x1="{M}" y1="{M - 40}" x2="{M + B}" y2="{M - 40}"/>')
bp.append(f'    <line x1="{M}" y1="{M - 52}" x2="{M}" y2="{M - 28}"/>')
bp.append(f'    <line x1="{M + B}" y1="{M - 52}" x2="{M + B}" y2="{M - 28}"/>')
bp.append(f'    <line x1="{M + B}" y1="{M + B / 2}" x2="{M + B + G}" y2="{M + B / 2}"/>')
bp.append(f'    <line x1="{M + B}" y1="{M + B / 2 - 12}" x2="{M + B}" y2="{M + B / 2 + 12}"/>')
bp.append(f'    <line x1="{M + B + G}" y1="{M + B / 2 - 12}" x2="{M + B + G}" '
          f'y2="{M + B / 2 + 12}"/>')
bp.append('  </g>')
bp.append(f'  <text x="{M + B / 2}" y="{M - 56}" font-family="{FONT}" font-size="30" '
          f'fill="#0B6E62" text-anchor="middle">B {B:.0f}</text>')
bp.append(f'  <text x="{M + B + G / 2}" y="{M + B / 2 - 20}" font-family="{FONT}" '
          f'font-size="30" fill="#0B6E62" text-anchor="middle">G {G:.0f}</text>')
bp.append(f'  <text x="{M + B / 2}" y="{M + B + 56}" font-family="{FONT}" font-size="30" '
          f'fill="#0B6E62" text-anchor="middle">R {R:.0f}</text>')
bp.append('</svg>')
with open(os.path.join(SUB["spec"], "blueprint.svg"), "w", encoding="utf-8") as f:
    f.write("\n".join(bp) + "\n")

log("\n构建完成。")
with open(os.path.join(SUB["src"], "build.log.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
