import React, { ReactNode, useMemo } from "react";
import { Card, Flex } from "antd";
import { LinkOutlined } from "@ant-design/icons";
import { translate } from "@docusaurus/Translate";
import clsx from "clsx";
import styles from "./styles.module.css";
import { categoryVars, primaryTag, autoCategoryVars } from "@site/src/data/categoryColors";
import type { TagType } from "@site/src/data/tags";

/**
 * antd 多行省略靠 `display:-webkit-box` + `-webkit-line-clamp`，而 flex 子项的 display
 * 会被 blockify（Chrome 算成 flow-root）——clamp 失效，只剩 overflow:hidden 把最后一行
 * 拦腰切断。所以放进 flex 容器的 Typography 都垫这层普通块盒：flex 属性由盒子承担。
 */
export const ClampBox: React.FC<{ children: ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <div style={{ flex: 1, minWidth: 0, minHeight: 0, ...style }}>{children}</div>
);

/**
 * 卡片角落的原文链接。DataCard / CommunityCard / FavoriteCard / UserCard 曾各写一份
 * 逐字相同的裸 `<a><LinkOutlined/></a>`，四份一起带着两个缺陷：
 *
 *   1. 命中区只有 12×22 —— 图标 12px、外层 `<a>` 无内边距。WCAG 2.2 AA(2.5.8) 要求
 *      24×24，手机上实测很容易点空。这里把 `<a>` 撑成 24×24 的 inline-flex 盒子，
 *      图标视觉尺寸不变，纯粹加大命中区。
 *   2. 没有可访问名称 —— 图标链接无文本、无 aria-label，读屏只念「链接」。复用已在
 *      17 个 locale 里译好的 `prompt.source`，不必为此新增 id（新增就得同步改 17 份
 *      code.json，漏一份那门语言就回落中文）。
 *
 * marginLeft 从 8 收到 4：新盒子自带 6px 内边距，视觉间距与改动前保持一致。
 */
export const PromptSourceLink: React.FC<{ href?: string }> = ({ href }) =>
  href ? (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={translate({ id: "prompt.source", message: "来源" })}
      style={{ marginInlineStart: 4, display: "inline-flex", alignItems: "center", justifyContent: "center", minWidth: 24, minHeight: 24 }}>
      <LinkOutlined style={{ fontSize: 12, color: "var(--site-color-text-tertiary)" }} />
    </a>
  ) : null;

interface BasePromptCardProps {
  title?: ReactNode;
  titleExtra?: ReactNode;
  actions?: ReactNode[];
  children?: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  loading?: boolean;
  id?: string;
  onCardClick?: () => void;
  /**
   * 卡片的分类标签。传入后卡片按「主分类」（= 卡内首个标签）染上对应渐变：
   * 底色 135° 渐变 + 顶部柔光 + 悬停描边环，配色见 src/data/categoryColors.ts。
   * 不传则回落到中性 slate，视觉上与改动前一致。
   */
  tags?: TagType[];
  /**
   * 无分类数据（社区提示词后端不返回 tags）时的稳定配色种子。
   * 优先级：tags > autoColorSeed > slate 兜底。用 id 作种子，同一张卡颜色恒定。
   */
  autoColorSeed?: string | number;
}

export const BasePromptCard = React.forwardRef<HTMLDivElement, BasePromptCardProps>(
  ({ title, titleExtra, actions, children, className, style, loading, id, onCardClick, tags, autoColorSeed, ...rest }, ref) => {
    // 分类三档色写成 CSS 变量挂在卡片根元素上，渐变/描边/柔光都在 CSS 里读它 —— 一处注入，
    // 样式层不用为 26 个分类各写一条规则，也不必把颜色塞进 className 字符串。
    // 优先级：真实分类 > 无分类数据的稳定配色 > CSS 类里的 slate 兜底。
    const categoryStyle = useMemo(() => {
      const primary = primaryTag(tags);
      if (primary) return categoryVars(primary);
      if (autoColorSeed !== undefined) return autoCategoryVars(autoColorSeed);
      return {};
    }, [tags, autoColorSeed]);

    // 整卡可点开详情弹窗，但 antd Card 渲染的是裸 <div>：不给 role/tabIndex/键盘处理，
    // 键盘与读屏用户就完全够不到这个入口（styles 里的 :focus-visible 规则也永远不触发）。
    // 卡内还有标题链接与操作按钮，所以只在事件源就是卡片本身时响应，避免 Enter 双触发。
    const handleCardKeyDown = onCardClick
      ? (e: React.KeyboardEvent<HTMLDivElement>) => {
          if (e.target !== e.currentTarget) return;
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onCardClick();
          }
        }
      : undefined;

    return (
      <Card
        ref={ref}
        id={id}
        hoverable
        loading={loading}
        className={clsx(styles.showcaseCard, className)}
        role={onCardClick ? "button" : undefined}
        tabIndex={onCardClick ? 0 : undefined}
        onKeyDown={handleCardKeyDown}
        style={{
          height: "100%",
          display: "flex",
          flexDirection: "column",
          // 别在这里写 borderColor：内联样式的优先级高于 .showcaseCard:hover，
          // 写了 hover 的分类色描边就永远不生效。默认值由 CSS 类的 border 提供。
          cursor: onCardClick ? "pointer" : undefined,
          ...categoryStyle,
          ...style,
        }}
        styles={{
          body: {
            flex: 1,
            display: "flex",
            flexDirection: "column",
            padding: 16,
            gap: 8,
          },
          actions: {
            borderTop: "1px solid var(--site-color-hairline)",
            backgroundColor: "transparent",
            padding: "8px 12px",
          },
        }}
        actions={actions}
        onClick={onCardClick}
        {...rest}>
        {(title || titleExtra) && (
          <Flex justify="space-between" align="start" style={{ marginBottom: 12, minHeight: 32 }}>
            <div style={{ flex: 1, overflow: "hidden", marginInlineEnd: 8 }}>{title}</div>
            {/* flexShrink:0：角标是定宽信息，标题再长也不该压扁它 */}
            {titleExtra && <Flex align="center" gap={8} style={{ flexShrink: 0 }}>{titleExtra}</Flex>}
          </Flex>
        )}
        {children}
      </Card>
    );
  }
);

BasePromptCard.displayName = "BasePromptCard";
