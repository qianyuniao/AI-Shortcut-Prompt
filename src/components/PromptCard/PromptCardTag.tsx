import React, { useCallback, useMemo } from "react";
import { Tooltip, Space, Tag as AntTag } from "antd";
import { useHistory, useLocation } from "@docusaurus/router";
import { Tags, TagList, type TagType } from "@site/src/data/tags";
import { categoryVars } from "@site/src/data/categoryColors";
import { toggleListItem } from "@site/src/utils/jsUtils";
import { prepareUserState } from "@site/src/components/SearchBar/index";
import styles from "./styles.module.css";

interface PromptCardTagProps {
  tags: TagType[];
  muted?: boolean;
  /** When true (default), clicking a tag filters the homepage and blocks card modal.
   *  When false, tags are display-only and clicks pass through to the card. */
  clickable?: boolean;
}

const TagQueryStringKey = "tags";

function readSearchTags(search: string): TagType[] {
  return new URLSearchParams(search).getAll(TagQueryStringKey) as TagType[];
}

function replaceSearchTags(search: string, newTags: TagType[]) {
  const searchParams = new URLSearchParams(search);
  searchParams.delete(TagQueryStringKey);
  newTags.forEach((tag) => searchParams.append(TagQueryStringKey, tag));
  return searchParams.toString();
}

function sortTags(tags: TagType[]) {
  return (tags || [])
    .map((tag) => ({ tag, ...Tags[tag] }))
    .sort((a, b) => TagList.indexOf(a.tag) - TagList.indexOf(b.tag));
}

/** Renders tag list with click-to-filter behavior */
const ClickableTagList = ({ tags, muted }: { tags: TagType[]; muted: boolean }) => {
  const location = useLocation();
  const history = useHistory();
  const tagObjectsSorted = useMemo(() => sortTags(tags), [tags]);

  const handleTagClick = useCallback(
    (e: React.MouseEvent, tag: TagType) => {
      e.stopPropagation();
      const currentTags = readSearchTags(location.search);
      const newTags = toggleListItem(currentTags, tag);
      const newSearch = replaceSearchTags(location.search, newTags);
      history.push({
        ...location,
        search: newSearch,
        state: prepareUserState(),
      });
    },
    [location, history],
  );

  return <TagLayout tags={tagObjectsSorted} muted={muted} onClick={(e, tag) => handleTagClick(e, tag)} cursor="pointer" />;
};

/** Renders static tag list (clicks pass through to parent) */
const StaticTagList = ({ tags, muted }: { tags: TagType[]; muted: boolean }) => {
  const tagObjectsSorted = useMemo(() => sortTags(tags), [tags]);
  return <TagLayout tags={tagObjectsSorted} muted={muted} cursor="default" />;
};

/** Shared layout for rendering tag badges */
const TagLayout = ({
  tags,
  muted,
  onClick,
  cursor,
}: {
  tags: Array<{ tag: TagType; label: string; description: string }>;
  muted: boolean;
  onClick?: (e: React.MouseEvent, tag: TagType) => void;
  cursor: string;
}) => (
  // muted 一律不压文字的透明度：原来 Space 0.6 × Tag 0.75 = 0.45，11px 标签在浅色底上
  // 实测 2.05:1（AA 小字要 4.5:1），压成单层 0.75 也只有 3.75:1，仍不合格。
  // 层级改由左侧 tick 承担（见下），文字保持全强度 —— 该弱化的是装饰，不是标签本身。
  <Space size={[6, 6]} wrap>
    {tags.map((tagObject, index) => (
      <Tooltip key={index} title={tagObject.description} id={`showcase_card_tag_${tagObject.tag}`}>
        <AntTag
          onClick={onClick ? (e) => onClick(e, tagObject.tag) : undefined}
          className={styles.categoryTag}
          style={{
            marginRight: 0,
            color: "var(--ifm-color-content-secondary)",
            backgroundColor: "transparent",
            // border 交给 .categoryTag：内联 border 会盖掉 CSS 里的 hover 变色（内联优先级更高），
            // 那样标签就永远点不亮。
            borderRadius: 0,
            paddingInlineStart: 10,
            paddingInlineEnd: 8,
            fontSize: 11,
            letterSpacing: "0.02em",
            position: "relative",
            cursor,
            ...categoryVars(tagObject.tag),
          }}>
          {/* 左侧 tick = 该分类的渐变色条。色彩只落在这 2px 装饰上，标签文字保持全强度
              （压文字透明度会让 11px 掉到 3.3:1，过不了 AA 小字 4.5:1）。
              muted 与否的层级差别改为调低 alpha，而不是退回中性灰 —— 分类色本身就是信息。 */}
          <span
            aria-hidden
            style={{
              position: "absolute",
              insetInlineStart: 0,
              top: 0,
              bottom: 0,
              width: 2,
              backgroundImage: "linear-gradient(180deg, rgb(var(--cat-mid) / 0.95), rgb(var(--cat-deep) / 0.85))",
              opacity: muted ? 0.45 : 1,
            }}
          />
          {tagObject.label}
        </AntTag>
      </Tooltip>
    ))}
  </Space>
);

export const PromptCardTag = ({ tags, muted = false, clickable = true }: PromptCardTagProps) => {
  return clickable ? <ClickableTagList tags={tags} muted={muted} /> : <StaticTagList tags={tags} muted={muted} />;
};
