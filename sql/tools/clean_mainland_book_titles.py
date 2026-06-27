#!/usr/bin/env python
"""Normalize crawled mainland book names to catalog titles."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path


SQL_DIR = Path(__file__).resolve().parents[1]
BOOK_SOURCE_PATH = SQL_DIR / "source" / "books_mainland.csv"

PLACEHOLDER_VALUES = {"", "作者待详情补采", "出版社待详情补采"}

PROMO_BRACKET_WORDS = [
    "推荐",
    "出品",
    "正版",
    "包邮",
    "售后",
    "退换",
    "发票",
    "赠",
    "扫码",
    "粉丝",
    "采购",
    "团购",
    "优惠",
    "打卡",
    "视频",
    "点击",
    "好评",
    "畅销",
    "人手",
    "暌违",
    "再归来",
    "力作",
    "年度",
    "影响教师",
]

TRAIL_MARKERS = [
    "购买更多",
    "点击进入",
    "线上线下同步销售",
    "请咨询客服",
    "下单前",
    "欢迎选购",
    "正版保障",
    "正版旧书",
    "全新正版",
    "新华书店正版",
    "速开发票",
    "优质售后",
    "支持7天",
    "七天无理由",
    "电子发票",
    "正规发票",
    "团购优惠",
    "企业采购",
    "可开发票",
    "满额减",
    "保证质量",
    "优选包邮",
    "官方正版",
    "读客熊猫君出品",
    "小读客出品",
    "本书采用",
    "本书基于",
    "本书由",
    "本书是",
    "本书收录",
    "本字典",
    "本词典",
    "本套丛书",
    "全网粉丝",
    "豆瓣",
    "被BBC",
    "扫码即可",
    "名校名师",
    "随书附赠",
    "附赠",
    "赠送",
    "适合亲子阅读",
    "看半小时漫画",
    "与历代",
    "斩获",
    "得主",
    "入选",
    "考虑到",
    "接聪明豆",
    "同步教材",
    "一题双模板",
    "一题多解法",
    "常考问法",
    "收录小学",
    "收录常用",
    "传奇营销",
    "全景呈现",
    "深度剖析",
    "文津奖",
    "孩子爱看",
    "专为孩子",
    "中国教育新闻网",
    "全书考点",
    "低幼启蒙",
    "适合21世纪",
    "王缉思作品",
    "不知从何写起",
    "让孩子",
    "帮助孩子",
    "答案有详解",
    "每天15分钟",
    "学科规划",
    "对标",
    "开心教育",
    "随机限量签名版",
    "正版字典",
    "正版图书",
    "正版书籍",
    "小学生阅读书目",
    "专家推荐",
    "家长希望",
    "美国社会学",
    "2018年度",
    "2019年全国",
    "2022年主题",
]

CONTRIBUTOR_SUFFIXES = [
    "著",
    "编著",
    "主编",
    "编",
    "译",
    "绘",
    "等",
    "作品",
    "著作",
    "斩获",
    "推荐",
    "代表作",
    "经典作品",
    "全新",
]

TRAIL_SUFFIXES = [
    "正版书籍",
    "正版图书",
    "正版字典",
    "随机限量签名版",
    "官方正版",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str) -> str:
    text = html.unescape(value or "")
    text = text.replace("\u3000", " ")
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compact_text(value: str) -> str:
    text = normalize_text(value)
    text = re.sub(r"\s+", "", text)
    text = text.replace("：", ":")
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("【", "[").replace("】", "]")
    text = text.replace("＜", "<").replace("＞", ">")
    return text


def remove_promo_brackets(text: str) -> str:
    bracket_pattern = re.compile(r"([\(\[<])([^\(\)\[\]<>]{1,120})([\)\]>])")

    def replacement(match: re.Match[str]) -> str:
        content = match.group(2)
        if len(content) > 48 or any(word in content for word in PROMO_BRACKET_WORDS):
            return ""
        return match.group(0)

    previous = None
    while previous != text:
        previous = text
        text = bracket_pattern.sub(replacement, text)
    return text


def contributor_names(authors: str) -> list[str]:
    names: list[str] = []
    for part in re.split(r"[;；、,/|]+", authors or ""):
        name = compact_text(part)
        name = re.sub(r"(著|编著|主编|编|译|绘|等)$", "", name)
        if len(name) >= 2 and name not in PLACEHOLDER_VALUES:
            names.append(name)
    return sorted(dict.fromkeys(names), key=len, reverse=True)


def cut_at_author(text: str, authors: str, publisher: str) -> str:
    publisher_key = compact_text(publisher)
    if publisher_key in PLACEHOLDER_VALUES:
        publisher_key = ""

    best: int | None = None
    for name in contributor_names(authors):
        start = 0
        while True:
            position = text.find(name, start)
            if position < 0:
                break
            tail = text[position + len(name) : position + len(name) + 16]
            has_suffix = any(tail.startswith(suffix) for suffix in CONTRIBUTOR_SUFFIXES)
            followed_by_publisher = bool(publisher_key and publisher_key in tail)
            if position >= 3 and (has_suffix or followed_by_publisher):
                best = position if best is None else min(best, position)
                break
            start = position + 1
    return text[:best] if best is not None else text


def cut_at_publisher(text: str, publisher: str) -> str:
    publisher_key = compact_text(publisher)
    if publisher_key and publisher_key not in PLACEHOLDER_VALUES:
        position = text.find(publisher_key)
        if position >= 4:
            return text[:position]

    match = re.search(r"[\u4e00-\u9fff]{2,}(出版社|书局|出版集团|出版公司)", text)
    if match and match.start() >= 4:
        return text[: match.start()]
    return text


def cut_at_markers(text: str) -> str:
    best: int | None = None
    for marker in TRAIL_MARKERS:
        marker_key = compact_text(marker)
        position = text.find(marker_key)
        if position >= 6:
            best = position if best is None else min(best, position)

    isbn_match = re.search(r"(ISBN)?97[89]\d{10}", text, flags=re.IGNORECASE)
    if isbn_match and isbn_match.start() >= 4:
        best = isbn_match.start() if best is None else min(best, isbn_match.start())

    sentence_match = re.search(r"[。!！]", text)
    if sentence_match and sentence_match.start() >= 8:
        best = sentence_match.start() if best is None else min(best, sentence_match.start())

    return text[:best] if best is not None else text


def balance_brackets(text: str) -> str:
    for opener, closer in [("(", ")"), ("[", "]"), ("<", ">")]:
        if text.count(opener) > text.count(closer):
            text = text[: text.rfind(opener)]
    return text


def final_cleanup(text: str) -> str:
    text = balance_brackets(text)
    text = re.sub(r"[\[\]<>]", "", text)
    text = re.sub(r"^[,，、:：;；/|+-]+", "", text)
    text = re.sub(r"[,，、:：;；/|+\\-。.!！“”\"'《（(]+$", "", text)
    text = re.sub(r"\(\)", "", text)
    text = re.sub(r"^\((.*)\)$", r"\1", text)
    for suffix in TRAIL_SUFFIXES:
        if text.endswith(suffix) and len(text) > len(suffix) + 4:
            text = text[: -len(suffix)]
    return text.strip()


def trim_trailing_contributor(text: str, authors: str) -> str:
    for name in contributor_names(authors):
        if text.endswith(name) and len(text) > len(name) + 4:
            return text[: -len(name)]
    return text


def pure_title(row: dict[str, str]) -> str:
    original = compact_text(row["title"])
    text = remove_promo_brackets(original)
    text = cut_at_author(text, row.get("authors", ""), row.get("publisher", ""))
    text = cut_at_publisher(text, row.get("publisher", ""))
    text = cut_at_markers(text)
    text = trim_trailing_contributor(text, row.get("authors", ""))
    text = final_cleanup(text)
    if len(text) < 2:
        text = final_cleanup(remove_promo_brackets(original))
    return text[:120]


def clean_source_titles() -> None:
    fields, rows = read_csv(BOOK_SOURCE_PATH)
    changed = 0
    examples: list[tuple[str, str]] = []
    for row in rows:
        cleaned = pure_title(row)
        if cleaned and cleaned != row["title"]:
            if len(examples) < 12:
                examples.append((row["title"], cleaned))
            row["title"] = cleaned
            changed += 1

    write_csv(BOOK_SOURCE_PATH, fields, rows)
    print(f"{BOOK_SOURCE_PATH}: cleaned {changed} of {len(rows)} book titles")
    for before, after in examples:
        print(f"- {before} -> {after}")


if __name__ == "__main__":
    clean_source_titles()
