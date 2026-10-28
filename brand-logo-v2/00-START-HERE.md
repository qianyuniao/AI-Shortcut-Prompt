# AI Shortcut Prompt 标志 v2 · 从这里开始

方向：**二分圆盘 · The Direct Line**　　取代 v1「切角卡片 · The Shortcut」

> 一个圆盘被竖直直径一分为二——左半实心，是已经攒下的 5000+ 条提示词；右半留白，一条圆头直线直连两端。
> 原 logo 右半是 6-8 个节点的直角绕行走线，现在只剩一条直连段。**被删掉的那部分绕路，就是捷径。**

## 为什么长这样（推导链）

| 关键词 | 原 logo 观察到的事实 | 几何决策 |
|---|---|---|
| 复用 Reuse | 左半为实心填充面（F1 闭合轮廓被纵轴二分，左实右线） | 实心半圆块，主标记族 P1 |
| 捷径 Shortcut | 右半电路为直角折线 + 等径端点节点（F6） | 折线删至一条直连段，端点即圆头，辅族 P5+S1 |
| 即取即用 Instant | 整体近圆、外圈深色描边、纵向中缝（F2/F3） | 深色外环 + 中缝留白 |

被丢弃的事实：F6 的节点数量（6-8 个在 24px 下必粘连）、F7 的明暗渐变（违反平板约束）。

## 该用哪个文件

| 场景 | 用这个文件 |
|---|---|
| 网站页眉 / README 头图 | `svg/aishort-logo-horizontal-fullcolor.svg` 或 `assets/aishort-logo-horizontal-2048px.png` |
| 深色模式页眉 | `svg/aishort-logo-horizontal-reverse.svg` 或 `assets/aishort-logo-horizontal-dark-2048px.png` |
| 头像 / App 图标 / 社交头像 | `svg/aishort-mark-only-fullcolor.svg` 或 `assets/aishort-logo-stacked-1024px.png` |
| 单色印刷 / 雕刻 / 印章 | `svg/aishort-logo-horizontal-mono.svg` 或 `assets/aishort-logo-horizontal-mono-2048px.png` |
| 浏览器 / PWA 图标 | `assets/favicon.ico` + `assets/favicon-16.png` |
| 位图（PPT 等不支持 SVG 的平台） | `assets/aishort-mark-(32,64,128,256,512,1024)px.png` |
| **要透明底 PNG（无白板）** | **`png-transparent/`**（推荐：`aishort-mark-transparent-1024px.png`） |
| 品牌规范页（中文，含设计理念） | **`brand-sheet.html`**（图片已内嵌 base64，单文件可分享） |
| 想改规范页内容 | **`brand-sheet.src.html`** → 改完跑 `publish.py` 重新发布 |
| 使用规范 / 色值 / 禁用项 | `dist/spec.md` |
| 改标志（调参数） | `mark.json` → 重跑 `mark_spec.py` → `build_assets.py` |

## 关键数字

| 项 | 值 |
|---|---|
| 主色 / 结构色 | `#3EB489` 青绿（沿用线上配色，改 logo 不动全站） / `#43474A` 深灰 |
| 图元数 | 完整版 **3**（环·实心半圆·圆头直连）｜16px 简化版 **2** |
| 几何 | 环 r=36 stroke=12｜实心半圆 r=20｜中缝间隙 10 单位｜直连段 x58→72 厚 11 |
| footprint | 72% W × 72% H |
| 净空区 | 11 单位（标志宽的 11%） |
| 最小尺寸 | 完整版 **32px** ｜简化版 **16px**（favicon / 扩展工具栏） |
| 单色判定 | **PASS** —— 层级靠中缝留白，不靠色相 |

## 16px 为什么单独一版

完整版在 16px 下右半区只有约 6px 宽，直连段必糊。且单色模式下圆环与实心半圆同色，**间隙低于 1px 就会塌成一个实心饼**（F4 单色崩塌）。
因此：32px 及以上用完整版，16/24px 用 `mark-simplified.json` 产出的简化版——保留「二分圆盘」这一最强识别点，去掉直连段，并把中缝拉到 10 单位（16px 下 ≈1.6px）。

## 目录

```
brand-logo-v2/
├── 00-START-HERE.md
├── brand-sheet.html                  品牌规范页（中文 · 设计理念 · 图片已内嵌，可直接分享）
├── brand-sheet.src.html              规范页唯一源码（改这个，再跑 publish.py）
├── publish.py                        发布：src → brand-sheet.html + dist/spec.html（都内嵌图片）
├── inline_images.py / uninline.py    旧的内嵌方式（保留，日常改用 publish.py）
├── png-transparent/                  **透明底 PNG 包**（留白版 / 紧裁版 / 单色 / 白色 / 简化 + 验证图）
├── build_transparent.py              透明底 PNG 构建脚本
├── editorial-aishort-1024x1536.png   编辑作品（上：原 logo ｜ 下：抽象面板 + 署名）
├── mark.json / mark-simplified.json  图元源（改这里，不要手改 SVG）
├── build_assets.py                   favicon 与位图构建脚本
├── build_lockup.py                   横版/竖版组合构建（项目全名 AI Shortcut Prompt）
├── svg/                              6 个规范 SVG（横版 3 版 + 纯图形 3 版）
├── assets/                           favicon.ico · 16/20/24 · 32~1024px PNG · 平台图标 · 验证图
├── dist/                             完整版规范包（spec.html / spec.md / scale-test / 六场景）
└── dist-simplified/                  16-24px 简化版规范包
```

## 重新生成

```bash
python <expert>/skills/mark-to-spec/scripts/mark_spec.py --config mark.json --outdir ./dist --check-mono
python build_assets.py      # favicon 与纯图形位图
python build_lockup.py      # 横版 / 竖版组合（SVG + PNG）
python build_transparent.py # 透明底 PNG 包 → png-transparent/
python publish.py           # 规范页：src → 内嵌图片的 brand-sheet.html 与 dist/spec.html
```

## 关于「白色」

标志 PNG **本身一直是透明的**（alpha=0），白底来自两处：看图软件填充透明区、以及规范页旧的
`figure img{background:#fff}`。已修：规范页改用透明 + 棋盘格标识，并单独产出
`png-transparent/` 一包（留白版保留 8% 净空，紧裁版贴齐图形边缘）。

> 注意：`dist/spec.html` 已被手工改写为中文品牌规范页，重跑 `mark_spec.py` 会覆盖它。
> 保留版本见根目录 `brand-sheet.html`。
