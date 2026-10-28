import type { CSSProperties } from "react";
import { TagList, type TagType } from "./tags";

/**
 * 看板分类色板 —— 分类 → 渐变的单一数据源。
 *
 * 色值取自参考站的 `.gp-<color>` 渐变体系（Tailwind 400/500/700 三档）：
 *   radial-gradient(ellipse 80% 80% at 50% -30%, <light>, transparent)   ← 顶部柔光
 *   linear-gradient(135deg, <mid>, <deep>)                                ← 135° 底色
 * 本站是暗色看板，所以三档只作为【通道串】注入 CSS 变量，由样式层按需压低 alpha，
 * 而不是照搬参考站 0x66/0x38 那种在深底上会糊成一片的强度。
 *
 * ── 为什么存 "R G B" 而不是 #hex ──
 *   CSS 侧要写 rgb(var(--cat-mid) / 0.45) 这类带 alpha 的调用；hex 无法参与 alpha 运算，
 *   只能靠 color-mix()（多一层运行时开销且旧 Safari 不支持）。存通道串，一处定义、任意 alpha。
 *
 * ── 改色 ──
 *   只改这里。卡片渐变、卡片标签 tick、分类筛选 chips 三处渲染层都从这里读，
 *   不要在各自组件里写死颜色（历史上 tags.tsx 的 24 色彩虹圆点就是这样散落失效的）。
 */

export interface CategoryColor {
  /** 色板名，仅用于调试与序列化，不参与渲染 */
  name: string;
  /** 亮档：顶部柔光 / 选中态文字 */
  light: string;
  /** 中档：主色，描边、悬停环、渐变中段 */
  mid: string;
  /** 深档：渐变收尾 */
  deep: string;
}

type Palette = Record<string, { light: string; mid: string; deep: string }>;

/** 参考站同源色板（Tailwind 400 / 500 / 700） */
const PALETTE: Palette = {
  amber: { light: "251 191 36", mid: "245 158 11", deep: "180 83 9" },
  blue: { light: "96 165 250", mid: "59 130 246", deep: "29 78 216" },
  cyan: { light: "34 211 238", mid: "6 182 212", deep: "14 116 144" },
  emerald: { light: "52 211 153", mid: "16 185 129", deep: "4 120 87" },
  fuchsia: { light: "232 121 249", mid: "217 70 239", deep: "162 28 175" },
  gray: { light: "156 163 175", mid: "107 114 128", deep: "55 65 81" },
  green: { light: "74 222 128", mid: "34 197 94", deep: "21 128 61" },
  indigo: { light: "129 140 248", mid: "99 102 241", deep: "67 56 202" },
  lime: { light: "163 230 53", mid: "132 204 22", deep: "77 124 15" },
  orange: { light: "251 146 60", mid: "249 115 22", deep: "194 65 12" },
  pink: { light: "244 114 182", mid: "236 72 153", deep: "190 24 93" },
  purple: { light: "192 132 252", mid: "168 85 247", deep: "126 34 206" },
  red: { light: "248 113 113", mid: "239 68 68", deep: "185 28 28" },
  rose: { light: "251 113 133", mid: "244 63 94", deep: "190 18 60" },
  sky: { light: "56 189 248", mid: "14 165 233", deep: "3 105 161" },
  slate: { light: "148 163 184", mid: "100 116 139", deep: "51 65 85" },
  teal: { light: "45 212 191", mid: "20 184 166", deep: "15 118 110" },
  violet: { light: "167 139 250", mid: "139 92 246", deep: "109 40 217" },
  yellow: { light: "250 204 21", mid: "234 179 8", deep: "161 98 7" },
};

const pick = (name: string, p: { light: string; mid: string; deep: string }): CategoryColor => ({ name, ...p });

/**
 * 分类 → 颜色。
 * 26 个分类对 19 个色板位，尾部 7 个必然复用；复用时按语义就近归并
 * （企业职能沿用教育蓝、SEO 沿用趣味琥珀……），同色即同类，视觉上仍是分组信号。
 */
export const CATEGORY_COLORS: Record<TagType, CategoryColor> = {
  write: pick("indigo", PALETTE.indigo),
  article: pick("violet", PALETTE.violet),
  code: pick("cyan", PALETTE.cyan),
  ai: pick("fuchsia", PALETTE.fuchsia),
  living: pick("emerald", PALETTE.emerald),
  interesting: pick("amber", PALETTE.amber),
  life: pick("lime", PALETTE.lime),
  social: pick("pink", PALETTE.pink),
  philosophy: pick("purple", PALETTE.purple),
  mind: pick("sky", PALETTE.sky),
  pedagogy: pick("blue", PALETTE.blue),
  academic: pick("teal", PALETTE.teal),
  games: pick("orange", PALETTE.orange),
  tool: pick("slate", PALETTE.slate),
  interpreter: pick("green", PALETTE.green),
  language: pick("rose", PALETTE.rose),
  speech: pick("red", PALETTE.red),
  comments: pick("yellow", PALETTE.yellow),
  text: pick("gray", PALETTE.gray),
  company: pick("blue", PALETTE.blue),
  seo: pick("amber", PALETTE.amber),
  doctor: pick("rose", PALETTE.rose),
  finance: pick("emerald", PALETTE.emerald),
  music: pick("purple", PALETTE.purple),
  professional: pick("teal", PALETTE.teal),
  contribute: pick("gray", PALETTE.gray),
};

/** 无分类 / 分类缺失时的中性兜底（slate） */
export const CATEGORY_FALLBACK: CategoryColor = pick("slate", PALETTE.slate);

export function getCategoryColor(tag?: TagType | string): CategoryColor {
  return (tag && CATEGORY_COLORS[tag as TagType]) || CATEGORY_FALLBACK;
}

/**
 * 卡片的「主分类」= 卡内标签排序后的第一个，与 PromptCardTag 的展示顺序一致。
 * 这样卡片主色永远等于用户看到的第一个标签，不会出现"卡片是青色但首个标签是琥珀"的错配。
 */
export function primaryTag(tags?: TagType[] | string[]): TagType | undefined {
  if (!tags || tags.length === 0) return undefined;
  const sorted = [...tags].sort((a, b) => TagList.indexOf(a as TagType) - TagList.indexOf(b as TagType));
  return sorted[0] as TagType;
}

/**
 * 把分类三档色写成 CSS 自定义属性，交给样式层消费。
 * React 的 CSSProperties 不认识 `--*`，故断言一次；不要改成字符串拼接（会丢掉类型检查）。
 */
export function categoryVars(tag?: TagType | string): CSSProperties {
  const color = getCategoryColor(tag);
  return {
    "--cat-light": color.light,
    "--cat-mid": color.mid,
    "--cat-deep": color.deep,
  } as CSSProperties;
}

// ==================== 无分类数据的稳定配色 ====================

/** FNV-1a 32bit：实现简单、分布均匀，且纯同步无依赖 */
function hash32(input: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = Math.imul(h, 0x01000193);
  }
  return h >>> 0;
}

const PALETTE_NAMES = Object.keys(PALETTE);

/**
 * 社区提示词的配色。后端 /userprompts/bulk 不返回 tags（已实测确认），
 * 没有分类可染 —— 这里用 id 做稳定散列从色板取色，让社区看板与首页共用同一套
 * 渐变语言。颜色在这里只承担「区分卡片」，不承担「分类」语义，所以：
 *   - 用 id 而非 title：标题编辑后颜色不跳变，SSG/CSR 两侧也必然一致；
 *   - 散列而非顺序取模：相邻卡片颜色不相邻，看板才有多彩观感。
 * 若后端将来补上 tags，调用方优先走 categoryVars(tags)，此函数自动退位。
 */
export function autoCategoryColor(seed: string | number): CategoryColor {
  const name = PALETTE_NAMES[hash32(String(seed)) % PALETTE_NAMES.length];
  return { name, ...PALETTE[name] };
}

export function autoCategoryVars(seed: string | number): CSSProperties {
  const color = autoCategoryColor(seed);
  return {
    "--cat-light": color.light,
    "--cat-mid": color.mid,
    "--cat-deep": color.deep,
  } as CSSProperties;
}
