# AiShort 标志交付包 · 从这里开始

方向：**切角卡片 · The Shortcut**　v1.0　比例系统：整数比 + 8pt 网格

> 一张提示词卡片，右上角沿 45° 抄近道切掉一块；被切下的三角沿切边镜像翻折进卡内，成为点亮的琥珀折片。
> 斜边 452.5 &lt; 直角路径 640——捷径是三角形不等式，不是比喻。

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
| 位图（PPT / 不支持 SVG 的平台） | `01-web-rgb/png/aishort-mark-only-fullcolor-rgb-(256, 512, 1024, 2048)px.png`（另含单黑/反白/灰阶 512px） |
| 使用规范 / 色值 / 禁用项 | `05-spec/spec.md` |
| 改标志（调参数） | `06-source/build.py` 顶部常量 → 重跑，整包联动 |

## 关键数字

| 项 | 值 |
|---|---|
| 主色 / 点缀 | `#0B6E62` 墨松绿 / `#F2A33C` 琥珀（8.56%） |
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
