# -*- coding: utf-8 -*-
"""
AiShort 标志 · 参数化构建脚本 v1.0
================================================================
概念：切角卡片 The Shortcut
  - 圆角方形       = 提示词卡片 / 5000+ 提示词库
  - 右上 45° 切角  = 抄近道（斜边 < 两直角边之和，捷径的几何本义）
  - 折片（镜像三角）= 被折起的那段路，同时是书签/标记，琥珀色点亮
  - 缝 GAP         = 真实负空间，保证单色与剪影层级仍然成立

比例系统：整数比 + 8pt 模块网格
  B : R    = 640 : 160 = 4 : 1
  B : CUT  = 640 : 320 = 2 : 1
  B : GAP  = 640 : 40  = 16 : 1
  CANVAS:B = 1024: 640 = 8 : 5
  CUT 直角等腰 = 1 : 1
输出：SVG 六变体 / PNG 矩阵 / favicon 三件套 / 几何与色彩数据 JSON
"""
import math, os, json, zlib, struct

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

# ───────────────────────────── 常量 ─────────────────────────────
CANVAS = 1024.0     # 画布
U      = 8.0        # 基准单位 8pt
B      = 640.0      # 卡片边长      = 80U
R      = 128.0      # 圆角半径      = 16U  (B:R   = 5:1)
CUT    = 320.0      # 切角直角边长  = 40U  (B:CUT = 2:1,  CUT:R = 5:2)
GAP    = 48.0       # 折片缝宽      = 6U   (R:GAP = 8:3,  B:GAP = 40:3)
SEAM   = GAP / 2.0  # 内缩/外扩量   = 20

COL = {
    "primary": "#0B6E62",   # 墨松绿（主色）
    "accent":  "#F2A33C",   # 琥珀（点缀色 = 被点亮的捷径）
    "ink":     "#14171A",   # 炭黑
    "paper":   "#F5F8F7",   # 冷白底（带主色倾向，非纯白）
    "white":   "#FFFFFF",
    "gray1":   "#3D4448",   # 灰阶主
    "gray2":   "#8A9296",   # 灰阶辅（与主明度差 >20%）
    "darkbg":  "#14171A",   # 深色模式底
    "primary_dark": "#3FC2A9",  # 深底上的主色提亮变体
}

FONT_STACK = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, 'PingFang SC', 'Microsoft YaHei', sans-serif"
FONT_STACK_CN = "'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', 'Source Han Sans SC', sans-serif"

# ───────────────────────── 三角内缩 / 外扩 ─────────────────────────
def _line_from_edge(A, Bp, C, d):
    """边 A->Bp，对角点 C；返回 ((nx,ny), c)：内缩 d 后直线 (P-A)·n = d，n 指向 C"""
    ex, ey = Bp[0] - A[0], Bp[1] - A[1]
    L = math.hypot(ex, ey)
    nx, ny = -ey / L, ex / L
    if (C[0] - A[0]) * nx + (C[1] - A[1]) * ny < 0:
        nx, ny = -nx, -ny
    return (nx, ny, d + A[0] * nx + A[1] * ny)

def tri_offset(tri, d, ds=None):
    """三角形沿边内缩。ds 给出逐边内缩量（ds[i] 对应边 tri[i]->tri[i+1]）；
    ds=None 时三边同为 d。d<0 为外扩。"""
    if ds is None:
        ds = [d] * 3
    ls = [_line_from_edge(tri[i], tri[(i + 1) % 3], tri[(i + 2) % 3], ds[i]) for i in range(3)]
    out = []
    for i in range(3):
        n1, m1, c1 = ls[i]
        n2, m2, c2 = ls[(i + 1) % 3]
        det = n1 * m2 - n2 * m1
        x = (c1 * m2 - c2 * m1) / det
        y = (n1 * c2 - n2 * c1) / det
        out.append((x, y))
    return out

def geom(dx=0.0, dy=0.0, b=B, r=R, cut=CUT, gap=GAP):
    """返回几何字典（dx/dy 为光学配平偏移）"""
    x0 = (CANVAS - b) / 2.0 + dx
    y0 = (CANVAS - b) / 2.0 + dy
    x1, y1 = x0 + b, y0 + b
    P1 = (x1 - cut, y0)          # 上边切点
    P2 = (x1, y0 + cut)          # 右边切点
    V  = (x1, y0)                # 右上角（被切掉）
    Vp = (x1 - cut, y0 + cut)    # V 沿切边 P1P2 的镜像 = 折片直角顶点
    flap = [P1, P2, Vp]          # 折片原三角（边序：P1→P2 斜边=折痕，P2→Vp 横边，Vp→P1 竖边）
    notch = [P1, V, P2]          # 缺口（负空间）
    # 折叠的物理：折痕（斜边）处折片与卡片相连，只有切开的两条直角边留缝。
    # 故挖除区 = 原三角本身（斜边不扩），折片只沿两直角边内缩 GAP。
    return dict(x0=x0, y0=y0, x1=x1, y1=y1, r=r, cut=cut, gap=gap,
                P1=P1, P2=P2, V=V, Vp=Vp,
                flap=flap, notch=notch,
                flap_in=tri_offset(flap, 0, ds=[0.0, gap, gap]),  # 折片实体（折痕共享）
                flap_out=flap)                                    # 主卡挖除区

# ─────────────────────────── SVG 构件 ───────────────────────────
def f(v):
    return ("%.3f" % v).rstrip("0").rstrip(".")

def card_path(g):
    x0, y0, x1, y1, r = g["x0"], g["y0"], g["x1"], g["y1"], g["r"]
    p1, p2 = g["P1"], g["P2"]
    return " ".join([
        f"M {f(x0+r)} {f(y0)}",
        f"L {f(p1[0])} {f(p1[1])}",                 # 上边
        f"L {f(p2[0])} {f(p2[1])}",                 # 45° 切角（捷径斜边）
        f"L {f(x1)} {f(y1-r)}",
        f"A {f(r)} {f(r)} 0 0 1 {f(x1-r)} {f(y1)}", # 右下圆角
        f"L {f(x0+r)} {f(y1)}",
        f"A {f(r)} {f(r)} 0 0 1 {f(x0)} {f(y1-r)}", # 左下圆角
        f"L {f(x0)} {f(y0+r)}",
        f"A {f(r)} {f(r)} 0 0 1 {f(x0+r)} {f(y0)}", # 左上圆角
        "Z"])

def tri_path(t):
    return "M " + " L ".join(f"{f(p[0])} {f(p[1])}" for p in t) + " Z"

def mark_svg(g, card_color, flap_color, size=1024, with_seam=True, comment=""):
    """纯图形 mark（1024×1024 viewBox）"""
    mid = ("aishort-mark-" + comment) if comment else "aishort-mark"
    card = card_path(g)
    if not with_seam:                       # 16px 极简版：折片并入主形
        body = f'<path fill="{card_color}" d="{card}"/>'
        if flap_color and flap_color != card_color:
            body += f'\n  <path fill="{flap_color}" d="{tri_path(g["flap_in"])}"/>'
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
                f'width="{size}" height="{size}" role="img" aria-label="AiShort">\n'
                f'  <!-- {comment or "mark"} : B={f(B)} R={f(R)} CUT={f(CUT)} GAP={f(GAP)} -->\n  '
                + body + "\n</svg>\n")
    body = (f'  <mask id="{mid}-m" maskUnits="userSpaceOnUse" x="0" y="0" width="{size}" height="{size}">\n'
            f'    <path fill="#FFFFFF" d="{card}"/>\n'
            f'    <path fill="#000000" d="{tri_path(g["flap_out"])}"/>\n'
            f'  </mask>\n'
            f'  <path fill="{card_color}" d="{card}" mask="url(#{mid}-m)"/>\n'
            f'  <path fill="{flap_color}" d="{tri_path(g["flap_in"])}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
            f'width="{size}" height="{size}" role="img" aria-label="AiShort">\n'
            f'  <!-- {comment or "mark"} : B={f(B)} R={f(R)} CUT={f(CUT)} GAP={f(GAP)} '
            f'比例系统=整数比(8pt) 光学偏移=({f(g["x0"]- (CANVAS-B)/2)},{f(g["y0"]-(CANVAS-B)/2)}) -->\n'
            + body + "\n</svg>\n")

def wordmark(x, y, size, fill, cn=False, weight=650, ls=-0.012, tl=None):
    """tl = textLength：锁定字标宽度，消除跨平台字体差异导致的版式漂移"""
    fam = FONT_STACK_CN if cn else FONT_STACK
    tl_attr = (f' textLength="{f(tl)}" lengthAdjust="spacingAndGlyphs"' if tl else
               f' letter-spacing="{f(ls * size)}"')
    return (f'<text x="{f(x)}" y="{f(y)}" font-family="{fam}" font-size="{f(size)}" '
            f'font-weight="{weight}"{tl_attr} fill="{fill}">'
            f'{"AiShort" if not cn else "AI 提示词库"}</text>')

def lockup_v(g, card_color, flap_color, text_color):
    """竖排组合标 viewBox 0 0 720 720：mark 288 高居中，字标 150（cap≈109）"""
    MV = 288.0                       # mark 目标高
    s = MV / B
    gg = scale_geom(g, s, (720.0 - MV) / 2 - g["x0"] * s, 96.0 - g["y0"] * s)
    fs = 150.0
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 720" width="720" height="720" '
           f'role="img" aria-label="AiShort">',
           f'  <!-- 竖排 lockup · mark 288 / 字标 cap ≈109 · 图字间距 96 = 0.33×mark高 · 字标宽锁定 560 -->',
           f'  <g>{mark_body(gg, card_color, flap_color, "v")}</g>',
           "  " + wordmark(80, 590, fs, text_color, tl=560.0),
           "</svg>\n"]
    return "\n".join(out)

def scale_geom(g, s, ox, oy):
    def sp(p): return (p[0] * s + ox, p[1] * s + oy)
    return dict(x0=g["x0"] * s + ox, y0=g["y0"] * s + oy, x1=g["x1"] * s + ox, y1=g["y1"] * s + oy,
                r=g["r"] * s, cut=g["cut"] * s, gap=g["gap"] * s,
                P1=sp(g["P1"]), P2=sp(g["P2"]), V=sp(g["V"]), Vp=sp(g["Vp"]),
                flap=[sp(p) for p in g["flap"]], notch=[sp(p) for p in g["notch"]],
                flap_in=[sp(p) for p in g["flap_in"]], flap_out=[sp(p) for p in g["flap_out"]])

def mark_body(g, card_color, flap_color, tag="x", with_seam=True):
    """lockup 内部用的 mark 片段（不含 svg 外壳）"""
    card = card_path(g)
    if not with_seam:
        return f'<path fill="{card_color}" d="{card}"/>'
    mid = "m-" + tag
    return (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="4096" height="4096">'
            f'<path fill="#FFFFFF" d="{card}"/><path fill="#000000" d="{tri_path(g["flap_out"])}"/></mask>'
            f'<path fill="{card_color}" d="{card}" mask="url(#{mid})"/>'
            f'<path fill="{flap_color}" d="{tri_path(g["flap_in"])}"/>')

def lockup_h2(g, card_color, flap_color, text_color, sub_color=None, sub=None):
    """横版组合标 viewBox 0 0 1024 256：mark 192 高，字标 cap 138（mark:cap = 10:7.19）"""
    MH = 180.0                       # mark 目标高（: 字标 cap 128 = 1.406 ≈ 1:0.71）
    s = MH / B
    gg = scale_geom(g, s, 64.0 - g["x0"] * s, (256.0 - MH) / 2 - g["y0"] * s)
    fs = 176.0
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 256" width="1024" height="256" '
           f'role="img" aria-label="AiShort">',
           f'  <!-- 横版 lockup · mark 180 / 字标 cap ≈128 · 图字间距 60 = 0.33×mark高 · 字标宽锁定 660 -->',
           f'  <g>{mark_body(gg, card_color, flap_color, "h")}</g>',
           "  " + wordmark(304.0, 192.0, fs, text_color, tl=660.0)]
    if sub:
        out.append("  " + wordmark(304.0, 236.0, 44.0, sub_color or text_color, weight=500, ls=0.08))
    out.append("</svg>\n")
    return "\n".join(out)

# ─────────────────────────── 光栅器（纯 Python） ───────────────────────────
def seg_dist(px, py, A, Bp):
    ex, ey = Bp[0] - A[0], Bp[1] - A[1]
    wx, wy = px - A[0], py - A[1]
    t = max(0.0, min(1.0, (wx * ex + wy * ey) / (ex * ex + ey * ey)))
    return math.hypot(wx - t * ex, wy - t * ey)

def tri_sdf(px, py, tri):
    """三角形有符号距离：内部为负，外部为到边线段的真实欧氏距离"""
    vs = []
    for i in range(3):
        A, Bp, C = tri[i], tri[(i + 1) % 3], tri[(i + 2) % 3]
        ex, ey = Bp[0] - A[0], Bp[1] - A[1]
        L = math.hypot(ex, ey)
        nx, ny = -ey / L, ex / L
        if (C[0] - A[0]) * nx + (C[1] - A[1]) * ny < 0:
            nx, ny = -nx, -ny
        vs.append((px - A[0]) * nx + (py - A[1]) * ny)
    mn = min(vs)
    if mn >= 0.0:
        return -mn                                   # 内部
    return min(seg_dist(px, py, tri[i], tri[(i + 1) % 3]) for i in range(3))

def rrect_sdf(px, py, x0, y0, x1, y1, r):
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    hw, hh = (x1 - x0) / 2.0 - r, (y1 - y0) / 2.0 - r
    dx, dy = abs(px - cx) - hw, abs(py - cy) - hh
    return math.hypot(max(dx, 0.0), max(dy, 0.0)) + min(max(dx, dy), 0.0) - r

def _cov(d):
    return 0.0 if d > 0.5 else (1.0 if d < -0.5 else 0.5 - d)

def render(size, g, card_rgba, flap_rgba, ss=2, with_seam=True):
    """返回 RGBA 行列表；ss = 每边超采样数"""
    rows = []
    x0, y0, x1, y1, r = g["x0"], g["y0"], g["x1"], g["y1"], g["r"]
    fin, fout, notch = g["flap_in"], g["flap_out"], g["notch"]
    k = CANVAS / float(size)
    inv = 1.0 / (ss * ss)
    for py in range(size):
        row = bytearray()
        for px in range(size):
            ar = ag = ab = aa = 0.0
            for sy in range(ss):
                for sx in range(ss):
                    wx = (px + (sx + 0.5) / ss) * k
                    wy = (py + (sy + 0.5) / ss) * k
                    if tri_sdf(wx, wy, notch) < 0:      # 右上缺口：抄近道被跳过的那段
                        continue
                    dc = rrect_sdf(wx, wy, x0, y0, x1, y1, r)
                    ac = _cov(dc)
                    if ac <= 0:
                        continue
                    if with_seam:
                        a_out = _cov(tri_sdf(wx, wy, fout))
                        ac *= (1.0 - a_out)
                        a_in = _cov(tri_sdf(wx, wy, fin))
                    else:
                        a_in = 0.0
                    # 先铺主卡，再叠折片
                    ar += (card_rgba[0] * ac * (1 - a_in) + flap_rgba[0] * a_in) * 255.0
                    ag += (card_rgba[1] * ac * (1 - a_in) + flap_rgba[1] * a_in) * 255.0
                    ab += (card_rgba[2] * ac * (1 - a_in) + flap_rgba[2] * a_in) * 255.0
                    aa += (ac * (1 - a_in) + a_in) * 255.0
            row += bytes((min(255, int(ar * inv + 0.5)), min(255, int(ag * inv + 0.5)),
                          min(255, int(ab * inv + 0.5)), min(255, int(aa * inv + 0.5))))
        rows.append(bytes(row))
    return rows

def mass_center(g, n=512):
    """实体质心（画布坐标），用于光学配平"""
    sx = sy = sw = 0.0
    k = CANVAS / float(n)
    x0, y0, x1, y1, r = g["x0"], g["y0"], g["x1"], g["y1"], g["r"]
    fout, fin, notch = g["flap_out"], g["flap_in"], g["notch"]
    for py in range(n):
        wy = (py + 0.5) * k
        for px in range(n):
            wx = (px + 0.5) * k
            if rrect_sdf(wx, wy, x0, y0, x1, y1, r) > 0:
                continue
            if tri_sdf(wx, wy, notch) < 0:
                continue
            if tri_sdf(wx, wy, fout) < 0:
                continue
            w = 1.0
            sx += wx * w; sy += wy * w; sw += w
    return sx / sw, sy / sw

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

def write_png(path, w, h, rows):
    raw = bytearray()
    for r in rows:
        raw.append(0)
        raw += r
    comp = zlib.compress(bytes(raw), 9)

    def chunk(t, data):
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xffffffff)

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", comp) + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return png

def write_ico(path, items):
    n = len(items)
    head = struct.pack("<HHH", 0, 1, n)
    off = 6 + 16 * n
    ent = b""
    for s, data in items:
        b = 0 if s >= 256 else s
        ent += struct.pack("<BBBBHHII", b, b, 0, 0, 1, 32, len(data), off)
        off += len(data)
    with open(path, "wb") as fh:
        fh.write(head + ent + b"".join(d for _, d in items))

# ─────────────────────────── 主流程 ───────────────────────────
log = []
def L(s):
    log.append(str(s))

g0 = geom()
cx, cy = mass_center(g0)
# 光学配平：质心全量补偿 = 48.41px（B 的 7.6%）会把外轮廓推得明显偏心，
# 超出 2–5% 的经验区间；取 40% 补偿 = 19.36px（B 的 3.0%），外轮廓与视觉重量双兼顾。
COMP = 0.40
DX, DY = (CANVAS / 2 - cx) * COMP, (CANVAS / 2 - cy) * COMP
G = geom(dx=DX, dy=DY)
L(f"质心(未偏移) = ({cx:.2f},{cy:.2f}) → 光学配平偏移 DX={DX:.3f} DY={DY:.3f}")

# 关键比例校验
def ratio(a, b):
    return a / b
checks = {
    "B:R": (B / R, 5.0), "B:CUT": (B / CUT, 2.0), "B:GAP": (B / GAP, 40.0 / 3.0),
    "CANVAS:B": (CANVAS / B, 1.6), "CUT:R": (CUT / R, 2.5), "R:GAP": (R / GAP, 8.0 / 3.0),
}
for k, (v, t) in checks.items():
    L(f"比例校验 {k} = {v:.4f} (期望 {t}) 误差 {abs(v-t)/t*100:.3f}%")

# 面积占比（折片 = 点缀色占比，须 <10%）
import statistics
def poly_area(t):
    return abs(sum(t[i][0] * t[(i + 1) % 3][1] - t[(i + 1) % 3][0] * t[i][1] for i in range(3))) / 2
area_card = (B * B - (4 - math.pi) * R * R) - poly_area(G["notch"]) - poly_area(G["flap_out"])
area_flap = poly_area(G["flap_in"])
L(f"折片面积占比 = {area_flap/area_card*100:.2f}% (点缀色纪律 <10%)")

# ── SVG 六变体 ──
C, A = COL["primary"], COL["accent"]
variants = {}
variants["aishort-logo-primary-fullcolor-rgb"] = lockup_h2(G, C, A, COL["ink"])
variants["aishort-logo-stacked-fullcolor-rgb"] = lockup_v(G, C, A, COL["ink"])
variants["aishort-mark-only-fullcolor-rgb"] = mark_svg(G, C, A, 1024, True, "mark-only")
variants["aishort-logo-primary-mono-black-rgb"] = lockup_h2(G, COL["ink"], COL["ink"], COL["ink"])
variants["aishort-logo-primary-reversed-rgb"] = lockup_h2(G, COL["white"], COL["white"], COL["white"])
variants["aishort-logo-primary-grayscale-rgb"] = lockup_h2(G, COL["gray1"], COL["gray2"], COL["ink"])
# 附加：纯图形各色版（供 favicon / 头像）
variants["aishort-mark-only-mono-black-rgb"] = mark_svg(G, COL["ink"], COL["ink"], 1024, True, "mark-mono")
variants["aishort-mark-only-reversed-rgb"] = mark_svg(G, COL["white"], COL["white"], 1024, True, "mark-reversed")
variants["aishort-mark-only-grayscale-rgb"] = mark_svg(G, COL["gray1"], COL["gray2"], 1024, True, "mark-gray")
variants["aishort-mark-only-darkmode-rgb"] = mark_svg(G, COL["primary_dark"], A, 1024, True, "mark-darkmode")
for name, s in variants.items():
    with open(os.path.join(SUB["svg"], name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(s)
L(f"SVG 变体 {len(variants)} 个 → 01-web-rgb/svg/")

# ── favicon：与主标同骨架（折痕共享 + 双边缝），实测 16px 折片仍占 5.6px，无需再简化 ──
fg = G
with open(os.path.join(SUB["fav"], "favicon.svg"), "w", encoding="utf-8") as fh:
    fh.write(mark_svg(fg, C, A, 1024, True, "favicon"))
L("favicon.svg 已输出（与主标同几何：折片 224/640 = 35% 边长，16px 下 ≈5.6px）")

# ── PNG 矩阵 ──
def png_for(path, size, card_hex, flap_hex, g, ss=2, with_seam=True):
    rows = render(size, g, hex2rgb(card_hex), hex2rgb(flap_hex), ss=ss, with_seam=with_seam)
    return write_png(path, size, size, rows)

pngs = {}
for size in (128, 256, 512, 1024, 2048):
    ss = 2 if size <= 1024 else 1
    p = os.path.join(SUB["png"], f"aishort-mark-only-fullcolor-rgb-{size}px.png")
    pngs[f"mark-{size}"] = p
    png_for(p, size, C, A, G, ss=ss)
# 变体位图（单色 / 反白 / 灰阶 512px）
for nm, cc, ff in [("mono-black", COL["ink"], COL["ink"]),
                   ("reversed", COL["white"], COL["white"]),
                   ("grayscale", COL["gray1"], COL["gray2"])]:
    png_for(os.path.join(SUB["png"], f"aishort-mark-only-{nm}-rgb-512px.png"), 512, cc, ff, G, ss=2)
# Android 自适应图标前景层 432（安全区直径 288，本图 mark 占 270 → 合规）
png_for(os.path.join(SUB["fav"], "android-adaptive-foreground-432.png"), 432, C, A, G, ss=2)
L("PNG 全彩梯队 128/256/512/1024/2048 + 变体 512 + Android 前景层 432 已输出")

# favicon 位图
fav_items = []
for s in (16, 32, 48, 64):
    p = os.path.join(SUB["fav"], f"favicon-{s}x{s}.png")
    png_for(p, s, C, A, fg, ss=4 if s <= 32 else 3, with_seam=True)
for s in (180, 512):
    p = os.path.join(SUB["fav"], f"{'apple-touch-icon' if s==180 else 'android-chrome'}-{s}.png")
    png_for(p, s, C, A, G if s != 180 else fg, ss=2)
ico_parts = []
for s in (16, 32, 48):
    p = os.path.join(SUB["fav"], f"favicon-{s}x{s}.png")
    ico_parts.append((s, open(p, "rb").read()))
write_ico(os.path.join(SUB["fav"], "favicon.ico"), ico_parts)
L("favicon 三件套：favicon.ico(16/32/48) + favicon.svg + apple-touch-icon-180 + android-chrome-512")

# ── 16px / 32px ASCII 实测（压力测试凭证）──
def ascii_art(size, g, ss=4):
    """# = 主卡实体, O = 琥珀折片, + = 半调边缘, . = 空"""
    rows = render(size, g, hex2rgb(C), hex2rgb(A), ss=ss, with_seam=True)
    out = []
    for py in range(size):
        line = ""
        for px in range(size):
            r, gg_, b, a = rows[py][px * 4:px * 4 + 4]
            if a > 170:
                line += "O" if r > 128 else "#"
            elif a > 70:
                line += "+"
            else:
                line += "."
        out.append(line)
    return out

A16 = ascii_art(16, fg, ss=6)
A32 = ascii_art(32, fg, ss=4)
L("\n--- 16px 实测（# = 实心, + = 半调, . = 空）---")
L("\n".join(A16))
L("\n--- 32px 实测 ---")
L("\n".join(A32))

# ── 模糊测试：3px 盒式模糊后大形是否仍成立 ──
def blur_ascii(size=28, k=3):
    rows = render(size, G, hex2rgb(C), hex2rgb(A), ss=3)
    a = [[rows[py][px * 4 + 3] / 255.0 for px in range(size)] for py in range(size)]
    out = []
    half = k // 2
    for py in range(size):
        line = ""
        for px in range(size):
            s = n = 0.0
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    yy, xx = py + dy, px + dx
                    if 0 <= yy < size and 0 <= xx < size:
                        s += a[yy][xx]; n += 1
            v = s / n
            line += "#" if v > 0.6 else ("+" if v > 0.3 else ("." if v > 0.08 else " "))
        out.append(line)
    return out

BLUR = blur_ascii()
L("\n--- 模糊测试（28px 渲染 + 3px 盒式模糊；# 实 + 半调 . 弱 空）---")
L("\n".join(BLUR))

# ── 数据 JSON（供文档脚本使用，数值零手写）──
def rel_lum(hexs):
    r, g, b = hex2rgb(hexs)
    def t(v): return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * t(r) + 0.7152 * t(g) + 0.0722 * t(b)

def contrast(h1, h2):
    l1, l2 = rel_lum(h1), rel_lum(h2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)

def gray_lum(hexs):
    return rel_lum(hexs)

def rgb2cmyk(hexs):
    r, g, b = [int(hexs.lstrip('#')[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    k = 1 - max(r, g, b)
    if k == 1:
        return (0, 0, 0, 100)
    return (round((1 - r - k) / (1 - k) * 100), round((1 - g - k) / (1 - k) * 100),
            round((1 - b - k) / (1 - k) * 100), round(k * 100))

data = {
    "canvas": CANVAS, "U": U, "B": B, "R": R, "CUT": CUT, "GAP": GAP, "SEAM": SEAM,
    "dx": DX, "dy": DY, "centroid": [cx, cy],
    "ratios": {k: {"value": v, "target": t, "err_pct": abs(v - t) / t * 100} for k, (v, t) in checks.items()},
    "x0": G["x0"], "y0": G["y0"], "x1": G["x1"], "y1": G["y1"],
    "P1": G["P1"], "P2": G["P2"], "V": G["V"], "Vp": G["Vp"],
    "flap_in": G["flap_in"], "flap_out": G["flap_out"],
    "area_card": area_card, "area_flap": area_flap, "flap_pct": area_flap / area_card * 100,
    "colors": COL,
    "contrast": {
        "primary_on_paper": contrast(COL["primary"], COL["paper"]),
        "primary_on_white": contrast(COL["primary"], COL["white"]),
        "accent_on_primary": contrast(COL["accent"], COL["primary"]),
        "primary_dark_on_darkbg": contrast(COL["primary_dark"], COL["darkbg"]),
        "gray1_on_white": contrast(COL["gray1"], COL["white"]),
        "gray2_on_gray1": contrast(COL["gray2"], COL["gray1"]),
    },
    "gray_lum": {k: gray_lum(v) for k, v in COL.items()},
    "cmyk": {k: rgb2cmyk(v) for k, v in COL.items()},
    "ascii16": A16, "ascii32": A32, "blur": BLUR,
    "comp": COMP, "flap_leg": CUT - 2 * GAP, "cut_hyp": CUT * math.sqrt(2),
    "font_stack": FONT_STACK,
}
with open(os.path.join(SUB["src"], "geometry.json"), "w", encoding="utf-8") as fh:
    json.dump(data, fh, ensure_ascii=False, indent=2)
L("\ngeometry.json 已输出")

with open(os.path.join(SUB["src"], "build.log.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(log))
print("OK")
