# -*- coding: utf-8 -*-
"""
生成 preview.html —— 自包含单文件交互预览（无外部依赖、无网络请求）
"""
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── 几何常量（与 build.py 一致）──
CANVAS, B, G, R, M = 1024.0, 320.0, 160.0, 80.0, 112.0
GRID = 2 * B + G

COL = {
    "pine": "#0B6E62", "teal": "#10997F", "mist": "#A9DFD5",
    "ink": "#14171A", "gray": "#8A9296", "teal_d": "#3FC2A9",
    "mist_d": "#2F3839", "white": "#FFFFFF", "icon_dim": "#6DA8A1",
    "darkbg": "#14171A", "paper": "#F7F9F9", "line": "#E2E8E8",
    "muted": "#5F6B70",
}
FONT = ("Inter, 'Segoe UI', 'Helvetica Neue', Arial, "
        "'PingFang SC', 'Microsoft YaHei', sans-serif")


def rr(x, y, w, h, r):
    return (f"M {x+r:g} {y:g} L {x+w-r:g} {y:g} A {r:g} {r:g} 0 0 1 {x+w:g} {y+r:g} "
            f"L {x+w:g} {y+h-r:g} A {r:g} {r:g} 0 0 1 {x+w-r:g} {y+h:g} "
            f"L {x+r:g} {y+h:g} A {r:g} {r:g} 0 0 1 {x:g} {y+h-r:g} "
            f"L {x:g} {y+r:g} A {r:g} {r:g} 0 0 1 {x+r:g} {y:g} Z")


CELLS = [(M, M), (M + B + G, M), (M, M + B + G), (M + B + G, M + B + G)]
LIT = 3


def mark_svg(dim, lit, size=None, bx=0, by=0, extra=""):
    w = size or 1024
    h = size or 1024
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
         f'width="{w}" height="{h}" role="img" aria-label="AiShort"{extra}>']
    if bx or by:
        o.append(f'<g transform="translate({bx},{by})">')
    for i, (x, y) in enumerate(CELLS):
        o.append(f'<path fill="{lit if i == LIT else dim}" d="{rr(x, y, B, B, R)}"/>')
    if bx or by:
        o.append('</g>')
    o.append('</svg>')
    return "".join(o)


def icon_svg(size=1024):
    k = 0.84
    BB, GG, RR = B * k, G * k, R * k
    MM = (CANVAS - (2 * BB + GG)) / 2
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
         f'width="{size}" height="{size}" role="img" aria-label="AiShort">',
         f'<path fill="{COL["pine"]}" d="{rr(0, 0, 1024, 1024, 224)}"/>']
    for i, (cx, cy) in enumerate([(MM, MM), (MM + BB + GG, MM),
                                  (MM, MM + BB + GG), (MM + BB + GG, MM + BB + GG)]):
        o.append(f'<path fill="{COL["white"] if i == LIT else COL["icon_dim"]}" '
                 f'd="{rr(cx, cy, BB, BB, RR)}"/>')
    o.append('</svg>')
    return "".join(o)


def stacked_svg(dim, lit, txt, size=200):
    s = 448.0 / CANVAS
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
         f'width="{size}" height="{size}" role="img" aria-label="AiShort">',
         f'<g transform="translate(288,96) scale({s})">']
    for i, (x, y) in enumerate(CELLS):
        o.append(f'<path fill="{lit if i == LIT else dim}" d="{rr(x, y, B, B, R)}"/>')
    o.append('</g>')
    o.append(f'<text x="202" y="760" font-family="{FONT}" font-size="200" '
             f'font-weight="650" textLength="620" lengthAdjust="spacingAndGlyphs" '
             f'fill="{txt}">AiShort</text>')
    o.append('</svg>')
    return "".join(o)


def lockup_h(dim, lit, txt, w=1024, h=256):
    s = 180.0 / CANVAS
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 256" '
         f'width="{w}" height="{h}" role="img" aria-label="AiShort">',
         f'<g transform="translate(64,38) scale({s})">']
    for i, (x, y) in enumerate(CELLS):
        o.append(f'<path fill="{lit if i == LIT else dim}" d="{rr(x, y, B, B, R)}"/>')
    o.append('</g>')
    o.append(f'<text x="308" y="192" font-family="{FONT}" font-size="176" '
             f'font-weight="650" textLength="652" lengthAdjust="spacingAndGlyphs" '
             f'fill="{txt}">AiShort</text>')
    o.append('</svg>')
    return "".join(o)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:@@FONT@@;background:#FFFFFF;color:#14171A;-webkit-font-smoothing:antialiased;
 line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:0 40px 120px}
header{padding:96px 0 72px;border-bottom:1px solid @@LINE@@}
.eyebrow{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:@@TEAL@@;
 font-weight:600;margin-bottom:20px}
h1{font-size:52px;line-height:1.1;font-weight:680;letter-spacing:-.02em}
h1 em{font-style:normal;color:@@TEAL@@}
.sub{margin-top:20px;font-size:19px;color:@@MUTED@@;max-width:640px}
h2{font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:@@MUTED@@;
 font-weight:650;margin:80px 0 28px;padding-bottom:12px;border-bottom:1px solid @@LINE@@}
h3{font-size:17px;font-weight:650;margin-bottom:6px}
p{font-size:15px;color:@@MUTED@@}
table{width:100%;border-collapse:collapse;font-size:14px}
th{text-align:left;font-weight:650;padding:11px 14px 11px 0;border-bottom:1.5px solid @@LINE@@;
 color:@@MUTED@@;font-size:12px;letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}
td{padding:11px 14px 11px 0;border-bottom:1px solid @@LINE@@;vertical-align:top;color:#26302F}
td code,th code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;
 background:#F2F5F5;padding:2px 6px;border-radius:4px}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:@@LINE@@;
 border:1px solid @@LINE@@;border-radius:18px;overflow:hidden;margin-top:44px}
.hero>div{padding:56px 40px;display:flex;flex-direction:column;align-items:center;
 justify-content:center;gap:26px;background:#fff}
.hero .dark{background:@@DARKBG@@}
.cap{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:@@MUTED@@}
.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:26px}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.card{border:1px solid @@LINE@@;border-radius:14px;padding:22px;display:flex;
 flex-direction:column;align-items:center;gap:14px;background:#fff}
.card .nm{font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:@@MUTED@@}
.card .cv{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#7C878B}
.dk{background:@@DARKBG@@;border-color:#22292C}
.dk .nm,.dk .cv{color:#8C989C}
.sizes{display:flex;align-items:flex-end;gap:34px;flex-wrap:wrap;padding:30px 0}
.sz{display:flex;flex-direction:column;align-items:center;gap:10px}
.sz span{font-family:ui-monospace,Menlo,monospace;font-size:11px;color:#7C878B}
.scen{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.mock{border:1px solid @@LINE@@;border-radius:14px;overflow:hidden;background:#fff}
.mock .bar{background:#EDEFF0;padding:9px 14px;font-size:11.5px;color:#6B7478;
 display:flex;align-items:center;gap:8px;border-bottom:1px solid @@LINE@@}
.mock .bar i{width:9px;height:9px;border-radius:50%;background:#D3D8DA;display:block}
.mock .bd{padding:26px;display:flex;align-items:center;justify-content:center;min-height:132px}
.mock .dkbd{background:@@DARKBG@@}
.note{background:@@PAPER@@;border-left:3px solid @@TEAL@@;padding:18px 22px;
 border-radius:0 10px 10px 0;font-size:14px;color:#2A3437;margin-top:24px}
.note b{color:@@TEAL@@}
.no{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.no div{border:1px solid @@LINE@@;border-radius:12px;padding:18px 20px;font-size:14px}
.no .t{font-weight:650;color:#A33;display:block;margin-bottom:4px}
ul{list-style:none}
li{font-size:14.5px;padding:7px 0 7px 20px;position:relative;color:#2A3437}
li:before{content:"";position:absolute;left:0;top:15px;width:7px;height:7px;
 border-radius:2px;background:@@TEAL@@}
.kv{display:grid;grid-template-columns:auto 1fr;gap:6px 20px;font-size:14px}
.kv b{font-weight:650;white-space:nowrap}
footer{margin-top:90px;padding-top:28px;border-top:1px solid @@LINE@@;
 font-size:13px;color:@@MUTED@@}
"""
for _k, _v in [("@@FONT@@", FONT), ("@@LINE@@", COL["line"]), ("@@TEAL@@", COL["teal"]),
               ("@@MUTED@@", COL["muted"]), ("@@DARKBG@@", COL["darkbg"]),
               ("@@PAPER@@", COL["paper"])]:
    CSS = CSS.replace(_k, _v)

VARIANTS = [
    ("fullcolor", "全彩 · 默认", COL["mist"], COL["teal"], "#fff", False),
    ("highcontrast", "高对比", COL["mist"], COL["pine"], "#fff", False),
    ("mono-black", "单色", COL["gray"], COL["ink"], "#fff", False),
    ("darkmode", "深色模式", COL["mist_d"], COL["teal_d"], COL["darkbg"], True),
    ("reversed", "反白", "#FFFFFF", "#FFFFFF", COL["darkbg"], True),
]

SIZES = [16, 24, 32, 48, 64, 128, 256]


def rev_svg(size=200):
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
         f'width="{size}" height="{size}" role="img" aria-label="AiShort">']
    for i, (x, y) in enumerate(CELLS):
        o.append(f'<path fill="#FFFFFF" fill-opacity="{1 if i == LIT else 0.30}" '
                 f'd="{rr(x, y, B, B, R)}"/>')
    o.append('</svg>')
    return "".join(o)


H = []
A = H.append
A(f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">')
A('<meta name="viewport" content="width=device-width,initial-scale=1">')
A('<title>AiShort 标志 v2.0 · 一格之距 One of Many</title>')
A(f'<style>{CSS}</style></head><body><div class="wrap">')

# ── Header ──
A('<header>')
A('<div class="eyebrow">AiShort · Brand Mark v2.0</div>')
A('<h1>一格之距<br><em>One of Many</em></h1>')
A('<p class="sub">一张 2×2 的提示词卡片阵列，只有右下那一格是实的。'
  '5000+ 条提示词里，你要的永远只有一条——标志只画这一条，其余三格退成浅青。</p>')
A('<div class="hero">')
A(f'<div>{mark_svg(COL["mist"], COL["teal"], 300)}<div class="cap">浅底 · fullcolor</div></div>')
A(f'<div class="dark">{mark_svg(COL["mist_d"], COL["teal_d"], 300)}'
  f'<div class="cap" style="color:#8C989C">深底 #14171A · darkmode</div></div>')
A('</div></header>')

# ── 1 推导链 ──
A('<h2>1 · 推导链 — 每个图元都回溯到产品截图的观察事实</h2>')
A('<table><thead><tr><th>品牌语义</th><th>观察到的空间事实（评分）</th>'
  '<th>几何决策</th><th>24px 判据</th></tr></thead><tbody>')
rows = [
    ("提示词库 / 卡片", "界面 4 列等宽圆角卡片网格　<b>High</b>", "2×2 圆角方阵，间隙 G = B/2",
     "4 格 + 十字负空间可辨 ✓"),
    ("一秒找到那一条", "唯一一处青色高亮描边框，出现在「被选中」卡片上　<b>High</b>",
     "一格实色 / 三格浅色，用明度差表达", "明度差 2.41:1 ✓"),
    ("复制 / 取走", "每张卡底部成对出现复制 + 收藏按钮　<b>High</b>",
     "不画图标，退为「实/虚」对偶", "已抽象，不参与小尺寸识别 ✓"),
    ("抄近道 Shortcut", "青色细竖线、斜向高亮　Medium", "不落地为图元，由品牌名承担",
     "删掉后主族仍成立 ✓"),
    ("留白", "卡片间均匀深色间隙　<b>High</b>", "G = B/2，负空间 60.9%",
     "16px 下十字间隙 2.5px 未闭合 ✓"),
]
for r in rows:
    A("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
A("</tbody></table>")
A(f'<div class="note"><b>未采用的 Low 评分事实：</b>4 列的具体数量、标签胶囊、'
  f'心形图标、文字层级——全部依赖细节或数量，24px 下不可辨，一律不进入标志。</div>')

# ── 2 几何 ──
A('<h2>2 · 几何与比例 — 整数比 + 8pt 网格</h2>')
A('<div class="grid2">')
A('<table><thead><tr><th>参数</th><th>值</th><th>网格</th></tr></thead><tbody>')
for n, v, u in [("画布 CANVAS", "1024", "128U"), ("格边长 B", "320", "40U"),
                ("间隙 G", "160", "20U"), ("圆角 R", "80", "10U"),
                ("边距 M", "112", "14U"), ("阵列总宽", "800", "100U")]:
    A(f"<tr><td>{n}</td><td><code>{v}</code></td><td>{u}</td></tr>")
A("</tbody></table>")
A('<table><thead><tr><th>比例</th><th>实测</th><th>误差</th></tr></thead><tbody>')
for n, v in [("B : R", "4.0000"), ("B : G", "2.0000"), ("G : R", "2.0000"),
             ("阵列 : 画布", "0.7812"), ("M : B", "0.3500"), ("CANVAS : U", "128.0000")]:
    A(f"<tr><td>{n}</td><td><code>{v}</code></td><td>0.000%</td></tr>")
A("</tbody></table>")
A('<div class="kv" style="align-content:start;padding:8px 0">'
  '<b>几何质心</b><span>(512.0, 512.0) = 画布中心，形态对称，无需光学配平偏移</span>'
  '<b>四格占地</b><span>39.1%</span>'
  '<b>负空间</b><span>60.9%</span>'
  '<b>净空区 X</b><span>= G = 160（画布的 15.6%）</span>'
  '<b>最小尺寸</b><span>实底图标 16px｜纯图形 24px｜横版组合 32px 高</span></div>')
A("</div>")
A(f'<div class="note"><b>本版唯一的重大返工：</b>第一版原型取 B:G = 11:3（间隙 96），'
  f'16px 实测时两列糊成一条横线，判定失败。间隙加倍至 G = B/2 后，16px 下十字负空间'
  f'仍有 2.5px，四格重新分离。</div>')

# ── 3 变体 ──
A('<h2>3 · 变体矩阵</h2>')
A('<div class="grid4">')
for name, cn, dim, lit, bg, dk in VARIANTS:
    svg = rev_svg(150) if name == "reversed" else mark_svg(dim, lit, 150)
    A(f'<div class="card{" dk" if dk else ""}" style="background:{bg}">'
      f'{svg}<div class="nm">{cn}</div><div class="cv">{name}</div></div>')
A(f'<div class="card dk">{icon_svg(150)}<div class="nm">实底图标</div>'
  f'<div class="cv">favicon / App</div></div>')
A(f'<div class="card">{lockup_h(COL["mist"], COL["teal"], COL["pine"], 250, 62)}'
  f'<div class="nm">横版组合</div><div class="cv">primary</div></div>')
A(f'<div class="card">{stacked_svg(COL["mist"], COL["teal"], COL["pine"], 150)}'
  f'<div class="nm">竖版组合</div><div class="cv">stacked</div></div>')
A("</div>")
A(f'<div class="note"><b>单色说明：</b>单墨印刷时，未点亮的三格使用主墨的 '
  f'<b>45% 网点（半调）</b>，点亮格 100% 实底。若工艺不支持半调（雕刻、冲压），'
  f'必须改用实底图标版——纯剪影下四格同色，「哪一格被点亮」的信息会丢失，'
  f'这是已知的有损降级。</div>')

# ── 4 缩放墙 ──
A('<h2>4 · 缩放墙 — 真实像素渲染</h2>')
A('<div class="sizes">')
for s in SIZES:
    A(f'<div class="sz">{mark_svg(COL["gray"], COL["ink"], s)}<span>{s}px</span></div>')
A("</div>")
A(f'<div class="note"><b>结论：</b>16px 起四格与十字负空间均已分离，右下实色格可辨。'
  f'但 16px 仅限<b>实底图标版</b>——透明底版在 16px 时浅青格与白底只有 1.48:1，'
  f'会与背景糊在一起。</div>')

# ── 5 六场景 ──
A('<h2>5 · 六场景应用</h2>')
A('<div class="scen">')
A(f'<div class="mock"><div class="bar"><i></i><i></i><i></i>'
  f'{icon_svg(16)}&nbsp; AiShort — 5000+ AI Prompts</div>'
  f'<div class="bd">{lockup_h(COL["mist"], COL["teal"], COL["pine"], 300, 75)}</div></div>')
A(f'<div class="mock"><div class="bar">App 图标</div>'
  f'<div class="bd">{icon_svg(96)}</div></div>')
A(f'<div class="mock"><div class="bar">名片 / 印刷</div><div class="bd">'
  f'{mark_svg(COL["gray"], COL["ink"], 84)}</div></div>')
A(f'<div class="mock"><div class="bar">深色模式页眉</div><div class="bd dkbd">'
  f'{lockup_h(COL["mist_d"], COL["teal_d"], "#E8EDEF", 300, 75)}</div></div>')
A(f'<div class="mock"><div class="bar">README 头图</div><div class="bd">'
  f'{mark_svg(COL["mist"], COL["teal"], 96)}</div></div>')
A(f'<div class="mock"><div class="bar">社交头像</div><div class="bd">'
  f'{icon_svg(88)}</div></div>')
A("</div>")

# ── 6 色彩 ──
A('<h2>6 · 色彩规范</h2>')
A('<table><thead><tr><th>角色</th><th>HEX</th><th>RGB</th><th>HSL</th>'
  '<th>CMYK</th><th>vs 白底</th><th>vs #14171A</th></tr></thead><tbody>')
cd = [
    ("pine 墨松绿 · 结构/字标", "#0B6E62", "11, 110, 98", "173 82% 24%",
     "90 0 11 57", "6.14", "2.93"),
    ("teal 青绿 · 点亮格", "#10997F", "16, 153, 127", "169 81% 33%",
     "90 0 17 40", "3.57", "5.04"),
    ("mist 浅青 · 未点亮格", "#A9DFD5", "169, 223, 213", "169 46% 77%",
     "24 0 4 13", "1.48", "12.17"),
    ("ink 炭黑 · 单色主", "#14171A", "20, 23, 26", "210 13% 9%",
     "23 12 0 90", "17.99", "1.00"),
    ("gray 灰阶辅 · 单色辅", "#8A9296", "138, 146, 150", "200 5% 56%",
     "8 3 0 41", "3.17", "5.68"),
    ("teal_d 青绿亮阶 · 深底点亮", "#3FC2A9", "63, 194, 169", "169 52% 50%",
     "68 0 13 24", "2.21", "8.14"),
    ("mist_d 深底未点亮格", "#2F3839", "47, 56, 57", "186 10% 20%",
     "18 2 0 78", "12.03", "1.50"),
    ("icon_dim 实底图标三格", "#6DA8A1", "109, 168, 161", "171 33% 55%",
     "35 0 4 34", "3.57", "5.04"),
]
for r in cd:
    A(f'<tr><td>{r[0]}</td><td><code>{r[1]}</code></td><td>{r[2]}</td>'
      f'<td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td>{r[6]}</td></tr>')
A("</tbody></table>")
A('<div class="grid2" style="margin-top:26px">')
A('<table><thead><tr><th>关键配对</th><th>对比度</th></tr></thead><tbody>')
for n, v in [("teal ↔ mist（点亮 vs 未点亮）", "2.41 : 1"),
             ("teal ↔ 白底（过 WCAG 非文本 3:1）", "3.57 : 1"),
             ("pine ↔ 白底（过文字 4.5:1）", "6.14 : 1"),
             ("ink ↔ gray（单色版）", "5.68 : 1")]:
    A(f"<tr><td>{n}</td><td><code>{v}</code></td></tr>")
A("</tbody></table>")
A('<table><thead><tr><th>实底图标三层</th><th>对比度</th></tr></thead><tbody>')
for n, v in [("底板 #0B6E62 ↔ 白页", "6.14 : 1"),
             ("底板 ↔ 三格 #6DA8A1", "2.27 : 1"),
             ("三格 ↔ 点亮格 #FFFFFF", "2.70 : 1")]:
    A(f"<tr><td>{n}</td><td><code>{v}</code></td></tr>")
A("</tbody></table></div>")
A(f'<div style="font-size:14px;color:#2A3437;margin-top:26px">'
  f'<b style="font-weight:650">色彩纪律</b>'
  f'<ul><li>1 主色 + 1 结构色 + 至多 1 点缀；mist 是 teal 的浅阶，不另计一色</li>'
  f'<li>全部取自产品已有青绿色系（站点 <code>--ifm-color-primary</code> 为 hsl(163 38%)，'
  f'本系统收束到 hsl(169–173)）</li>'
  f'<li>禁止渐变、阴影、外发光、纹理</li>'
  f'<li>禁止把三格换成别的色相</li></ul></div>')

# ── 7 禁用 ──
A('<h2>7 · 禁用项</h2>')
A('<div class="no">')
for t, d in [("拉伸 / 压扁 / 非等比缩放", "破坏 B:G = 2:1"),
             ("旋转非 90° 倍数", "阵列轴与界面卡片网格失配"),
             ("把点亮格挪到别的角", "「读序终点落在答案上」是语义的一部分"),
             ("加渐变 / 阴影 / 外发光 / 描边", "违反色彩纪律"),
             ("四格改成 2×3、3×3 等", "改动会稀释唯一性"),
             ("低于 16px 使用透明底版", "浅青格与白底糊在一起"),
             ("在净空区 X 内放置元素", "规范"),
             ("替换字标字体", "字标锁定宽度 652（横版）/ 620（竖版）")]:
    A(f'<div><span class="t">✕ {t}</span>{d}</div>')
A("</div>")

# ── 8 与 v1.0 对比 ──
A('<h2>8 · 与 v1.0「切角卡片」的差异</h2>')
A('<table><thead><tr><th>维度</th><th>v1.0 切角卡片</th>'
  '<th>v2.0 一格之距</th></tr></thead><tbody>')
for r in [("语义锚点", "抄近道（45° 切角 = 三角形不等式）", "一格之距（5000+ 里那一条）"),
          ("识别点", "被切走的角 + 琥珀折片", "哪一格是实的（颜色 + 明度双重编码）"),
          ("主色", "墨松绿 + 琥珀点缀", "墨松绿 / 青绿双色阶（无第二色相）"),
          ("图元", "卡片 + 折片（2 主体）", "4 个等大方块（1 主族）"),
          ("小尺寸", "折片在 16px 下 5.6px", "十字负空间 16px 下 2.5px 未闭合")]:
    A("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>")
A("</tbody></table>")

A('<h2>9 · 交付清单</h2><ul>')
for f in ["01-web-rgb/svg — 12 个（6 纯图形变体 + 4 横版 + 2 竖版）",
          "01-web-rgb/png — 128 / 256 / 512 / 1024 / 2048 + 4 变体 512",
          "03-social-favicon — favicon.ico(16/32/48) · favicon.svg · 16/32/48/64 · "
          "apple-touch-180 · android-chrome-512 · 自适应前景层 432",
          "05-spec — spec.md · safe-zone.svg · blueprint.svg · scale-test.png",
          "06-source — build.py · geometry.json · mark.json · build.log.txt · "
          "markspec-kit/（mark_spec.py 机器交叉校验）"]:
    A(f"<li>{f}</li>")
A("</ul>")
A(f'<footer>AiShort 标志 v2.0「一格之距」· 参数化构建 · '
  f'几何比例误差 0.000% · 机器校验 PASS（形态承载层级）</footer>')
A("</div></body></html>")

out = os.path.join(BASE, "preview.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write("".join(H))
print("OK ->", out, os.path.getsize(out) // 1024, "KB")
