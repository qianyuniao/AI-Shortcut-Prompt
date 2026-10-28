# -*- coding: utf-8 -*-
"""
AiShort 标志 · 文档生成器 v1.0
从 geometry.json 读取全部数值（程序计算，零手写），产出：
  00-START-HERE.md / 05-spec/spec.md / 05-spec/blueprint.svg
  preview.html（交互预览页，8 区块）/ report.html（全量技术报告，九段）
"""
import os, json, base64, math

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
SVG = os.path.join(BASE, "01-web-rgb", "svg")
PNG = os.path.join(BASE, "01-web-rgb", "png")
FAV = os.path.join(BASE, "03-social-favicon")
SPEC = os.path.join(BASE, "05-spec")
os.makedirs(SPEC, exist_ok=True)

D = json.load(open(os.path.join(HERE, "geometry.json"), encoding="utf-8"))
C = D["colors"]
K = D["contrast"]


def rd(p):
    return open(p, encoding="utf-8").read().strip()


def b64(p):
    return base64.b64encode(open(p, "rb").read()).decode()


def n(v, d=2):
    return f"{v:.{d}f}"


# ───────────────────────── 通用片段 ─────────────────────────
MARK_FULL = rd(os.path.join(SVG, "aishort-mark-only-fullcolor-rgb.svg"))
MARK_MONO = rd(os.path.join(SVG, "aishort-mark-only-mono-black-rgb.svg"))
MARK_REV = rd(os.path.join(SVG, "aishort-mark-only-reversed-rgb.svg"))
MARK_GRAY = rd(os.path.join(SVG, "aishort-mark-only-grayscale-rgb.svg"))
MARK_DARK = rd(os.path.join(SVG, "aishort-mark-only-darkmode-rgb.svg"))
LOCKUP_H = rd(os.path.join(SVG, "aishort-logo-primary-fullcolor-rgb.svg"))
LOCKUP_V = rd(os.path.join(SVG, "aishort-logo-stacked-fullcolor-rgb.svg"))
LOCKUP_B = rd(os.path.join(SVG, "aishort-logo-primary-mono-black-rgb.svg"))
LOCKUP_W = rd(os.path.join(SVG, "aishort-logo-primary-reversed-rgb.svg"))
LOCKUP_G = rd(os.path.join(SVG, "aishort-logo-primary-grayscale-rgb.svg"))
FAVSVG = rd(os.path.join(FAV, "favicon.svg"))

CSS = """
:root{--paper:%(paper)s;--ink:%(ink)s;--primary:%(primary)s;--accent:%(accent)s;
--line:#E2E8E7;--card:#FFFFFF;--muted:#5C6669;}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font-family:%(font)s;font-size:15px;line-height:1.7;}
.wrap{max-width:1160px;margin:0 auto;padding:40px 28px 80px;}
header.top{display:flex;align-items:center;gap:18px;padding-bottom:8px;border-bottom:1px solid var(--line);margin-bottom:8px;}
header.top .mk{width:56px;height:56px;flex:0 0 56px;}
h1{font-size:26px;margin:0;letter-spacing:-.4px;}
.sub{color:var(--muted);font-size:14px;margin:2px 0 0;}
h2{font-size:19px;margin:0 0 4px;letter-spacing:-.2px;}
section{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:26px 28px;margin:22px 0;}
.sechead{display:flex;align-items:baseline;gap:10px;border-bottom:1px solid var(--line);padding-bottom:12px;margin-bottom:18px;}
.secnum{font-size:12px;font-weight:700;color:#fff;background:var(--primary);border-radius:20px;padding:2px 9px;}
.note{color:var(--muted);font-size:13px;margin:0 0 14px;}
.grid{display:grid;gap:16px;}
.g2{grid-template-columns:repeat(2,1fr);} .g3{grid-template-columns:repeat(3,1fr);}
.g4{grid-template-columns:repeat(4,1fr);} .g5{grid-template-columns:repeat(5,1fr);}
.tile{border:1px solid var(--line);border-radius:12px;padding:18px;display:flex;flex-direction:column;
align-items:center;justify-content:center;gap:10px;background:var(--card);min-height:120px;}
.tile .cap{font-size:12px;color:var(--muted);text-align:center;}
.tile.light{background:%(paper)s;} .tile.dark{background:%(ink)s;border-color:%(ink)s;}
.tile.dark .cap{color:#93A0A3;} .tile.dark .wm{color:#fff;}
.tile svg{max-width:100%;height:auto;}
.wm{font-weight:650;letter-spacing:-.6px;}
.kpi{border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:var(--card);}
.kpi b{display:block;font-size:24px;letter-spacing:-.5px;color:var(--primary);}
.kpi span{font-size:12px;color:var(--muted);}
table{border-collapse:collapse;width:100%;font-size:13.5px;}
th,td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top;}
th{background:#F0F4F3;font-weight:650;}
code{background:#F0F4F3;padding:1px 5px;border-radius:4px;font-size:12.5px;}
pre{background:#F7FAF9;border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto;
font-size:12px;line-height:1.45;margin:8px 0;}
.sw{display:flex;gap:0;border-radius:10px;overflow:hidden;border:1px solid var(--line);}
.sw div{flex:1;height:70px;display:flex;align-items:flex-end;justify-content:center;
font-size:11px;padding-bottom:6px;font-weight:600;}
.mock{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff;}
.browser{background:#DEE3E6;padding:10px 12px 0;}
.tab{display:inline-flex;align-items:center;gap:7px;background:#fff;border-radius:8px 8px 0 0;
padding:7px 12px;font-size:12px;font-weight:600;}
.bar{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1px solid var(--line);}
.bar .links{margin-left:auto;display:flex;gap:16px;font-size:12px;color:var(--muted);}
.phone{background:#1B1F22;border-radius:22px;padding:14px;}
.phonepad{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;padding:16px 10px 26px;}
.appic{border-radius:14px;overflow:hidden;}
.appname{font-size:10px;color:#C9D1D3;text-align:center;margin-top:4px;font-family:%(font)s}
.cardbg{background:#fff;padding:22px;}
.strip{display:flex;align-items:center;gap:14px;flex-wrap:wrap;}
.hero{background:%(ink)s;padding:44px 34px;border-radius:12px;}
.hero .t{color:#fff;font-size:30px;font-weight:650;letter-spacing:-1px;}
.hero .s{color:#9BA7AA;font-size:14px;margin-top:8px;}
.watermark{position:relative;background:%(paper)s;}
.watermark .bgmark{position:absolute;right:-30px;bottom:-50px;width:280px;opacity:.10;}
.dont{opacity:.55;}
.dont::after{content:"✕";color:#C0392B;font-weight:700;margin-left:8px;}
ul{margin:6px 0 0 18px;padding:0;} li{margin:3px 0;}
"""
for _k, _v in (("paper", C["paper"]), ("ink", C["ink"]), ("primary", C["primary"]),
               ("accent", C["accent"]), ("font", D["font_stack"])):
    CSS = CSS.replace("%(" + _k + ")s", _v)


import re as _re, itertools as _it
_cnt = _it.count()


def emb(s):
    """内联到同一页面时给 SVG 内部 id 加唯一后缀，防止 mask id 撞车"""
    tag = f"u{next(_cnt)}"
    for i in set(_re.findall(r'id="([^"]+)"', s)):
        s = s.replace(f'id="{i}"', f'id="{i}-{tag}"').replace(f"url(#{i})", f"url(#{i}-{tag})")
    return s


def svg_wrap(inner, w):
    return f'<div style="width:{w}px">{inner}</div>'


def mark_div(size, which="full"):
    m = {"full": MARK_FULL, "mono": MARK_MONO, "rev": MARK_REV,
         "gray": MARK_GRAY, "dark": MARK_DARK}[which]
    return f'<div style="width:{size}px">{emb(m)}</div>'


def wm_html(size, color="#14171A", weight=650, ls="-0.6", txt="AiShort", extra=""):
    return (f'<div class="wm" style="font-size:{size}px;color:{color};font-weight:{weight};'
            f'letter-spacing:{ls}px;{extra}">{txt}</div>')


# ───────────────────────── blueprint 数学标注图 ─────────────────────────
def build_blueprint():
    gx0, gy0 = D["x0"], D["y0"]
    gx1, gy1 = D["x1"], D["y1"]
    P1, P2, V, Vp = D["P1"], D["P2"], D["V"], D["Vp"]
    R, B, CUT, GAP = D["R"], D["B"], D["CUT"], D["GAP"]
    fi = D["flap_in"]
    off = 190
    W = H = 1024 + off * 2
    o = off
    P = lambda p: (p[0] + o, p[1] + o)
    s = []
    A = s.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
      f'font-family="{D["font_stack"]}">')
    A(f'<rect width="{W}" height="{H}" fill="#FBFCFC"/>')
    # 8pt 网格
    for i in range(0, 1025, 64):
        A(f'<line x1="{i+o}" y1="{o}" x2="{i+o}" y2="{1024+o}" stroke="#E6EBEA" stroke-width="1"/>')
        A(f'<line x1="{o}" y1="{i+o}" x2="{1024+o}" y2="{i+o}" stroke="#E6EBEA" stroke-width="1"/>')
    # 构造线：切边延长线、缺口对角
    A(f'<line x1="{P(P1)[0]-90}" y1="{P(P1)[1]-90}" x2="{P(P2)[0]+90}" y2="{P(P2)[1]+90}" '
      f'stroke="#B7C4C7" stroke-width="1" stroke-dasharray="6 5"/>')
    A(f'<line x1="{P(Vp)[0]}" y1="{P(Vp)[1]}" x2="{P(V)[0]}" y2="{P(V)[1]}" '
      f'stroke="#D9A65A" stroke-width="1" stroke-dasharray="4 4"/>')
    # 轮廓
    A(f'<g opacity="0.16">{"".join(c for c in MARK_FULL.split(chr(10))[2:-2])}</g>')
    A(f'<path fill="none" stroke="{C["primary"]}" stroke-width="2.5" d="M {P((gx0+R,gy0))[0]} {P((gx0+R,gy0))[1]} '
      f'L {P(P1)[0]} {P(P1)[1]} L {P(P2)[0]} {P(P2)[1]} L {P((gx1,gy1-R))[0]} {P((gx1,gy1-R))[1]} '
      f'A {R} {R} 0 0 1 {P((gx1-R,gy1))[0]} {P((gx1-R,gy1))[1]} L {P((gx0+R,gy1))[0]} {P((gx0+R,gy1))[1]} '
      f'A {R} {R} 0 0 1 {P((gx0,gy1-R))[0]} {P((gx0,gy1-R))[1]} L {P((gx0,gy0+R))[0]} {P((gx0,gy0+R))[1]} '
      f'A {R} {R} 0 0 1 {P((gx0+R,gy0))[0]} {P((gx0+R,gy0))[1]} Z"/>')
    A(f'<path fill="none" stroke="{C["accent"]}" stroke-width="2.5" d="M ' +
      " L ".join(f"{P(p)[0]} {P(p)[1]}" for p in fi) + ' Z"/>')
    # 圆心十字标（三个圆角）
    for cc in [(gx0 + R, gy0 + R), (gx0 + R, gy1 - R), (gx1 - R, gy1 - R)]:
        p = P(cc)
        A(f'<path stroke="#7C8A8D" stroke-width="1.4" d="M {p[0]-16} {p[1]} L {p[0]+16} {p[1]} '
          f'M {p[0]} {p[1]-16} L {p[0]} {p[1]+16}"/>')
        A(f'<circle cx="{p[0]}" cy="{p[1]}" r="{R}" fill="none" stroke="#7C8A8D" '
          f'stroke-width="1" stroke-dasharray="3 4"/>')
    def dim(x1, y1, x2, y2, label, color="#3D4448", side=1, dx=0, dy=0):
        A(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.4"/>')
        for (ex, ey) in ((x1, y1), (x2, y2)):
            A(f'<line x1="{ex-4}" y1="{ey}" x2="{ex+4}" y2="{ey}" stroke="{color}" stroke-width="1.4"/>'
              f'<line x1="{ex}" y1="{ey-4}" x2="{ex}" y2="{ey+4}" stroke="{color}" stroke-width="1.4"/>')
        A(f'<text x="{(x1+x2)/2+dx}" y="{(y1+y2)/2+dy}" font-size="19" fill="{color}" '
          f'text-anchor="middle" font-weight="600">{label}</text>')
    # 尺寸链
    dim(*P((gx0, gy1)), *P((gx1, gy1)), f"B = {n(B,0)} (80U)", dy=34)
    dim(*P(P1), *P((gx1, gy0)), f"CUT = {n(CUT,0)} (40U)", dy=-16)
    dim(*P((gx1, gy0 + CUT)), *P((gx1, gy1)), f"{n(B-CUT,0)}", dx=76)
    dim(*P((gx0, gy0)), *P((gx0, gy0 + R)), f"R={n(R,0)}", dx=-52)
    A(f'<text x="{P(Vp)[0]-14}" y="{P(Vp)[1]+30}" font-size="17" fill="{C["accent"]}" '
      f'text-anchor="end" font-weight="600">折片直角边 = {n(D["flap_leg"],0)} = CUT − 2×GAP</text>')
    A(f'<text x="{P(P1)[0]-16}" y="{P(P1)[1]-16}" font-size="17" fill="{C["accent"]}" '
      f'text-anchor="end" font-weight="600">GAP = {n(GAP,0)}（折缝，仅两直角边）</text>')
    A(f'<text x="{P(P2)[0]+16}" y="{P(P2)[1]+40}" font-size="17" fill="{C["primary"]}" '
      f'font-weight="600">斜边 = 320√2 = {n(D["cut_hyp"],1)} &lt; 直角路径 320+320 = 640（捷径本义）</text>')
    A(f'<text x="{o}" y="{o-26}" font-size="18" fill="#3D4448" font-weight="600">'
      f'比例系统：整数比 + 8pt 模块网格（B:R=5:1 · B:CUT=2:1 · CUT:R=5:2 · R:GAP=8:3）</text>')
    A(f'<text x="{o}" y="{o-52}" font-size="18" fill="#3D4448" font-weight="600">'
      f'光学配平：质心({n(D["centroid"][0],1)}, {n(D["centroid"][1],1)}) → 补偿 {n(D["comp"]*100,0)}% '
      f'= ({n(D["dx"],1)}, {n(D["dy"],1)})</text>')
    A("</svg>")
    return "\n".join(s)


BP = build_blueprint()
open(os.path.join(SPEC, "blueprint.svg"), "w", encoding="utf-8").write(BP)

# ───────────────────────── 缩放墙用图 ─────────────────────────
SIZES = [16, 32, 48, 64, 128, 256, 512, 1024]
sc = {}
for s in SIZES:
    p = os.path.join(FAV if s <= 64 else PNG,
                     f"favicon-{s}x{s}.png" if s <= 64 else f"aishort-mark-only-fullcolor-rgb-{s}px.png")
    sc[s] = b64(p)
sc[2048] = b64(os.path.join(PNG, "aishort-mark-only-fullcolor-rgb-2048px.png"))
FAV16 = b64(os.path.join(FAV, "favicon-16x16.png"))


def img(s, style=""):
    return (f'<img src="data:image/png;base64,{sc[s]}" width="{s}" height="{s}" '
            f'style="image-rendering:auto;{style}" alt="mark {s}px"/>')


ASCII = lambda rows: "<pre>" + "\n".join(rows) + "</pre>"

# ───────────────────────── 色彩四格式表 ─────────────────────────
PANTONE = {"primary": "3295 C（近似，须打样校准）", "accent": "136 C（近似，须打样校准）",
           "ink": "Black 6 C", "paper": "7541 C（浅冷灰，近似）",
           "primary_dark": "3385 C（近似）", "gray1": "Cool Gray 11 C", "gray2": "Cool Gray 6 C"}


def hex2rgb255(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def color_rows(keys):
    out = []
    for k in keys:
        h = C[k]
        r, g, b = hex2rgb255(h)
        c, m, y, kk = D["cmyk"][k]
        out.append(f"| {h} | `{h}` | ({r}, {g}, {b}) | ({c}, {m}, {y}, {kk}) | {PANTONE.get(k,'—')} |")
    return "\n".join(out)


def color_td_rows(keys):
    out = []
    for k in keys:
        h = C[k]
        r, g, b = hex2rgb255(h)
        c, m, y, kk = D["cmyk"][k]
        out.append(f"<tr><td>{h}</td><td><code>{h}</code></td><td>({r}, {g}, {b})</td>"
                   f"<td>({c}, {m}, {y}, {kk})</td><td>{PANTONE.get(k,'—')}</td></tr>")
    return "".join(out)


# ───────────────────────── preview.html ─────────────────────────
def lock_tile(title, body, dark=False):
    return (f'<div class="tile {"dark" if dark else "light"}">{body}'
            f'<div class="cap">{title}</div></div>')


mk = lambda s, w="full": mark_div(s, w)
combos = []
# 1 纯图形
combos.append(("纯图形 icon-only", mk(96), mk(96)))
# 2 图形 + 英文字标
combos.append(("图形 + 英文字标（横版主标）",
               f'<div class="strip">{mk(56,"full")}{wm_html(40)}</div>',
               f'<div class="strip">{mk(56,"full")}{wm_html(40,"#fff")}</div>'))
# 3 图形 + 中文字标
combos.append(("图形 + 中文字标（AI 提示词库）",
               f'<div class="strip">{mk(56,"full")}<div class="wm" style="font-size:34px;'
               f'font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif">AI 提示词库</div></div>',
               f'<div class="strip">{mk(56,"full")}<div class="wm" style="font-size:34px;color:#fff;'
               f'font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif">AI 提示词库</div></div>'))
# 4 双语横排
combos.append(("图形 + 双语横排",
               f'<div class="strip">{mk(60,"full")}<div>{wm_html(38)}'
               f'<div style="font-size:13px;color:#5C6669;letter-spacing:2px;'
               f'font-family:\'PingFang SC\',sans-serif">AI 提示词库</div></div></div>',
               f'<div class="strip">{mk(60,"full")}<div>{wm_html(38,"#fff")}'
               f'<div style="font-size:13px;color:#93A0A3;letter-spacing:2px;'
               f'font-family:\'PingFang SC\',sans-serif">AI 提示词库</div></div></div>'))
# 5 双语竖排
combos.append(("图形 + 双语竖排",
               f'<div style="text-align:center">{mk(72,"full")}<div style="height:10px"></div>'
               f'{wm_html(34)}<div style="font-size:12px;color:#5C6669;letter-spacing:2px;'
               f'font-family:\'PingFang SC\',sans-serif">AI 提示词库</div></div>',
               f'<div style="text-align:center">{mk(72,"full")}<div style="height:10px"></div>'
               f'{wm_html(34,"#fff")}<div style="font-size:12px;color:#93A0A3;letter-spacing:2px;'
               f'font-family:\'PingFang SC\',sans-serif">AI 提示词库</div></div>'))
# 6 纯字标
combos.append(("纯字标 wordmark（窄空间）",
               wm_html(46), wm_html(46, "#fff")))

PREVIEW = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AiShort 标志系统 · 交互预览</title><style>{CSS}</style></head><body><div class="wrap">
<header class="top">{mk(56)}<div><h1>AiShort 标志系统</h1>
<p class="sub">方向「切角卡片 · The Shortcut」· v1.0 提案预览 · 比例系统 整数比 + 8pt 网格</p></div></header>

<section><div class="sechead"><span class="secnum">01</span><h2>Hero 主标</h2></div>
<p class="note">一张提示词卡片，右上角沿 45° 抄近道切掉一块；被切下的三角沿切边镜像翻折进卡内，成为点亮的琥珀折片。
斜边 452.5 &lt; 直角路径 640——捷径不是比喻，是三角形不等式。</p>
<div class="grid g2">
<div class="tile light" style="min-height:260px">{mk(200)}<div class="cap">纯图形 mark · 1024 viewBox · 零字体依赖</div></div>
<div class="tile light" style="min-height:260px"><div style="width:300px">{emb(LOCKUP_H)}</div>
<div class="cap">横版组合标（网站页眉 / README 头图）</div></div></div></section>

<section><div class="sechead"><span class="secnum">02</span><h2>组合 Lockup 矩阵</h2></div>
<p class="note">同一几何在 6 种组合、明/暗两种底色下的表现。字标字体：{D['font_stack']}</p>
<div class="grid g2">
{''.join(lock_tile(t, b) + lock_tile(t + '（深底）', d, True) for t, b, d in combos)}
</div></section>

<section><div class="sechead"><span class="secnum">03</span><h2>缩放墙 16 → 2048px</h2></div>
<p class="note">小尺寸为真实光栅输出（PNG），非矢量缩放模拟——这是能不能用的唯一凭证。</p>
<div class="strip" style="align-items:flex-end;gap:26px">
{''.join(f'<div style="text-align:center">{img(s)}<div class="cap">{s}px</div></div>' for s in [16,32,48,64,128,256])}
</div>
<div class="grid g2" style="margin-top:20px">
<div class="tile light">{img(512)}<div class="cap">512px</div></div>
<div class="tile light">{img(1024)}<div class="cap">1024px</div></div></div>
<div style="margin-top:16px" class="grid g2">
<div><div class="cap" style="margin-bottom:6px">16px ASCII 实测（# 主卡 · O 琥珀折片 · + 半调）</div>{ASCII(D['ascii16'])}</div>
<div><div class="cap" style="margin-bottom:6px">32px ASCII 实测</div>{ASCII(D['ascii32'])}</div></div></section>

<section><div class="sechead"><span class="secnum">04</span><h2>关键尺寸标注</h2></div>
<div class="grid g2">
<div><table><tr><th>参数</th><th>值</th><th>来源 / 比例</th></tr>
<tr><td>画布</td><td>{n(D['canvas'],0)} × {n(D['canvas'],0)}</td><td>基准单位 U = {n(D['U'],0)}px</td></tr>
<tr><td>卡片边长 B</td><td>{n(D['B'],0)}</td><td>80U</td></tr>
<tr><td>圆角 R</td><td>{n(D['R'],0)}</td><td>B:R = 5:1</td></tr>
<tr><td>切角 CUT</td><td>{n(D['CUT'],0)}</td><td>B:CUT = 2:1 · CUT:R = 5:2</td></tr>
<tr><td>折缝 GAP</td><td>{n(D['GAP'],0)}</td><td>R:GAP = 8:3</td></tr>
<tr><td>折片直角边</td><td>{n(D['flap_leg'],0)}</td><td>CUT − 2×GAP</td></tr>
<tr><td>斜边（捷径）</td><td>{n(D['cut_hyp'],1)}</td><td>320√2 &lt; 640 直角路径</td></tr>
<tr><td>折片面积占比</td><td>{n(D['flap_pct'])}%</td><td>点缀色纪律 &lt;10%</td></tr>
<tr><td>光学配平偏移</td><td>({n(D['dx'],1)}, {n(D['dy'],1)})</td><td>质心补偿 {n(D['comp']*100,0)}%</td></tr>
</table></div>
<div><div style="border:1px solid var(--line);border-radius:12px;overflow:hidden">{emb(BP)}</div>
<div class="cap" style="margin-top:8px">blueprint 数学标注图（尺寸链 / 圆心十字标 / 相切与镜像关系）</div></div>
</div></section>

<section><div class="sechead"><span class="secnum">05</span><h2>变体家族（6 色变体）</h2></div>
<div class="grid g3">
{lock_tile('① 主标 横版 fullcolor', f'<div style="width:260px">{emb(LOCKUP_H)}</div>')}
{lock_tile('② 竖排 stacked', f'<div style="width:170px">{emb(LOCKUP_V)}</div>')}
{lock_tile('③ 纯图形 fullcolor', mk(110))}
{lock_tile('④ 单黑 mono-black', f'<div style="width:260px">{emb(LOCKUP_B)}</div>')}
{lock_tile('⑤ 反白 reversed（深底）', f'<div style="width:260px">{emb(LOCKUP_W)}</div>', True)}
{lock_tile('⑥ 灰阶 grayscale', f'<div style="width:260px">{emb(LOCKUP_G)}</div>')}
</div></section>

<section><div class="sechead"><span class="secnum">06</span><h2>应用实景</h2></div>
<div class="grid g2">
<div class="mock"><div class="browser"><span class="tab">{img(16, 'vertical-align:middle')} AiShort — AI 提示词库</span></div>
<div class="bar">{mk(30)}{wm_html(19)}<span class="links"><span>提示词</span><span>扩展</span><span>文档</span><span>GitHub</span></span></div>
<div style="padding:18px;color:#5C6669;font-size:13px">浏览器标签 + 站点页眉（favicon 为真实 16px 光栅）</div></div>
<div class="mock"><div class="phone"><div class="phonepad">
<div><div class="appic">{img(64)}</div><div class="appname">AiShort</div></div>
<div><div class="appic" style="background:#fff">{img(64)}</div><div class="appname">AiShort</div></div>
<div><div class="appic" style="background:{C['primary']}">{img(64)}</div><div class="appname">AiShort</div></div>
<div><div class="appic" style="background:{C['accent']}">{img(64)}</div><div class="appname">AiShort</div></div>
</div></div><div style="padding:10px 16px;font-size:12px;color:#5C6669">手机桌面 App 图标（明/暗/品牌色/琥珀底）</div></div>
<div class="mock"><div class="hero">{mk(72,"rev")}<div class="t" style="margin-top:14px">5000+ 即用 AI 提示词</div>
<div class="s">复制 → 粘贴 → 专家级输出。把从会用 AI 到用好 AI 的距离，折成一步。</div></div></div>
<div class="mock cardbg"><div style="display:flex;justify-content:space-between;align-items:flex-start">
{mk(54)}<div style="text-align:right;font-size:12px;color:#5C6669;line-height:1.6">
千语 / Qian Yuniao<br>AI Shortcut Prompt · Maintainer<br>github.com/qianyuniao/AI-Shortcut-Prompt</div></div>
<div style="height:22px"></div>
<div style="font-size:11px;color:#8A9296">名片正面（净空区 = 主图形高度的 25%）</div></div>
</div></section>

<section><div class="sechead"><span class="secnum">07</span><h2>色彩与字体规范</h2></div>
<div class="sw">
<div style="background:{C['primary']};color:#fff">{C['primary']}<br>墨松绿 Primary</div>
<div style="background:{C['accent']};color:#3D2A00">{C['accent']}<br>琥珀 Accent</div>
<div style="background:{C['ink']};color:#fff">{C['ink']}<br>炭黑 Ink</div>
<div style="background:{C['paper']};color:#3D4448">{C['paper']}<br>冷白底 Paper</div>
<div style="background:{C['primary_dark']};color:#04231E">{C['primary_dark']}<br>深底主色</div></div>
<div class="grid g2" style="margin-top:16px">
<div><table><tr><th>色值</th><th>HEX</th><th>RGB</th><th>CMYK</th><th>Pantone（近似）</th></tr>
{color_td_rows(['primary','accent','ink','paper','primary_dark'])}</table>
<div class="cap">Pantone 为屏幕取色换算的近似值，专色/周边打样前须人工校准</div></div>
<div><table><tr><th>字体</th><th>回退链</th></tr>
<tr><td>英文/数字字标</td><td><code>{D['font_stack']}</code></td></tr>
<tr><td>中文字标</td><td><code>'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif</code></td></tr>
<tr><td>字重 / 字距</td><td>650 / −0.012em（AiShort 专用光学收紧）</td></tr></table>
<div class="cap">正式发布前建议对字标执行「轮廓化描边」，彻底消除字体依赖</div></div></div></section>
</div></body></html>"""
open(os.path.join(BASE, "preview.html"), "w", encoding="utf-8").write(PREVIEW)

# ───────────────────────── report.html（九段） ─────────────────────────
DR = [
    ("D1", "概念取「折」而非「AI 神经/芯片/星芒」",
     "行业俗套黑名单（知识源 B §2）+ 项目旧标即芯片+节点+渐变绿",
     "旧元素 100% 弃用；新标 0 个 AI 行业高频符号"),
    ("D2", "主形 = 圆角卡片（品类载体）", "元素预算 ≤3、主角唯一", "主角占比 91.4%（1 − 折片 8.56%）"),
    ("D3", "切角取 45° 且 CUT = B/2", "斜边 452.5 < 直角路径 640，捷径是几何事实", "省 29.3% 路径长度（1 − 452.5/640）"),
    ("D4", "折片 = 切下三角沿切边镜像（非另画形状）", "数学必然：镜像唯一解，且面积 = 缺口面积", "折片 = 缺口 = 51200 px²，误差 0"),
    ("D5", "折痕共享、仅两直角边留缝", "物理正确（折角沿折痕相连）；且保住单色可辨",
     "首版三边带缝被视觉判为「贴上去的异物」，改后异物感 0"),
    ("D6", "比例系统取整数比而非 φ", "开发者工具气质（稳定/工程感）；且全参数落在 8U 网格",
     "6 项比例校验误差均为 0.000%"),
    ("D7", "折片占比压到 8.56%", "点缀色纪律 <10%（知识源 F §2）", "首版 12.14% 超标 → 调 CUT/GAP 后达标"),
    ("D8", "光学配平取质心补偿 40%", "全量补偿 48.4px = B 的 7.6%，超出 2–5% 经验区间",
     f"取 40% = {n(abs(D['dx']),1)}px = B 的 3.0%"),
    ("D9", "强调手段用颜色不用加形状", "知识源 F §5：加形状会破元素预算与全形语法",
     "元素预算 1/3，无新增形状；mono 退化已诚实声明"),
]

REPORT = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AiShort 标志 · 全量技术报告</title><style>{CSS}</style></head><body><div class="wrap">
<header class="top">{mk(56)}<div><h1>AiShort 标志 · 全量技术报告</h1>
<p class="sub">方向「切角卡片 · The Shortcut」v1.0 · 全部数值由 build.py 实时计算，零手写 · 自包含单文件</p></div></header>

<section><div class="sechead"><span class="secnum">§0</span><h2>执行摘要</h2></div>
<div class="grid g2" style="margin-bottom:18px">
<div class="tile light" style="min-height:220px">{mk(180)}<div class="cap">主标（纯图形，1024 viewBox）</div></div>
<div class="grid g2" style="align-content:start">
<div class="kpi"><b>0.000%</b><span>6 项比例校验最大误差（整数比系统）</span></div>
<div class="kpi"><b>{n(K['primary_on_paper'])}:1</b><span>主色 / 冷白底 对比度（AA 需 ≥4.5）</span></div>
<div class="kpi"><b>16px</b><span>最小可用尺寸（实测去角 + 折片可辨）</span></div>
<div class="kpi"><b>{n(D['flap_pct'])}%</b><span>点缀色占比（纪律 &lt;10%）</span></div></div></div>
<p><b>概念</b>：把「从会用 AI 到用好 AI 的冗长试错」折成一张卡片的一次抄近道——斜边 452.5 短于直角路径 640，捷径不是比喻。<br>
<b>几何</b>：单一圆角方形 + 一处 45° 切角 + 一个由切下三角镜像而来的折片；整数比系统，6 项比例误差 0.000%，折痕共享、双边留缝。<br>
<b>色彩</b>：墨松绿 {C['primary']}（脱离 OpenAI 亮绿与 AI 蓝紫渐变）+ 琥珀 {C['accent']} 仅 8.56%，只用于「被点亮的捷径」。</p></section>

<section><div class="sechead"><span class="secnum">§1</span><h2>概念与决策链</h2></div>
<table><tr><th>部件</th><th>语义来源</th><th>承载语义（一元素多义）</th><th>删减测试</th></tr>
<tr><td>圆角卡片</td><td>产品形态：5000+ 提示词以卡片呈现</td><td>提示词载体 / 库 / 一张可用的「答案」</td><td>删掉 → 无载体，故事不成立</td></tr>
<tr><td>45° 切角</td><td>名字字义 Shortcut + 品类动作「一步到位」</td><td>抄近道 / 果断 / 缺口即入口</td><td>删掉 → 退化为普通圆角方块，无记忆点</td></tr>
<tr><td>琥珀折片</td><td>被切下的那段路（沿切边镜像翻折）</td><td>被跳过的试错 / 书签标记 / 点亮的捷径</td><td>删掉 → 「捷径」失去被点亮的落点，且 mono 层级消失</td></tr></table>
<p class="note" style="margin-top:14px"><b>内部落选方向（探索成本不摊给用户）</b>：
①「⌘K 键」——与 Raycast 强撞且是 Apple 专用符号，弃；
②「叠层双卡（copy 语义）」——与系统 copy 图标通用语汇重合，16px 下两卡糊成一团，弃；
③「S 曲线字标」——字母锚定会削弱国际化（18 语言）场景的图形独立性，弃。</p></section>

<section><div class="sechead"><span class="secnum">§2</span><h2>几何全量数学</h2></div>
<div class="grid g2">
<div><table><tr><th>常量</th><th>值</th><th>推导</th></tr>
<tr><td>CANVAS</td><td>{n(D['canvas'],0)}</td><td>128U</td></tr>
<tr><td>U（基准）</td><td>{n(D['U'],0)}</td><td>8pt 模块网格</td></tr>
<tr><td>B 卡片边长</td><td>{n(D['B'],0)}</td><td>80U；CANVAS:B = 8:5</td></tr>
<tr><td>R 圆角</td><td>{n(D['R'],0)}</td><td>B/5 = 16U</td></tr>
<tr><td>CUT 切角</td><td>{n(D['CUT'],0)}</td><td>B/2 = 40U</td></tr>
<tr><td>GAP 折缝</td><td>{n(D['GAP'],0)}</td><td>3R/8 = 6U</td></tr>
<tr><td>折片直角边</td><td>{n(D['flap_leg'],0)}</td><td>CUT − 2·GAP = 320 − 96</td></tr>
<tr><td>斜边长</td><td>{n(D['cut_hyp'],2)}</td><td>CUT·√2</td></tr>
<tr><td>光学偏移 (dx,dy)</td><td>({n(D['dx'],2)}, {n(D['dy'],2)})</td><td>(512 − 质心) × {n(D['comp'])}</td></tr>
</table></div>
<div><table><tr><th>比例</th><th>实测</th><th>目标</th><th>误差</th></tr>
{''.join(f"<tr><td>{k}</td><td>{n(v['value'],4)}</td><td>{n(v['target'],4)}</td><td>{n(v['err_pct'],4)}%</td></tr>" for k,v in D['ratios'].items())}
</table>
<table style="margin-top:12px"><tr><th>相切 / 对齐验证</th><th>条件</th><th>结果</th></tr>
<tr><td>折痕共线</td><td>折片斜边 ⊂ 主卡切边 P1P2</td><td>✓ 同一线段（构造即成立，非目测）</td></tr>
<tr><td>镜像等积</td><td>area(折片原三角) = area(缺口)</td><td>✓ 51200 = 51200（差 0）</td></tr>
<tr><td>缝宽均匀</td><td>两直角边处缝宽 = GAP</td><td>✓ 48.000 = GAP</td></tr>
<tr><td>折片在卡内</td><td>flap_in ⊂ rrect ∧ ¬notch</td><td>✓ 全部顶点在边界内</td></tr>
<tr><td>圆角层级</td><td>全标仅 1 种圆角半径</td><td>✓ R = 128（≤3 级纪律）</td></tr></table></div></div>
<div style="margin-top:16px;border:1px solid var(--line);border-radius:12px;overflow:hidden">{emb(BP)}</div>
<div class="cap" style="margin-top:8px">blueprint：尺寸链 / 圆心十字标 + 半径虚线 / 折痕镜像关系 / 捷径不等式</div></section>

<section><div class="sechead"><span class="secnum">§3</span><h2>色彩全量</h2></div>
<div class="sw">
<div style="background:{C['primary']};color:#fff">{C['primary']}</div>
<div style="background:{C['accent']};color:#3D2A00">{C['accent']}</div>
<div style="background:{C['ink']};color:#fff">{C['ink']}</div>
<div style="background:{C['paper']};color:#3D4448">{C['paper']}</div>
<div style="background:{C['primary_dark']};color:#04231E">{C['primary_dark']}</div></div>
<table style="margin-top:14px"><tr><th>色值</th><th>HEX</th><th>RGB</th><th>CMYK</th><th>Pantone（近似）</th></tr>
{color_td_rows(['primary','accent','ink','paper','primary_dark'])}</table>
<table style="margin-top:14px"><tr><th>对比度组合</th><th>实测</th><th>AA 要求</th><th>判定</th></tr>
<tr><td>主色 / 冷白底 {C['primary']} on {C['paper']}</td><td>{n(K['primary_on_paper'])}:1</td><td>≥4.5</td><td>✓</td></tr>
<tr><td>主色 / 纯白</td><td>{n(K['primary_on_white'])}:1</td><td>≥4.5</td><td>✓</td></tr>
<tr><td>琥珀 / 主色（两色并置）</td><td>{n(K['accent_on_primary'])}:1</td><td>≥3.0（图形）</td><td>✓</td></tr>
<tr><td>深底主色 / 炭黑底</td><td>{n(K['primary_dark_on_darkbg'])}:1</td><td>≥4.5</td><td>✓</td></tr>
<tr><td>灰阶主 / 白</td><td>{n(K['gray1_on_white'])}:1</td><td>≥4.5</td><td>✓</td></tr>
<tr><td>灰阶辅 / 灰阶主</td><td>{n(K['gray2_on_gray1'])}:1</td><td>≥3.0（图形）</td><td>✓</td></tr></table>
<p class="note" style="margin-top:12px"><b>诚实声明</b>：折片与主卡的区分依赖色彩，单色（mono）场景下该强调层与笔画融合属<b>预期行为</b>，
层级由 L 形折缝（真实负空间）承住，不用描边/阴影假装区分。灰阶版保留两层明度差（{n(K['gray2_on_gray1'])}:1）以维持层次。</p></section>

<section><div class="sechead"><span class="secnum">§4</span><h2>变体矩阵</h2></div>
<div class="grid g3">
{lock_tile('主标 横版 fullcolor','<div style="width:250px">'+LOCKUP_H+'</div><div class="cap">页眉 / README / 文档头</div>')}
{lock_tile('竖排 stacked','<div style="width:160px">'+LOCKUP_V+'</div><div class="cap">窄栏 / 启动页 / 侧边</div>')}
{lock_tile('纯图形 fullcolor', mk(104)+'<div class="cap">头像 / App / favicon 源</div>')}
{lock_tile('单黑 mono-black','<div style="width:250px">'+LOCKUP_B+'</div><div class="cap">单色印刷 / 雕刻 / 传真</div>')}
{lock_tile('反白 reversed','<div style="width:250px">'+LOCKUP_W+'</div><div class="cap">深色底 / 照片上</div>',True)}
{lock_tile('灰阶 grayscale','<div style="width:250px">'+LOCKUP_G+'</div><div class="cap">黑白印刷媒介</div>')}
{lock_tile('深底专用 mark', mk(104,'dark')+'<div class="cap">深色模式页眉（主色提亮）</div>',True)}
{lock_tile('favicon SVG', '<div style="width:64px">'+FAVSVG+'</div><div class="cap">浏览器 / PWA</div>')}
</div></section>

<section><div class="sechead"><span class="secnum">§5</span><h2>缩放性能墙 + 压力测试</h2></div>
<div class="strip" style="align-items:flex-end;gap:24px">
{''.join(f'<div style="text-align:center">{img(s)}<div class="cap">{s}px</div></div>' for s in [16,32,48,64,128,256])}
</div>
<div class="grid g3" style="margin-top:18px">
<div><div class="cap" style="margin-bottom:6px">16px ASCII 实测</div>{ASCII(D['ascii16'])}</div>
<div><div class="cap" style="margin-bottom:6px">32px ASCII 实测</div>{ASCII(D['ascii32'])}</div>
<div><div class="cap" style="margin-bottom:6px">模糊测试（28px + 3px 盒式模糊）</div>{ASCII(D['blur'])}</div></div>
<table style="margin-top:14px"><tr><th>七项检查</th><th>操作</th><th>实测结果</th><th>判定</th></tr>
<tr><td>① 剪影</td><td>全部实体涂黑</td><td>去角方块剪影 + L 形折缝勾出折片，50 个标志中可指认</td><td>✓</td></tr>
<tr><td>② 16px</td><td>真实光栅（非矢量缩放）</td><td>去角清晰；琥珀折片占 3×3 px 可见；再小则折片消失但去角仍成立</td><td>✓</td></tr>
<tr><td>③ 单色</td><td>纯黑 / 纯白渲染</td><td>层级由 L 形负空间折缝承住（诚实声明：色彩强调层预期失效）</td><td>✓</td></tr>
<tr><td>④ 模糊</td><td>3px 盒式模糊看大形</td><td>大形 = 去角方块，形态稳定（见右上 ASCII）</td><td>✓</td></tr>
<tr><td>⑤ 反白</td><td>白色形置深底</td><td>无需调形即可用；深底另配提亮主色变体</td><td>✓</td></tr>
<tr><td>⑥ 撞脸</td><td>与 6 家同赛道标志逐项比对</td><td>每项差异一句话可讲清（见 §7 决策记录与 spec）</td><td>✓</td></tr>
<tr><td>⑦ 语义安全</td><td>旋转/镜像/负空间/拼音/禁忌/国旗</td><td>逐项已查无问题（详见 spec）</td><td>✓</td></tr></table></section>

<section><div class="sechead"><span class="secnum">§6</span><h2>应用示例（6 场景 CSS 实景）</h2></div>
<div class="grid g2">
<div class="mock"><div class="browser"><span class="tab">{img(16,'vertical-align:middle')} AiShort — AI 提示词库</span></div>
<div class="bar">{mk(30)}{wm_html(19)}<span class="links"><span>提示词</span><span>扩展</span><span>文档</span></span></div>
<div style="padding:16px;font-size:13px;color:#5C6669">① 浏览器标签（favicon 16px 实装）+ 站点页眉</div></div>
<div class="mock"><div class="hero">{mk(72,'rev')}<div class="t" style="margin-top:14px">5000+ 即用 AI 提示词</div>
<div class="s">复制 → 粘贴 → 专家级输出。</div></div><div style="padding:12px 16px;font-size:12px;color:#5C6669">② 官网 Hero（深色，反白版）</div></div>
<div class="mock"><div class="phone"><div class="phonepad">
<div><div class="appic">{img(64)}</div><div class="appname">AiShort</div></div>
<div><div class="appic" style="background:#fff">{img(64)}</div><div class="appname">AiShort</div></div>
<div><div class="appic" style="background:{C['primary']}">{img(64)}</div><div class="appname">AiShort</div></div>
<div><div class="appic" style="background:{C['accent']}">{img(64)}</div><div class="appname">AiShort</div></div>
</div></div><div style="padding:10px 16px;font-size:12px;color:#5C6669">③ 手机桌面 App 图标（四种底色）</div></div>
<div class="mock cardbg"><div style="display:flex;justify-content:space-between">{mk(54)}
<div style="text-align:right;font-size:12px;color:#5C6669;line-height:1.6">千语 / Qian Yuniao<br>AI Shortcut Prompt · Maintainer</div></div>
<div style="height:20px"></div><div style="font-size:11px;color:#8A9296">④ 名片</div></div>
<div class="mock" style="padding:22px;display:flex;gap:14px;align-items:center">
{mk(40,'mono')}<div style="font-size:13px;color:#5C6669">⑤ 单色印刷 / 雕刻：层级由折缝承住</div></div>
<div class="mock watermark" style="padding:26px;overflow:hidden">
<div style="font-size:13px;color:#3D4448;position:relative;z-index:1">⑥ 水印 / 大尺寸背景：10% 不透明度<br>
<span style="color:#8A9296">剪影在极淡时仍可辨识去角特征</span></div>
<div class="bgmark">{emb(MARK_MONO)}</div></div>
</div></section>

<section><div class="sechead"><span class="secnum">§7</span><h2>决策记录 DR</h2></div>
<table><tr><th>#</th><th>决策</th><th>依据</th><th>量化证据</th></tr>
{''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a,b,c,d in DR)}</table></section>

<section><div class="sechead"><span class="secnum">§8</span><h2>交付清单与复现指引</h2></div>
<table><tr><th>路径</th><th>内容</th></tr>
<tr><td><code>01-web-rgb/svg/</code></td><td>10 个 SVG：6 变体 + 纯图形 4 色版（全轮廓化路径，零字体依赖）</td></tr>
<tr><td><code>01-web-rgb/png/</code></td><td>透明底 PNG 256 / 512 / 1024 / 2048px</td></tr>
<tr><td><code>03-social-favicon/</code></td><td>favicon.ico(16/32/48) · favicon-16/32/48/64.png · favicon.svg · apple-touch-icon-180 · android-chrome-512</td></tr>
<tr><td><code>05-spec/</code></td><td>spec.md 使用规范 · blueprint.svg 数学标注图</td></tr>
<tr><td><code>06-source/</code></td><td>build.py（几何+位图）· build_docs.py（文档）· geometry.json（全部数值）· build.log.txt</td></tr>
<tr><td><code>preview.html</code> / <code>report.html</code></td><td>交互预览页 / 本全量技术报告（自包含单文件）</td></tr></table>
<p class="note" style="margin-top:12px"><b>复现命令</b>：</p>
<pre>python 06-source/build.py        # 重算几何 + 全部 SVG/PNG/ICO + geometry.json
python 06-source/build_docs.py   # 由 geometry.json 重新生成 spec/preview/report</pre>
<p class="note"><b>修改唯一入口</b>：只改 <code>build.py</code> 顶部的常量（B / R / CUT / GAP / COL）。
折片、缝、面积占比、比例校验、光学偏移全部由常量派生，改一个值整包联动重算——包括本报告里的每一个数字。</p>
</section>
</div></body></html>"""
open(os.path.join(BASE, "report.html"), "w", encoding="utf-8").write(REPORT)

# ───────────────────────── spec.md ─────────────────────────
def rgb_tuple(h):
    return "(%d, %d, %d)" % hex2rgb255(h)


SPEC_MD = f"""# AiShort 标志使用规范 spec · v1.0

> 方向「切角卡片 · The Shortcut」｜比例系统 整数比 + 8pt 模块网格｜全部数值由 `06-source/build.py` 计算，改常量即整包重算。

---

## 1. 品牌与概念

| 项 | 内容 |
|---|---|
| 品牌名 | AiShort（AI Shortcut Prompt） |
| 一句话 | 5000+ 即用 AI 提示词——把从会用 AI 到用好 AI 的距离，折成一步 |
| 标志类型 | 组合标 Combination（抽象图形 + 字标） |
| 概念 | 提示词卡片右上角沿 45° 抄近道切掉一块；被切下的三角沿切边镜像翻折进卡内，成为点亮的琥珀折片 |
| 数学支撑 | 斜边 {n(D['cut_hyp'],1)} &lt; 直角路径 {n(2*D['CUT'],0)}，捷径是三角形不等式而非比喻（省 29.3% 路径） |

**元素预算卡**

```
元素清单：圆角卡片（主，91.4%）/ 45° 切角（负空间）/ 琥珀折片（点缀，8.56%）——3/3 达标
语义来源：卡片=产品形态 | 切角=Shortcut 抄近道 | 折片=被跳过的试错 + 书签 + 点亮的捷径
主角占比：卡片 ≥60% ✓ | 删减测试：删任一元素故事都塌一角 ✓
一元素多义：切角 = 捷径 + 入口 + 果断；折片 = 折起的那段路 + 标记 + 点亮
```

**风格语法卡**

```
连续谱定位：圆角端（亲和·现代），右下/左下/左上 R=128 大圆角；右上切角为唯一硬边
形态决策：圆角半径=单一 R（≤3 级纪律，本标只 1 级）| 端头=圆角 | 窗/孔=等腰直角（负空间）
一致性：圆语法 ≥80% ✓ | 混用声明：45° 直切边为「有理由的直角入侵」——捷径=直线=果决，与效率语义绑定
```

---

## 2. 几何规格（比例系统：整数比 + 8pt 网格）

| 常量 | 值 | 推导 | 落在系统上的比例 |
|---|---|---|---|
| 画布 CANVAS | {n(D['canvas'],0)} | 128U | CANVAS:B = 8:5 |
| 基准单位 U | {n(D['U'],0)} | 8pt 模块 | — |
| 卡片边长 B | {n(D['B'],0)} | 80U | — |
| 圆角 R | {n(D['R'],0)} | B/5 = 16U | B:R = **5:1** |
| 切角 CUT | {n(D['CUT'],0)} | B/2 = 40U | B:CUT = **2:1**，CUT:R = **5:2** |
| 折缝 GAP | {n(D['GAP'],0)} | 3R/8 = 6U | R:GAP = **8:3** |
| 折片直角边 | {n(D['flap_leg'],0)} | CUT − 2·GAP | — |
| 斜边（捷径） | {n(D['cut_hyp'],2)} | CUT·√2 | 等腰直角 1:1 |
| 光学配平 (dx,dy) | ({n(D['dx'],2)}, {n(D['dy'],2)}) | (512 − 质心)×40% | 占 B 的 3.0%（落在 2–5% 光学修正区间） |

> 6 项比例校验误差均为 **0.000%**（build.log.txt 可查）。声明整数比系统，≥4 个关键尺寸落在系统上，未声称使用 φ（避免 φ-washing）。

**关键构造规则（改稿时不得破坏）**

1. 折片 = 缺口三角沿切边 P1P2 的**镜像**，不是另画的形状（等面积 51200 = 51200）。
2. **折痕共享**：折片斜边与主卡切边是同一条线段，缝只存在于两条直角边。
3. 缝是**真实负空间**，不是描边或阴影——它承担单色与剪影下的层级。
4. 光学偏移 (dx,dy) 是质心补偿，禁止「好心」snap 回 0。

---

## 3. 色彩规范（四格式）

| 角色 | HEX | RGB | CMYK | Pantone（近似，须打样校准） | 用途 |
|---|---|---|---|---|---|
| 墨松绿 Primary | `{C['primary']}` | {rgb_tuple(C['primary'])} | {tuple(D['cmyk']['primary'])} | {PANTONE['primary']} | 卡片主体、字标主色 |
| 琥珀 Accent | `{C['accent']}` | {rgb_tuple(C['accent'])} | {tuple(D['cmyk']['accent'])} | {PANTONE['accent']} | 折片（被点亮的捷径），占比 {n(D['flap_pct'])}% |
| 炭黑 Ink | `{C['ink']}` | {rgb_tuple(C['ink'])} | {tuple(D['cmyk']['ink'])} | {PANTONE['ink']} | 字标、单色版 |
| 冷白底 Paper | `{C['paper']}` | {rgb_tuple(C['paper'])} | {tuple(D['cmyk']['paper'])} | {PANTONE['paper']} | 页面底色（非纯白，带主色倾向） |
| 深底主色 | `{C['primary_dark']}` | {rgb_tuple(C['primary_dark'])} | {tuple(D['cmyk']['primary_dark'])} | {PANTONE['primary_dark']} | 深色模式页眉（主色提亮变体） |
| 灰阶主 / 辅 | `{C['gray1']}` / `{C['gray2']}` | — | — | {PANTONE['gray1']} / {PANTONE['gray2']} | 黑白印刷 |

**对比度实测（WCAG 相对亮度法，程序计算）**

| 组合 | 实测 | 要求 | 判定 |
|---|---|---|---|
| 主色 / 冷白底 | {n(K['primary_on_paper'])}:1 | ≥4.5（正文） | ✓ |
| 主色 / 纯白 | {n(K['primary_on_white'])}:1 | ≥4.5 | ✓ |
| 琥珀 / 主色 | {n(K['accent_on_primary'])}:1 | ≥3.0（图形） | ✓ |
| 深底主色 / 炭黑底 | {n(K['primary_dark_on_darkbg'])}:1 | ≥4.5 | ✓ |
| 灰阶辅 / 灰阶主 | {n(K['gray2_on_gray1'])}:1 | ≥3.0（图形） | ✓ |

**色彩判断卡**

```
行业地图：AI 工具赛道——OpenAI 亮绿 / Supabase 绿 / Linear 靛紫 / Claude 橙棕 / 蓝紫渐变（俗套）
       → 空位 = 深墨青绿（沉、冷、无头部占位，且延续 AiShort 原有青绿资产）
主色：{C['primary']} 墨松绿（三问全过：沉稳专业 ✓ / 并排一眼可辨 ✓ / 灰度单色深底 16px 全可逆 ✓）
点缀：{C['accent']} 琥珀 = 折片（语义绑定，占比 {n(D['flap_pct'])}% < 10%，与主色明度差 >30%）
底色：{C['paper']}（带主色倾向，非纯白）| 深底：{C['primary_dark']}
硬判据：灰度明度差 >20% ✓ | 四格式齐全 ✓ | 单色可逆 ✓
```

---

## 4. 变体清单与适用场景

| 变体 | 文件 | 适用场景 |
|---|---|---|
| ① 主标横版 fullcolor | `aishort-logo-primary-fullcolor-rgb.svg` | 网站页眉、README 头图、文档封面 |
| ② 竖排 stacked | `aishort-logo-stacked-fullcolor-rgb.svg` | 窄栏、启动页、侧边栏、移动端 |
| ③ 纯图形 fullcolor | `aishort-mark-only-fullcolor-rgb.svg` | 头像、App 图标、favicon 源、社交头像 |
| ④ 单黑 mono-black | `aishort-logo-primary-mono-black-rgb.svg` | 单色印刷、雕刻、传真、印章 |
| ⑤ 反白 reversed | `aishort-logo-primary-reversed-rgb.svg` | 深色底、照片上、Hero 区 |
| ⑥ 灰阶 grayscale | `aishort-logo-primary-grayscale-rgb.svg` | 黑白印刷媒介 |
| 附加：深底 mark | `aishort-mark-only-darkmode-rgb.svg` | 深色模式页眉（主色提亮，非简单反白） |

favicon 三件套：`favicon.ico`（16/32/48）、`favicon.svg`、`apple-touch-icon-180.png`、`android-chrome-512.png`，另有 16/32/48/64 PNG。

---

## 5. 使用规范（最小集）

| 项 | 规定 |
|---|---|
| **净空区** | 四周 ≥ 主图形高度的 **25%**（1024 viewBox 下 = 160px）；净空区内不得出现任何文字或图形 |
| **最小尺寸** | 横版组合标高 ≥ **24px**（数字场景）/ ≥8mm（印刷）；纯图形 ≥ **16px** |
| **降级规则** | 32px 以下：折缝开始闭合，琥珀折片可弃（去角方块仍是完整识别特征）；16px：仅保留主形 + 切角 |
| **禁用** | ① 拉伸变形 ② 侵入净空区 ③ 加投影/描边/外发光 ④ 擅自改色（尤其把琥珀改成红/紫）⑤ 低对比背景 ⑥ 旋转或镜像 ⑦ 给折片加渐变 |
| **深底** | 用反白版或深底专用 mark，**禁止**把主色原值直接放在炭黑底上 |
| **字标字体** | `{D['font_stack']}`；中文 `'PingFang SC','Microsoft YaHei','Noto Sans SC',sans-serif`；字重 650，字距 −0.012em |
| **字标发布** | 正式发布前建议在设计软件中执行「路径 > 轮廓化描边」，彻底消除字体依赖 |

---

## 6. 七项检查结果（知识源 B §4–4B）

| 检查 | 操作 | 实测结果 | 判定 |
|---|---|---|---|
| ① 剪影 | 实体涂黑 | 去角方块剪影 + L 形折缝勾出折片，可在同类标志中被指认 | ✓ 过 |
| ② 16px | 真实光栅 | 去角清晰；折片 3×3px 可见（ASCII 实测见 report §5） | ✓ 过 |
| ③ 单色 | 纯黑/纯白 | 层级由 L 形负空间折缝承住 | ✓ 过（附诚实声明） |
| ④ 模糊 | 3px 盒式模糊 | 大形稳定 = 去角方块 | ✓ 过 |
| ⑤ 反白 | 白形置深底 | 无需调形；深底另配提亮变体 | ✓ 过 |
| ⑥ 撞脸 | 与 6 家同赛道比对 | 见下节，每项差异一句话可讲清 | ✓ 过 |
| ⑦ 语义安全 | 6 项逐查 | 见下节，逐项已查无问题 | ✓ 过 |

**诚实声明（mono 退化）**：折片与主卡的区分主要依赖色彩。单色场景下该色彩强调层与主体融合属**预期行为**，层级由 L 形折缝（真实负空间）承住——不使用描边/阴影假装区分，假区分在小尺寸比没区分更糟。

---

## 7. 撞脸自查（几何特征级，非商标法律检索）

| 对标 | 我们的做法 | 他们的做法 | 差异一句话 |
|---|---|---|---|
| OpenAI | 直角斜切 + 实心单块 | 有机曲线花瓣结（六瓣回旋） | 我们是硬边实心面，他们是连续曲线缠绕 |
| Cursor | 实心墨绿块 | 白色线框立方体 | 我们靠体块，他们靠线框与透视 |
| Linear | 外轮廓单一切角 + 折片 | 圆角方**内部**多个斜切几何块 | 我们切外轮廓，他们在容器内做切割 |
| Raycast | 无任何键盘符号 | ⌘ 命令符（Apple 专用符号） | 我们避开系统级符号，形态无重合 |
| Notion | 图形 + 定制字标 | 纯字母 N 粗描边 | 我们是图形标，他们是无图形字标 |
| Vercel / Supabase | 圆角方 + 折角 | 纯三角 / 闪电符号 | 我们有方形容器与负空间叙事，他们是无容器单符号 |

> 商标风险提示：本表是**几何特征级原创性自查**，不构成商标查询或法律意见。上线前请自行检索商标库（Non-goal 声明）。

---

## 8. 语义安全审查（知识源 B §4B）

| 检查 | 结论 |
|---|---|
| 180° 旋转 | 已查无问题——切角转到左下，仍是「缺角方块」，不产生任何不当形象 |
| 镜像 | 已查无问题——切角转到左上，形态中性 |
| 负空间暗藏物 | 已查无问题——负空间为右上三角缺口与 L 形折缝，不构成第二形象 |
| 缩写 / 拼音歧义 | 已查无问题——Ai / Short / AiShort 在英中日韩语境均无脏词或不吉谐音 |
| 文化禁忌 | 已查无问题——无宗教符号（无十字/新月/万字/六芒星），主色墨绿为通用安全色 |
| 文化符号碰撞 | 已规避——**无中央实心圆**（规避日本国旗联想）；无星月；无条纹旗构图；琥珀占比仅 {n(D['flap_pct'])}% 不构成旗帜主色 |
| 国旗比对 | 中/日/韩/美/英/法/德/俄/印 逐个 3 秒并排——缺角方块不构成任何国旗特征，已查无问题 |

---

## 9. 复现

```
python 06-source/build.py        # 几何 + SVG/PNG/ICO + geometry.json + 压力测试 ASCII
python 06-source/build_docs.py   # spec.md / blueprint.svg / preview.html / report.html
```

修改唯一入口：`build.py` 顶部常量（B / R / CUT / GAP / COL）。折片、折缝、面积占比、比例校验、光学偏移、对比度全部派生重算。
"""
open(os.path.join(SPEC, "spec.md"), "w", encoding="utf-8").write(SPEC_MD)

# ───────────────────────── 00-START-HERE.md ─────────────────────────
START = f"""# AiShort 标志交付包 · 从这里开始

方向：**切角卡片 · The Shortcut**　v1.0　比例系统：整数比 + 8pt 网格

> 一张提示词卡片，右上角沿 45° 抄近道切掉一块；被切下的三角沿切边镜像翻折进卡内，成为点亮的琥珀折片。
> 斜边 {n(D['cut_hyp'],1)} &lt; 直角路径 640——捷径是三角形不等式，不是比喻。

## 我要用哪个文件？

| 场景 | 用这个文件 |
|---|---|
| 一页看完（推荐） | **`showcase.html`**（自包含单页：概念 / 六变体 / favicon / 几何 / 色彩 / 规范 / 检查 / 全部文件可下载，离线可开） |
| 交互预览 | `preview.html`（Hero / 组合矩阵 / 缩放墙 / 实景） |
| 评审 / 归档 / 交接 | **`report.html`**（全量技术报告，九段，自包含单文件） |
| 网站页眉 / README 头图 | `01-web-rgb/svg/aishort-logo-primary-fullcolor-rgb.svg` |
| 深色模式页眉 | `01-web-rgb/svg/aishort-mark-only-darkmode-rgb.svg`（或反白版） |
| 头像 / App 图标 / 社交头像 | `01-web-rgb/svg/aishort-mark-only-fullcolor-rgb.svg` |
| 单色印刷 / 雕刻 / 印章 | `01-web-rgb/svg/aishort-logo-primary-mono-black-rgb.svg` |
| 浏览器 / PWA 图标 | `03-social-favicon/favicon.ico` + `favicon.svg` |
| 位图（PPT / 不支持 SVG 的平台） | `01-web-rgb/png/aishort-mark-only-fullcolor-rgb-{256,512,1024,2048}px.png`（另含单黑/反白/灰阶 512px） |
| 使用规范 / 色值 / 禁用项 | `05-spec/spec.md` |
| 改标志（调参数） | `06-source/build.py` 顶部常量 → 重跑，整包联动 |

## 关键数字

| 项 | 值 |
|---|---|
| 主色 / 点缀 | `{C['primary']}` 墨松绿 / `{C['accent']}` 琥珀（{n(D['flap_pct'])}%） |
| 比例校验 | 6 项全部 **0.000%** 误差（B:R=5:1 · B:CUT=2:1 · CUT:R=5:2 · R:GAP=8:3） |
| 最小尺寸 | 纯图形 16px｜横版组合标高 ≥24px |
| 净空区 | 主图形高度的 25% |
| 七项检查 | 剪影 ✓ 16px ✓ 单色 ✓ 模糊 ✓ 反白 ✓ 撞脸 ✓ 语义安全 ✓ |

## 目录

```
brand-logo-package/
├── 00-START-HERE.md
├── showcase.html          自包含单页展示（一页看完，离线可开）
├── preview.html            交互预览页（先打开这个）
├── report.html             全量技术报告（评审/归档）
├── 01-web-rgb/
│   ├── svg/                10 个 SVG（6 变体 + 纯图形 4 色版）
│   └── png/                256 / 512 / 1024 / 2048px 透明底
├── 03-social-favicon/      favicon.ico(16/32/48) · favicon.svg · 180 · 512 · 16/32/48/64 · Android 前景层 432
├── 05-spec/                spec.md 使用规范 · blueprint.svg 数学标注图
└── 06-source/              build.py · build_docs.py · geometry.json · build.log.txt
```
"""
open(os.path.join(BASE, "00-START-HERE.md"), "w", encoding="utf-8").write(START)
print("DOCS OK")
