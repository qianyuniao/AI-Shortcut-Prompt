# AiShort 标志交付包 v2.0 · 从这里开始

方向：**一格之距 · One of Many**　比例系统：整数比 + 8pt 网格

> 一张 2×2 的提示词卡片阵列，只有右下那一格是实的。
> 5000+ 条提示词里，你要的永远只有一条——标志只画这一条。

本包**未改动项目任何现有文件**（`static/img/logo.svg` 等保持原样），确认后再决定是否替换。

---

## 我要用哪个文件？

| 场景 | 用这个文件 |
|---|---|
| **先看效果** | **`preview.html`**（Hero / 推导链 / 变体矩阵 / 缩放墙 / 六场景 / 色彩表） |
| 网站页眉 / README 头图 | `01-web-rgb/svg/aishort-logo-primary-fullcolor-rgb.svg` |
| 深色模式页眉 | `01-web-rgb/svg/aishort-logo-primary-darkmode-rgb.svg` |
| 头像 / 社交 / App 图标 | `03-social-favicon/android-chrome-512.png`（实底，别用透明版） |
| 浏览器 / PWA 图标 | `03-social-favicon/favicon.ico` + `favicon.svg` |
| 单色印刷 / 雕刻 / 印章 | `01-web-rgb/svg/aishort-logo-primary-mono-black-rgb.svg` |
| 位图（PPT 等不支持 SVG 的平台） | `01-web-rgb/png/aishort-mark-only-fullcolor-rgb-1024px.png` |
| 使用规范 / 色值 / 禁用项 | `05-spec/spec.md` |
| 改标志（调参数） | `06-source/build.py` 顶部常量 → 重跑，整包联动 |

---

## 关键数字

| 项 | 值 |
|---|---|
| 主色（点亮格） | `#10997F` 青绿 · 对白底 **3.57:1**（过 WCAG 非文本 3:1） |
| 结构色（字标） | `#0B6E62` 墨松绿 · 对白底 **6.14:1**（过文字 4.5:1） |
| 浅阶（未点亮格） | `#A9DFD5` |
| 几何 | B=320 · G=160 · R=80 · M=112（画布 1024，U=8） |
| 比例校验 | 6 项全部 **0.000%** 误差（B:R=4:1 · B:G=2:1 · G:R=2:1） |
| 负空间 | **60.9%** |
| 最小尺寸 | 实底图标 16px｜纯图形 24px｜横版组合 32px 高 |
| 净空区 | X = G = 160（画布的 15.6%） |

---

## 与 v1.0「切角卡片」的差异

| 维度 | v1.0 | v2.0 |
|---|---|---|
| 语义锚点 | 抄近道（45° 切角 = 三角形不等式） | 一格之距（5000+ 里那一条） |
| 识别点 | 被切走的角 + 琥珀折片 | 哪一格是实的（颜色 + 明度双重编码） |
| 主色 | 墨松绿 + 琥珀点缀 | 墨松绿 / 青绿双色阶（无第二色相） |
| 图元 | 卡片 + 折片（2 主体） | 4 个等大方块（1 主族） |
| 小尺寸 | 折片在 16px 下 5.6px | 十字负空间 16px 下 2.5px 未闭合 |

---

## 目录

```
brand-logo-package-v2/
├── 00-START-HERE.md
├── preview.html
├── 01-web-rgb/{svg,png}
├── 03-social-favicon/
├── 05-spec/{spec.md, safe-zone.svg, blueprint.svg, scale-test.png}
└── 06-source/{build.py, geometry.json, mark.json, build.log.txt, markspec-kit/}
```

## 重跑

```bash
cd 06-source && python build.py
```

依赖仅 Python 标准库（无 Pillow / cairosvg，PNG 由自带 SDF 抗锯齿光栅器生成）。
