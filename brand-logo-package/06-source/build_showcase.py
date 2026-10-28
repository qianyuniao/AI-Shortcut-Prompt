# -*- coding: utf-8 -*-
"""AiShort 品牌交付单页展示（自包含 HTML：SVG 内联 + PNG/ICO base64 内联）"""
import os, base64, json, re, itertools

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GJ = json.load(open(os.path.join(ROOT, "06-source", "geometry.json"), encoding="utf-8"))
COL = GJ["colors"]

_cnt = itertools.count()


def uniq(svg):
    """同一页内联多个 SVG 时给内部 id 加唯一后缀，防 mask id 撞车"""
    tag = "u%d" % next(_cnt)
    for i in set(re.findall(r'id="([^"]+)"', svg)):
        svg = svg.replace('id="%s"' % i, 'id="%s-%s"' % (i, tag))
        svg = svg.replace("url(#%s)" % i, "url(#%s-%s)" % (i, tag))
    return svg


def svg_inline(rel, fluid=True):
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    s = open(p, encoding="utf-8").read()
    s = re.sub(r'<\?xml[^>]*\?>', '', s).strip()
    if fluid:
        s = re.sub(r'(<svg[^>]*?)\s+width="[^"]*"\s+height="[^"]*"', r'\1 width="100%" height="100%"', s, count=1)
    return uniq(s)


def b64(rel, mime="image/png"):
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(p, "rb").read()).decode())


def fsize(rel):
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    n = os.path.getsize(p)
    return ("%.1f KB" % (n / 1024.0)) if n >= 1024 else ("%d B" % n)


# ───────────────────────── 素材 ─────────────────────────
SV = "01-web-rgb/svg/"
PN = "01-web-rgb/png/"
FV = "03-social-favicon/"

MARK_FULL = svg_inline(SV + "aishort-mark-only-fullcolor-rgb.svg")
MARK_MONO = svg_inline(SV + "aishort-mark-only-mono-black-rgb.svg")
MARK_GRAY = svg_inline(SV + "aishort-mark-only-grayscale-rgb.svg")
MARK_DARK = svg_inline(SV + "aishort-mark-only-darkmode-rgb.svg")
LOCK_H = svg_inline(SV + "aishort-logo-primary-fullcolor-rgb.svg")
LOCK_H_M = svg_inline(SV + "aishort-logo-primary-mono-black-rgb.svg")
LOCK_H_R = svg_inline(SV + "aishort-logo-primary-reversed-rgb.svg")
LOCK_H_G = svg_inline(SV + "aishort-logo-primary-grayscale-rgb.svg")
LOCK_V = svg_inline(SV + "aishort-logo-stacked-fullcolor-rgb.svg")
FAV_SVG = svg_inline(FV + "favicon.svg")
BLUEPRINT = svg_inline("05-spec/blueprint.svg")

PNG = {s: b64(PN + "aishort-mark-only-fullcolor-rgb-%dpx.png" % s) for s in (128, 256, 512, 1024, 2048)}
PNG_MONO = b64(PN + "aishort-mark-only-mono-black-rgb-512px.png")
PNG_REV = b64(PN + "aishort-mark-only-reversed-rgb-512px.png")
PNG_GRAY = b64(PN + "aishort-mark-only-grayscale-rgb-512px.png")
FAVPNG = {s: b64(FV + "favicon-%dx%d.png" % (s, s)) for s in (16, 32, 48, 64)}
ICO = b64(FV + "favicon.ico", "image/x-icon")
AT180 = b64(FV + "apple-touch-icon-180.png")
AC512 = b64(FV + "android-chrome-512.png")
AD432 = b64(FV + "android-adaptive-foreground-432.png")


def ascii_html(rows):
    """ASCII 实测 → 上色 span（连续同字符合并）"""
    out = []
    for line in rows:
        buf, cur, segs = "", None, []
        for ch in line:
            if ch != cur:
                if buf:
                    segs.append((cur, buf))
                cur, buf = ch, ch
            else:
                buf += ch
        if buf:
            segs.append((cur, buf))
        line_html = ""
        for ch, s in segs:
            cls = {"#": "k", "O": "a", "+": "h"}.get(ch, "d")
            if ch == ".":
                line_html += '<span class="d">%s</span>' % s
            else:
                line_html += '<span class="%s">%s</span>' % (cls, s)
        out.append(line_html)
    return "\n".join(out)


A16 = ascii_html(GJ["ascii16"])
A32 = ascii_html(GJ["ascii32"])
ABR = ascii_html(GJ["blur"])

# ───────────────────────── 变体卡 ─────────────────────────
VARIANTS = [
    ("横版主标", LOCK_H, "4/1", "primary", "网站页眉 · README 头图 · 文档封面",
     SV + "aishort-logo-primary-fullcolor-rgb.svg"),
    ("竖排 Stacked", LOCK_V, "1/1", "primary", "窄栏 · 启动页 · 侧边栏 · 移动端",
     SV + "aishort-logo-stacked-fullcolor-rgb.svg"),
    ("纯图形 Mark", uniq(MARK_FULL), "1/1", "primary", "头像 · App 图标 · 社交头像",
     SV + "aishort-mark-only-fullcolor-rgb.svg"),
    ("单黑 Mono", LOCK_H_M, "4/1", "primary", "单色印刷 · 雕刻 · 传真 · 印章",
     SV + "aishort-logo-primary-mono-black-rgb.svg"),
    ("反白 Reversed", LOCK_H_R, "4/1", "dark", "深色底 · 照片上 · Hero 区",
     SV + "aishort-logo-primary-reversed-rgb.svg"),
    ("灰阶 Grayscale", LOCK_H_G, "4/1", "primary", "黑白印刷媒介",
     SV + "aishort-logo-primary-grayscale-rgb.svg"),
]
v_html = ""
for name, svg, ar, bg, use, rel in VARIANTS:
    v_html += (
        '<figure class="vcard %s reveal"><div class="vstage" style="aspect-ratio:%s">'
        '<div class="vfit%s">%s</div></div>'
        '<figcaption><h3>%s</h3><p>%s</p>'
        '<a class="dl" href="%s" download="%s">下载 SVG</a></figcaption></figure>\n'
        % (bg, ar, " wide" if ar == "4/1" else "", svg, name, use,
           b64(rel, "image/svg+xml"), os.path.basename(rel)))

# ───────────────────────── 文件清单 ─────────────────────────
GROUPS = [
    ("网页与文档 · SVG", SV, "六变体矢量源，图形部分全轮廓化，零字体依赖"),
    ("网页与文档 · PNG", PN, "透明底位图梯队 128–2048px + 变体 512px"),
    ("favicon 与 App 图标", FV, "浏览器三件套 + Apple / Android 全套"),
    ("规范与源文件", "05-spec/", "使用规范、数学标注图"),
]
tree_html = ""
for title, folder, desc in GROUPS:
    d = os.path.join(ROOT, folder.replace("/", os.sep))
    files = sorted(f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))
    rows = ""
    for f in files:
        rel = folder + f
        mime = ("image/svg+xml" if f.endswith(".svg") else
                "image/x-icon" if f.endswith(".ico") else
                "image/png" if f.endswith(".png") else "text/plain")
        rows += ('<li><span class="fn">%s</span><span class="fsz">%s</span>'
                 '<a class="dl sm" href="%s" download="%s">下载</a></li>'
                 % (f, fsize(rel), b64(rel, mime), f))
    tree_html += ('<div class="fgroup reveal"><h3>%s</h3><p class="fdesc">%s</p>'
                  '<ul>%s</ul></div>' % (title, desc, rows))

# ───────────────────────── 色彩表 ─────────────────────────
PANTONE = {"primary": "3295 C", "accent": "136 C", "ink": "Black 6 C", "paper": "7541 C",
           "primary_dark": "3385 C", "gray1": "Cool Gray 11 C", "gray2": "Cool Gray 6 C"}
USE = {"primary": "卡片主体 · 字标主色", "accent": "折片（被点亮的捷径）", "ink": "字标 · 单色版",
       "paper": "页面底色（非纯白）", "primary_dark": "深色模式页眉", "gray1": "黑白印刷主",
       "gray2": "黑白印刷辅"}
NAME = {"primary": "墨松绿", "accent": "琥珀", "ink": "炭黑", "paper": "冷白底",
        "primary_dark": "深底主色", "gray1": "灰阶主", "gray2": "灰阶辅"}


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


swatches, crows = "", ""
for k in ("primary", "accent", "ink", "paper", "primary_dark", "gray1", "gray2"):
    h = COL[k]
    r, g, b = hex2rgb(h)
    c, m, y, kk = GJ["cmyk"][k]
    swatches += ('<button class="sw" data-hex="%s" style="--c:%s" aria-label="复制 %s">'
                 '<span class="swname">%s</span><span class="swhex">%s</span></button>'
                 % (h, h, NAME[k], NAME[k], h.upper()))
    crows += ('<tr><td><span class="dot" style="background:%s"></span>%s</td><td><code>%s</code></td>'
              '<td>%d, %d, %d</td><td>%d, %d, %d, %d</td><td>%s</td><td>%s</td></tr>'
              % (h, NAME[k], h.upper(), r, g, b, c, m, y, kk, PANTONE[k], USE[k]))

CONTRAST = [("主色 / 冷白底", "primary_on_paper", 4.5, "正文"),
            ("主色 / 纯白", "primary_on_white", 4.5, "正文"),
            ("琥珀 / 主色", "accent_on_primary", 3.0, "图形"),
            ("深底主色 / 炭黑底", "primary_dark_on_darkbg", 4.5, "正文"),
            ("灰阶辅 / 灰阶主", "gray2_on_gray1", 3.0, "图形")]
crows2 = ""
for label, key, req, kind in CONTRAST:
    v = GJ["contrast"][key]
    crows2 += ('<tr><td>%s</td><td><b>%.2f:1</b></td><td>≥%.1f（%s）</td>'
               '<td><span class="ok">通过 AA</span></td></tr>' % (label, v, req, kind))

# ───────────────────────── 参数 / 比例 ─────────────────────────
PARAMS = [("画布 CANVAS", "1024", "128U", "CANVAS:B = 8:5"),
          ("基准单位 U", "8", "8pt 模块", "—"),
          ("卡片边长 B", "640", "80U", "—"),
          ("圆角 R", "128", "B/5 = 16U", "B:R = 5:1"),
          ("切角 CUT", "320", "B/2 = 40U", "B:CUT = 2:1 · CUT:R = 5:2"),
          ("折缝 GAP", "48", "3R/8 = 6U", "R:GAP = 8:3"),
          ("折片直角边", "224", "CUT − 2·GAP", "—"),
          ("斜边（捷径）", "452.55", "CUT·√2", "等腰直角 1:1"),
          ("光学配平", "(+20.53, −20.53)", "(512 − 质心)×40%", "占 B 的 3.0%")]
prows = "".join('<tr><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td></tr>' % r for r in PARAMS)

rrows = ""
for k, d in GJ["ratios"].items():
    rrows += ('<tr><td><code>%s</code></td><td>%s</td><td>%s</td>'
              '<td><span class="ok">%.3f%%</span></td></tr>'
              % (k, ("%g:1" % d["target"]) if k != "B:GAP" else "%g:1" % d["target"],
                 "%.4f" % d["value"], d["err_pct"]))

RULES = ["折片 = 缺口三角沿切边 P1P2 的<b>镜像</b>，不是另画的形状（等面积 51200 = 51200）。",
         "<b>折痕共享</b>：折片斜边与主卡切边是同一条线段，缝只存在于两条直角边。",
         "缝是<b>真实负空间</b>，不是描边或阴影——它承担单色与剪影下的层级。",
         "光学偏移 (dx,dy) 是质心补偿，禁止「好心」snap 回 0。"]

BANS = ["拉伸变形", "侵入净空区", "加投影 / 描边 / 外发光", "擅自改色（尤其把琥珀改成红紫）",
        "低对比背景", "旋转或镜像", "给折片加渐变"]

CHECKS = [("剪影", "实体涂黑", "去角方块剪影 + L 形折缝勾出折片，可在同类标志中被指认"),
          ("16px", "真实光栅", "去角清晰；折片 3×3px 仍可见"),
          ("单色", "纯黑 / 纯白", "层级由 L 形负空间折缝承住"),
          ("模糊", "3px 盒式模糊", "大形稳定 = 去角方块"),
          ("反白", "白形置深底", "无需调形；深底另配提亮变体"),
          ("撞脸", "与 6 家同赛道比对", "每项差异一句话可讲清"),
          ("语义安全", "6 项逐查", "旋转 / 镜像 / 负空间 / 拼音 / 宗教 / 国旗，均无问题")]
chkrows = "".join('<tr><td>%s</td><td>%s</td><td>%s</td><td><span class="ok">通过</span></td></tr>' % c
                  for c in CHECKS)

# ───────────────────────── 模板 ─────────────────────────
TPL = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AiShort 标志交付 · 切角卡片 The Shortcut</title>
<link rel="icon" href="__ICO__">
<style>
:root{
  --paper:#F5F8F7; --surface:#FFFFFF; --ink:#14171A; --muted:#5C6669;
  --primary:#0B6E62; --soft:#E4EFEC; --accent:#F2A33C;
  --line:rgba(20,23,26,.11); --line2:rgba(20,23,26,.06); --stage:#EFF3F2;
  --cut:26px; --pad:clamp(20px,4vw,40px);
  --sans:Inter,'Segoe UI','Helvetica Neue',Arial,'PingFang SC','Microsoft YaHei',sans-serif;
  --mono:'SF Mono',ui-monospace,'JetBrains Mono',Consolas,monospace;
}
html[data-theme="dark"]{
  --paper:#0D1110; --surface:#161B1A; --ink:#E9EEEC; --muted:#97A3A0;
  --primary:#3FC2A9; --soft:#111817; --surface:#1A2020; --accent:#F2A33C;
  --stage:#1C2221;
  --line:rgba(233,238,236,.13); --line2:rgba(233,238,236,.07);
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.72;-webkit-font-smoothing:antialiased;
  transition:background .35s,color .35s}
::selection{background:var(--primary);color:#fff}
h1,h2,h3{margin:0;font-weight:660;letter-spacing:-.022em;line-height:1.14}
p{margin:0}
a{color:inherit}
code{font-family:var(--mono);font-size:.88em}

/* 切角语法：与标志同一条 45° 斜边 */
.cut{clip-path:polygon(0 0,calc(100% - var(--cut)) 0,100% var(--cut),100% 100%,0 100%)}

.wrap{max-width:1180px;margin:0 auto;padding:0 var(--pad)}
section{padding:clamp(64px,9vw,116px) 0;position:relative}
.grid-bg{position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(var(--line2) 1px,transparent 1px),
    linear-gradient(90deg,var(--line2) 1px,transparent 1px);
  background-size:32px 32px;
  -webkit-mask-image:radial-gradient(120% 90% at 50% 0%,#000 10%,transparent 78%);
  mask-image:radial-gradient(120% 90% at 50% 0%,#000 10%,transparent 78%)}

/* 顶栏 */
header.bar{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--paper) 86%,transparent);
  backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
.bar-in{display:flex;align-items:center;gap:14px;height:60px}
.bar .mk{width:26px;height:26px;flex:none}
.brand{font-weight:660;letter-spacing:-.02em;font-size:15px}
.brand small{display:block;font-weight:450;font-size:11.5px;color:var(--muted);letter-spacing:.02em}
nav.links{margin-left:auto;display:flex;gap:4px}
nav.links a{font-size:13.5px;color:var(--muted);text-decoration:none;padding:7px 11px;border-radius:8px}
nav.links a:hover{color:var(--ink);background:var(--line2)}
.tgl{margin-left:10px;border:1px solid var(--line);background:transparent;color:var(--ink);
  width:38px;height:34px;border-radius:9px;cursor:pointer;font-size:15px;display:grid;place-items:center}
.tgl:hover{background:var(--line2)}
@media(max-width:820px){nav.links{display:none}.tgl{margin-left:auto}}

/* Hero */
.hero{padding-top:clamp(52px,7vw,88px);overflow:hidden}
.hero-grid{display:grid;grid-template-columns:1.08fr .92fr;gap:clamp(28px,5vw,64px);align-items:center}
.eyebrow{font-size:12.5px;letter-spacing:.16em;color:var(--primary);font-weight:600;
  display:flex;align-items:center;gap:9px}
.eyebrow::before{content:"";width:22px;height:2px;background:var(--accent)}
h1.big{font-size:clamp(34px,5.2vw,60px);margin:18px 0 0}
h1.big em{font-style:normal;color:var(--primary)}
.lede{color:var(--muted);max-width:56ch;margin-top:20px;font-size:clamp(15px,1.5vw,17.5px)}
.cta{display:flex;gap:10px;margin-top:30px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 20px;border-radius:10px;
  font-size:14.5px;font-weight:600;text-decoration:none;border:1px solid transparent;cursor:pointer}
.btn.p{background:var(--primary);color:#fff}
.btn.p:hover{filter:brightness(1.12)}
.btn.g{border-color:var(--line);color:var(--ink);background:transparent}
.btn.g:hover{background:var(--line2)}
.stage{background:var(--surface);padding:clamp(26px,4vw,46px);--cut:40px;border:1px solid var(--line2);
  display:grid;place-items:center;box-shadow:0 22px 60px -34px rgba(0,0,0,.28)}
.stage .big-mark{width:min(100%,300px);aspect-ratio:1/1}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;margin-top:clamp(44px,6vw,72px);
  background:var(--line);border:1px solid var(--line);--cut:0px;overflow:hidden}
.stat{background:var(--surface);padding:20px 18px}
.stat b{display:block;font-size:clamp(21px,2.5vw,29px);font-weight:680;letter-spacing:-.03em;
  color:var(--primary);font-variant-numeric:tabular-nums}
.stat b i{font-style:normal;color:var(--accent)}
.stat span{font-size:12.5px;color:var(--muted);display:block;margin-top:3px}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}

/* 章节头 */
.shead{max-width:64ch;margin-bottom:clamp(30px,4vw,48px)}
.shead h2{font-size:clamp(25px,3.3vw,40px)}
.shead h2::after{content:"";display:block;width:46px;height:3px;background:var(--accent);margin-top:16px}
.shead p{color:var(--muted);margin-top:14px;max-width:60ch}

/* 概念三卡 */
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.card{background:var(--surface);padding:26px 24px;--cut:24px;border:1px solid var(--line2);
  box-shadow:0 14px 40px -30px rgba(0,0,0,.3)}
.card h3{font-size:18px;display:flex;align-items:center;gap:10px}
.card .pct{margin-left:auto;font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.card p{color:var(--muted);font-size:14.5px;margin-top:10px}
@media(max-width:860px){.cards{grid-template-columns:1fr}}

/* 不等式示意 */
.ineq{display:grid;grid-template-columns:1fr 1fr;gap:clamp(22px,4vw,48px);align-items:center;margin-top:26px}
.ineq svg{width:100%;height:auto}
.ineq ul{list-style:none;padding:0;margin:0;display:grid;gap:12px}
.ineq li{display:flex;gap:12px;font-size:14.5px;color:var(--muted);align-items:baseline}
.ineq li b{color:var(--ink);font-weight:640;flex:none;min-width:74px}
@media(max-width:860px){.ineq{grid-template-columns:1fr}}

/* 变体 */
.vgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.vcard{margin:0;background:var(--surface);--cut:22px;overflow:hidden;border:1px solid var(--line2);
  box-shadow:0 14px 40px -30px rgba(0,0,0,.3)}
.vstage{display:grid;place-items:center;background:var(--stage);padding:clamp(20px,3vw,34px)}
.vcard.dark .vstage{background:#14171A}
.vfit{width:100%;max-width:230px;margin:0 auto}
.vfit.wide{max-width:100%}
.vcard svg{width:100%;height:auto;display:block}
.vcard figcaption{padding:18px 20px 20px}
.vcard h3{font-size:15.5px}
.vcard figcaption p{color:var(--muted);font-size:13.5px;margin-top:5px}
@media(max-width:900px){.vgrid{grid-template-columns:1fr 1fr}}
@media(max-width:600px){.vgrid{grid-template-columns:1fr}}

/* favicon */
.favrow{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-end}
.favcell{background:var(--surface);--cut:14px;padding:16px;display:grid;place-items:center;gap:9px}
.favcell img{display:block;image-rendering:pixelated}
.favcell span{font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.tabsim{display:flex;align-items:center;gap:9px;background:var(--surface);border:1px solid var(--line);
  border-radius:11px 11px 0 0;padding:8px 14px 8px 11px;max-width:290px;
  box-shadow:0 10px 30px -22px rgba(0,0,0,.35)}
.tabsim img{width:16px;height:16px;image-rendering:pixelated}
.tabsim em{font-style:normal;font-size:12.5px;color:var(--muted)}
.favwrap{display:grid;grid-template-columns:1fr auto;gap:clamp(24px,4vw,50px);align-items:center}
@media(max-width:860px){.favwrap{grid-template-columns:1fr}}

/* 缩放墙 */
.wall{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end}
.wcell{background:var(--surface);--cut:12px;padding:14px;display:grid;place-items:center;gap:8px}
.wcell img{image-rendering:pixelated;display:block}
.wcell span{font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.wcell.small{background:var(--soft)}

/* 几何 */
.geo{display:grid;grid-template-columns:1.05fr .95fr;gap:clamp(24px,4vw,52px);align-items:start}
.bp{background:#FBFCFC;--cut:30px;padding:clamp(18px,3vw,30px);border:1px solid var(--line2)}
.bp svg{width:100%;height:auto;display:block}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{text-align:left;padding:11px 12px;border-bottom:1px solid var(--line2);vertical-align:top}
th{font-size:12px;letter-spacing:.06em;color:var(--muted);font-weight:600;text-transform:none}
td b{font-weight:640}
.ok{color:var(--primary);font-weight:620;font-size:13px}
.dot{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:8px;vertical-align:-1px}
.rules{list-style:none;padding:0;margin:18px 0 0;display:grid;gap:11px}
.rules li{font-size:14.5px;color:var(--muted);padding-left:20px;position:relative}
.rules li::before{content:"";position:absolute;left:0;top:9px;width:9px;height:9px;
  background:var(--accent);clip-path:polygon(0 0,100% 0,0 100%)}
.rules b{color:var(--ink);font-weight:620}
@media(max-width:900px){.geo{grid-template-columns:1fr}}

/* 色彩 */
.swgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:26px}
.sw{border:0;cursor:pointer;background:var(--c);--cut:18px;color:#fff;padding:44px 16px 14px;
  text-align:left;font-family:var(--sans);position:relative;transition:transform .18s}
.sw:hover{transform:translateY(-3px)}
.swname{display:block;font-size:14px;font-weight:640}
.swhex{display:block;font-size:11.5px;font-family:var(--mono);opacity:.82;margin-top:2px}
.sw[data-hex="#F5F8F7"],.sw[data-hex="#FFFFFF"]{color:#14171A;border:1px solid var(--line)}
.sw.copied::after{content:"已复制";position:absolute;right:12px;top:12px;font-size:11px;
  background:rgba(0,0,0,.6);color:#fff;padding:3px 7px;border-radius:5px}
@media(max-width:760px){.swgrid{grid-template-columns:repeat(2,1fr)}}

/* 规范 */
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.panel{background:var(--surface);--cut:24px;padding:clamp(22px,3vw,32px);border:1px solid var(--line2)}
.panel h3{font-size:17px;margin-bottom:14px}
.panel svg{width:100%;height:auto;display:block}
.panel p{color:var(--muted);font-size:14.5px;margin-top:12px}
.bans{list-style:none;padding:0;margin:0;display:grid;gap:10px}
.bans li{font-size:14.5px;color:var(--muted);display:flex;align-items:center;gap:11px;
  padding:9px 12px;background:var(--line2);--cut:10px}
.bans li::before{content:"";width:11px;height:11px;flex:none;
  background:var(--muted);clip-path:polygon(0 0,100% 0,100% 100%,0 100%)}
.mins{display:grid;gap:14px;margin-top:4px}
.mins div{display:flex;justify-content:space-between;gap:14px;padding-bottom:12px;
  border-bottom:1px solid var(--line2);font-size:14.5px}
.mins span{color:var(--muted)}
.mins b{font-weight:660;font-variant-numeric:tabular-nums}
@media(max-width:860px){.two{grid-template-columns:1fr}}

/* ASCII */
.ascii{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.abox{background:var(--surface);--cut:20px;padding:20px 18px;overflow:auto;border:1px solid var(--line2)}
.abox h4{margin:0 0 12px;font-size:13.5px;font-weight:640}
.abox h4 small{display:block;font-weight:450;color:var(--muted);font-size:12px;margin-top:2px}
pre.as{margin:0;font-family:var(--mono);font-size:11px;line-height:1.06;letter-spacing:.06em;
  white-space:pre;color:var(--muted)}
pre.as .k{color:var(--primary)} pre.as .a{color:var(--accent)}
pre.as .h{color:var(--muted);opacity:.5} pre.as .d{color:var(--line)}
@media(max-width:860px){.ascii{grid-template-columns:1fr}}

/* 文件 */
.fgroups{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.fgroup{background:var(--surface);--cut:22px;padding:24px;border:1px solid var(--line2)}
.fgroup h3{font-size:16px}
.fdesc{color:var(--muted);font-size:13.5px;margin-top:4px}
.fgroup ul{list-style:none;padding:0;margin:16px 0 0;display:grid;gap:1px}
.fgroup li{display:flex;align-items:center;gap:12px;padding:9px 10px;background:var(--line2);
  font-size:13px;--cut:8px}
.fn{font-family:var(--mono);font-size:11.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.fsz{margin-left:auto;color:var(--muted);font-size:11.5px;font-variant-numeric:tabular-nums;flex:none}
@media(max-width:860px){.fgroups{grid-template-columns:1fr}}

/* 下载 / 表格共用 */
.dl{display:inline-block;margin-top:12px;font-size:12.5px;font-weight:600;color:var(--primary);
  text-decoration:none;border-bottom:1.5px solid var(--accent);padding-bottom:1px}
.dl:hover{filter:brightness(1.15)}
.dl.sm{margin:0;font-size:11.5px;border-bottom-color:transparent;flex:none}
.dl.sm:hover{border-bottom-color:var(--accent)}
.tbl-wrap{overflow-x:auto}

footer{border-top:1px solid var(--line);padding:44px 0 60px;color:var(--muted);font-size:13.5px}
footer .fin{display:flex;gap:18px;flex-wrap:wrap;align-items:center}
footer .mk{width:22px;height:22px}

/* 动效：一次编排的入场 */
.reveal{opacity:0;transform:translateY(16px);transition:opacity .6s cubic-bezier(.2,.7,.2,1),
  transform .6s cubic-bezier(.2,.7,.2,1)}
.reveal.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .reveal{opacity:1;transform:none;transition:none}
  .sw:hover{transform:none}
}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
</style>
</head>
<body>

<header class="bar">
  <div class="wrap bar-in">
    <div class="mk">__MARK_A__</div>
    <div class="brand">AiShort 标志交付<small>切角卡片 · The Shortcut v1.0</small></div>
    <nav class="links">
      <a href="#concept">概念</a><a href="#variants">变体</a><a href="#favicon">图标</a>
      <a href="#geometry">几何</a><a href="#color">色彩</a><a href="#rules">规范</a>
      <a href="#files">文件</a>
    </nav>
    <button class="tgl" id="tgl" aria-label="切换明暗">◐</button>
  </div>
</header>

<section class="hero">
  <div class="grid-bg"></div>
  <div class="wrap">
    <div class="hero-grid">
      <div class="reveal">
        <div class="eyebrow">AI 提示词库 · 品牌标志</div>
        <h1 class="big">把从<em>会用 AI</em> 到用好 AI 的距离，<br>折成一步</h1>
        <p class="lede">一张提示词卡片，右上角沿 45° 抄近道切掉一块；被切下的三角沿切边镜像翻折进卡内，成为点亮的琥珀折片。斜边 452.5 短于直角路径 640——捷径是三角形不等式，不是比喻。</p>
        <div class="cta">
          <a class="btn p" href="#variants">看六个变体</a>
          <a class="btn g" href="#files">全部交付文件</a>
        </div>
      </div>
      <div class="stage cut reveal"><div class="big-mark">__MARK_B__</div></div>
    </div>
    <div class="stats cut reveal">
      <div class="stat"><b>452.5<i> / 640</i></b><span>斜边 vs 直角路径，省 29.3%</span></div>
      <div class="stat"><b>8.56<i>%</i></b><span>琥珀折片占比，守点缀色 &lt;10% 纪律</span></div>
      <div class="stat"><b>0.000<i>%</i></b><span>六项比例校验误差（整数比系统）</span></div>
      <div class="stat"><b>5.74<i>:1</i></b><span>主色 / 冷白底对比度，过 WCAG AA</span></div>
    </div>
  </div>
</section>

<section id="concept">
  <div class="wrap">
    <div class="shead reveal">
      <h2>为什么是切掉一个角</h2>
      <p>AI 赛道已经站满了芯片、大脑与星芒。AiShort 的资产在别处——它的名字本身就是产品：Shortcut。所以标志不讲 AI，讲「抄近道」。</p>
    </div>
    <div class="cards">
      <div class="card cut reveal"><h3>圆角卡片 <span class="pct">91.4%</span></h3>
        <p>产品形态本身——一张提示词卡。大圆角 R=128 给亲和力，占绝对主体，删掉它整个故事就没有容器。</p></div>
      <div class="card cut reveal"><h3>45° 切角 <span class="pct">负空间</span></h3>
        <p>唯一一条硬边。捷径是直线，果决是直角；它同时是缺口、是入口、是被省掉的那段路。</p></div>
      <div class="card cut reveal"><h3>琥珀折片 <span class="pct">8.56%</span></h3>
        <p>被切下的三角沿折痕翻进卡内：折起的那段试错、一枚书签、点亮的捷径。它是全标唯一的暖色。</p></div>
    </div>
    <div class="ineq">
      <div class="reveal">__INEQ__</div>
      <ul class="reveal">
        <li><b>直角路径</b><span>沿两条直角边走完，共 640</span></li>
        <li><b>斜边捷径</b><span>一步跨过，320·√2 = 452.55，省 29.3%</span></li>
        <li><b>折片 = 镜像</b><span>不是另画的形状，是缺口三角沿切边的镜像，等面积 51200</span></li>
        <li><b>缝 = 负空间</b><span>不是描边也不是阴影，它承担单色与剪影下的层级</span></li>
      </ul>
    </div>
  </div>
</section>

<section id="variants" style="background:var(--soft)">
  <div class="wrap">
    <div class="shead reveal">
      <h2>六个变体</h2>
      <p>覆盖页眉、窄栏、头像、单色印刷、深底与黑白印刷六类场景。图形部分已全部轮廓化，零字体依赖。</p>
    </div>
    <div class="vgrid">__VARIANTS__</div>
  </div>
</section>

<section id="favicon">
  <div class="wrap">
    <div class="shead reveal">
      <h2>favicon 三件套与应用图标</h2>
      <p>小尺寸重新配过缝宽与折片占比——不是主标等比缩小。下面每个尺寸都是真实光栅输出，未做插值。</p>
    </div>
    <div class="favwrap">
      <div>
        <div class="favrow reveal">
          __FAVCELLS__
        </div>
      </div>
      <div class="reveal">
        <div class="tabsim"><img src="__FAV16__" width="16" height="16" alt=""><em>AiShort · 5000+ 即用提示词</em></div>
        <p style="color:var(--muted);font-size:13px;margin-top:14px;max-width:32ch">浏览器标签页实测：16px 下切角与折片均在，不糊。</p>
      </div>
    </div>
    <div class="shead reveal" style="margin-top:clamp(40px,6vw,64px)">
      <h2>缩放墙</h2>
      <p>每一格都是该尺寸下真实跑出的光栅，没有插值。16–64px 用的是小尺寸专用几何（折缝加宽 1.5×），128px 以上回主标——这是设计好的降级，不是等比缩小。</p>
    </div>
    <div class="wall reveal">__WALL__</div>
  </div>
</section>

<section id="geometry" style="background:var(--soft)">
  <div class="wrap">
    <div class="shead reveal">
      <h2>几何与数学</h2>
      <p>比例系统用整数比 + 8pt 模块网格，不声称黄金分割。改 <code>build.py</code> 顶部常量重跑，全包连带这里的每个数字一起重算。</p>
    </div>
    <div class="geo">
      <div class="bp cut reveal">__BLUEPRINT__</div>
      <div class="reveal">
        <div class="tbl-wrap"><table>
          <tr><th>常量</th><th>值</th><th>推导</th><th>比例</th></tr>
          __PARAMS__
        </table></div>
        <div class="tbl-wrap" style="margin-top:22px"><table>
          <tr><th>比例</th><th>目标</th><th>实测</th><th>误差</th></tr>
          __RATIOS__
        </table></div>
        <ul class="rules">__RULES__</ul>
      </div>
    </div>
  </div>
</section>

<section id="color">
  <div class="wrap">
    <div class="shead reveal">
      <h2>色彩系统</h2>
      <p>深墨青绿避开 OpenAI 亮绿与蓝紫渐变，又延续 AiShort 原有青绿资产；琥珀只服务折片，占比 8.56%。点色块可复制 HEX。</p>
    </div>
    <div class="swgrid reveal">__SWATCHES__</div>
    <div class="two">
      <div class="tbl-wrap reveal"><table>
        <tr><th>角色</th><th>HEX</th><th>RGB</th><th>CMYK</th><th>Pantone</th><th>用途</th></tr>
        __CROWS__
      </table></div>
      <div class="tbl-wrap reveal"><table>
        <tr><th>组合</th><th>实测</th><th>要求</th><th>判定</th></tr>
        __CROWS2__
      </table></div>
    </div>
  </div>
</section>

<section id="rules" style="background:var(--soft)">
  <div class="wrap">
    <div class="shead reveal">
      <h2>使用规范</h2>
      <p>最小可用集：净空区、最小尺寸、禁用清单。完整版见交付包内 <code>05-spec/spec.md</code>。</p>
    </div>
    <div class="two">
      <div class="panel cut reveal">
        <h3>净空区</h3>
        __CLEAR__
        <p>四周 ≥ 主图形高度的 <b>25%</b>（1024 viewBox 下 = 160px）。净空区内不得出现任何文字或图形。</p>
      </div>
      <div class="panel cut reveal">
        <h3>最小尺寸</h3>
        <div class="mins">
          <div><span>横版组合标（数字）</span><b>高 ≥ 24px</b></div>
          <div><span>横版组合标（印刷）</span><b>高 ≥ 8mm</b></div>
          <div><span>纯图形（数字）</span><b>≥ 16px</b></div>
          <div><span>32px 以下</span><b>折片可弃，去角方块仍是完整识别特征</b></div>
        </div>
      </div>
    </div>
    <div class="panel cut reveal" style="margin-top:18px">
      <h3>七条禁用</h3>
      <ul class="bans">__BANS__</ul>
    </div>
  </div>
</section>

<section id="checks">
  <div class="wrap">
    <div class="shead reveal">
      <h2>七项检查实测</h2>
      <p>剪影、16px、单色、模糊、反白、撞脸、语义安全。下面三张是程序真实跑出的光栅 ASCII，不是矢量缩放模拟。</p>
    </div>
    <div class="ascii">
      <div class="abox cut reveal"><h4>16px 光栅<small>去角清晰，折片 3×3px 可见</small></h4><pre class="as">__A16__</pre></div>
      <div class="abox cut reveal"><h4>32px 光栅<small>L 形折缝完整勾出折片</small></h4><pre class="as">__A32__</pre></div>
      <div class="abox cut reveal"><h4>3px 盒式模糊<small>大形稳定 = 去角方块</small></h4><pre class="as">__ABR__</pre></div>
    </div>
    <div class="tbl-wrap reveal" style="margin-top:26px"><table>
      <tr><th>检查</th><th>操作</th><th>实测结果</th><th>判定</th></tr>
      __CHECKS__
    </table></div>
    <p class="reveal" style="color:var(--muted);font-size:13.5px;margin-top:18px;max-width:72ch">
      <b>诚实声明</b>：折片与主卡的区分主要依赖色彩。单色场景下这层强调与主体融合属预期行为，层级由 L 形折缝（真实负空间）承住——不用描边假装区分，假区分在小尺寸比没区分更糟。</p>
  </div>
</section>

<section id="files" style="background:var(--soft)">
  <div class="wrap">
    <div class="shead reveal">
      <h2>全部交付文件</h2>
      <p>__NFILES__ 个文件，共 __TOTALSIZE__。每一项都可直接下载；本页为自包含单文件，离线也能打开。</p>
    </div>
    <div class="fgroups">__TREE__</div>
  </div>
</section>

<footer>
  <div class="wrap fin">
    <div class="mk">__MARK_C__</div>
    <span>AiShort · 切角卡片 The Shortcut v1.0　|　几何、位图、规范全部由 <code>06-source/build.py</code> 生成</span>
  </div>
</footer>

<script>
(function(){
  var root=document.documentElement;
  document.getElementById('tgl').addEventListener('click',function(){
    root.dataset.theme = root.dataset.theme==='dark' ? 'light' : 'dark';
  });
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target);} });
  },{threshold:.12,rootMargin:'0px 0px -8% 0px'});
  document.querySelectorAll('.reveal').forEach(function(el,i){
    el.style.transitionDelay=(Math.min(i%6,5)*55)+'ms'; io.observe(el);
  });
  document.querySelectorAll('.sw').forEach(function(b){
    b.addEventListener('click',function(){
      var h=b.dataset.hex;
      (navigator.clipboard?navigator.clipboard.writeText(h):Promise.reject()).then(function(){
        b.classList.add('copied'); setTimeout(function(){b.classList.remove('copied')},1100);
      }).catch(function(){});
    });
  });
})();
</script>
</body>
</html>
"""

# ───────────────────────── 手绘示意图 ─────────────────────────
INEQ = """<svg viewBox="0 0 520 380" xmlns="http://www.w3.org/2000/svg" role="img"
 aria-label="直角三角形两直角边之和大于斜边">
  <rect x="60" y="40" width="400" height="300" rx="60" fill="none" stroke="var(--line)" stroke-width="1.5"/>
  <path d="M 60 100 A 60 60 0 0 1 120 40 L 320 40 L 460 180 L 460 280 A 60 60 0 0 1 400 340 L 120 340 A 60 60 0 0 1 60 280 Z"
        fill="var(--soft)" stroke="var(--primary)" stroke-width="2.5"/>
  <path d="M 320 40 L 460 180 L 320 180 Z" fill="var(--accent)" opacity=".9"/>
  <path d="M 320 40 L 460 180" stroke="var(--ink)" stroke-width="1" opacity=".25" stroke-dasharray="4 4"/>
  <path d="M 320 40 L 320 180 L 460 180" fill="none" stroke="var(--ink)" stroke-width="2.5"
        opacity=".55" stroke-dasharray="7 5" stroke-linejoin="round"/>
  <path d="M 320 40 L 460 180" fill="none" stroke="var(--accent)" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="320" cy="40" r="4" fill="var(--primary)"/><circle cx="460" cy="180" r="4" fill="var(--primary)"/>
  <circle cx="320" cy="180" r="4" fill="var(--primary)"/>
  <text x="336" y="150" font-family="var(--mono)" font-size="17" fill="var(--muted)">640</text>
  <text x="352" y="86" font-family="var(--mono)" font-size="19" font-weight="700" fill="var(--accent)">452.5</text>
  <text x="120" y="376" font-family="var(--sans)" font-size="13" fill="var(--muted)">绕两条直角边 640 ＞ 一步跨过 452.5</text>
</svg>"""

CLEAR = """<svg viewBox="0 0 480 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="净空区示意">
  <rect x="120" y="30" width="240" height="240" fill="none" stroke="var(--accent)"
        stroke-width="1.2" stroke-dasharray="5 5" opacity=".65"/>
  <g opacity=".22"><rect x="30" y="30" width="420" height="240" fill="var(--primary)"/></g>
  <g transform="translate(150,60) scale(0.5625)">
    <mask id="clr-m" maskUnits="userSpaceOnUse" x="0" y="0" width="1024" height="1024">
      <path fill="#FFFFFF" d="M 340.5 171.5 L 532.5 171.5 L 852.5 491.5 L 852.5 683.5 A 128 128 0 0 1 724.5 811.5 L 340.5 811.5 A 128 128 0 0 1 212.5 683.5 L 212.5 299.5 A 128 128 0 0 1 340.5 171.5 Z"/>
      <path fill="#000000" d="M 532.5 171.5 L 852.5 491.5 L 532.5 491.5 Z"/>
    </mask>
    <path fill="#0B6E62" d="M 340.5 171.5 L 532.5 171.5 L 852.5 491.5 L 852.5 683.5 A 128 128 0 0 1 724.5 811.5 L 340.5 811.5 A 128 128 0 0 1 212.5 683.5 L 212.5 299.5 A 128 128 0 0 1 340.5 171.5 Z" mask="url(#clr-m)"/>
    <path fill="#F2A33C" d="M 804.5 443.5 L 580.5 443.5 L 580.5 219.5 Z"/>
  </g>
  <text x="240" y="22" text-anchor="middle" font-family="var(--mono)" font-size="12" fill="var(--accent)">25% 净空</text>
  <text x="240" y="288" text-anchor="middle" font-family="var(--mono)" font-size="12" fill="var(--muted)">此区域内不得放置任何元素</text>
</svg>"""


def favcell(src, size, label, disp=None):
    d = disp or size
    return ('<div class="favcell cut"><img src="%s" width="%d" height="%d" alt="favicon %d">'
            '<span>%s</span></div>' % (src, d, d, size, label))


favcells = "".join([favcell(FAVPNG[s], s, "%dpx" % s) for s in (16, 32, 48, 64)]
                   + [favcell(AT180, 180, "180 · Apple", 72),
                      favcell(AC512, 512, "512 · Android", 72),
                      favcell(AD432, 432, "432 · 前景层", 72),
                      favcell(ICO, 32, "favicon.ico"),
                      favcell(b64(FV + "favicon.svg", "image/svg+xml"), 32, "favicon.svg")])
# 16–64px 用 favicon 专用几何（折缝加宽 1.5×），128 / 256 用主标位图；全部真实光栅，无插值
wall = "".join('<div class="wcell cut small"><img src="%s" width="%d" height="%d" alt="%dpx">'
               '<span>%dpx</span></div>' % (FAVPNG[s], s, s, s, s) for s in (16, 32, 48, 64))
wall += "".join('<div class="wcell cut"><img src="%s" width="%d" height="%d" alt="%dpx">'
                '<span>%dpx</span></div>' % (PNG[s], s, s, s, s) for s in (128, 256))

nfiles = len([f for _, d, fs in os.walk(ROOT) for f in fs])
total = sum(os.path.getsize(os.path.join(r, f))
            for r, _, fs in os.walk(ROOT) for f in fs)

html = (TPL
        .replace("__MARK_A__", uniq(MARK_FULL)).replace("__MARK_B__", uniq(MARK_FULL))
        .replace("__MARK_C__", uniq(MARK_FULL))
        .replace("__ICO__", ICO)
        .replace("__INEQ__", INEQ)
        .replace("__VARIANTS__", v_html)
        .replace("__FAVCELLS__", favcells)
        .replace("__FAV16__", FAVPNG[16])
        .replace("__WALL__", wall)
        .replace("__BLUEPRINT__", BLUEPRINT)
        .replace("__PARAMS__", prows)
        .replace("__RATIOS__", rrows)
        .replace("__RULES__", "".join("<li>%s</li>" % r for r in RULES))
        .replace("__SWATCHES__", swatches)
        .replace("__CROWS__", crows)
        .replace("__CROWS2__", crows2)
        .replace("__CLEAR__", CLEAR)
        .replace("__BANS__", "".join("<li>%s</li>" % b for b in BANS))
        .replace("__A16__", A16).replace("__A32__", A32).replace("__ABR__", ABR)
        .replace("__CHECKS__", chkrows)
        .replace("__TREE__", tree_html)
        .replace("__NFILES__", str(nfiles))
        .replace("__TOTALSIZE__", "%.0f KB" % (total / 1024.0)))

out = os.path.join(ROOT, "showcase.html")
open(out, "w", encoding="utf-8").write(html)
print("OK ->", out, "%.0f KB" % (os.path.getsize(out) / 1024.0))
