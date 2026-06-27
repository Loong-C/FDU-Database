#!/usr/bin/env python
"""Fetch mainland bookstore categories and product cards for seed data."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import time
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_from_bytes
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup


SQL_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = SQL_DIR / "source"

XHSD_HOME_URL = "https://www.xhsd.com/"
DANGDANG_CATEGORY_JS_URL = "http://static.dangdang.com/js/header2012/categorydata_new.js?20251111"
DANGDANG_SEARCH_URL = "http://search.dangdang.com/"

BOOK_SOURCE_PATH = SOURCE_DIR / "books_mainland.csv"
NONBOOK_SOURCE_PATH = SOURCE_DIR / "nonbook_mainland.csv"
PROJECT_CATEGORY_PATH = SOURCE_DIR / "categories_mainland.csv"
XHSD_CATEGORY_PATH = SOURCE_DIR / "categories_xhsd.csv"
DANGDANG_CATEGORY_PATH = SOURCE_DIR / "categories_dangdang.csv"

BOOK_PARENT_WEIGHTS = {
    "文学艺术": Decimal("0.20"),
    "人文社科": Decimal("0.13"),
    "少儿童书": Decimal("0.16"),
    "教育考试": Decimal("0.18"),
    "经济金融": Decimal("0.09"),
    "生活休闲": Decimal("0.10"),
    "科学技术": Decimal("0.14"),
}
NONBOOK_PARENT_WEIGHTS = {
    "学习用品": Decimal("0.55"),
    "家居/生活用品": Decimal("0.20"),
    "3C数码": Decimal("0.20"),
    "礼品卡": Decimal("0.05"),
}
SKIP_NONBOOK_TERMS = {"相机/摄影机"}
CSV_CATEGORY_FIELDS = [
    "category_id",
    "category_name",
    "parent_category_id",
    "source_site",
    "source_category_id",
    "source_category_name",
    "source_category_path",
    "is_book",
    "is_leaf",
]
CSV_BOOK_FIELDS = [
    "source_site",
    "source_item_id",
    "source_query_category",
    "source_category_path",
    "title",
    "isbn",
    "authors",
    "publisher",
    "publish_year",
    "publish_date_raw",
    "page_count",
    "language",
    "category_name",
    "unit",
    "suggested_unit_price",
    "status",
    "source_url",
]
CSV_NONBOOK_FIELDS = [
    "source_site",
    "source_item_id",
    "source_query_category",
    "source_category_path",
    "product_name",
    "barcode",
    "category_name",
    "unit",
    "suggested_unit_price",
    "status",
    "source_url",
]


@dataclass(frozen=True)
class SourceCategory:
    source_id: str
    parent_source_id: str
    name: str
    level: int
    path: str
    source_url: str
    top_name: str
    is_book: bool
    is_leaf: bool


@dataclass(frozen=True)
class ProjectLeaf:
    category_name: str
    source_category_name: str
    source_category_id: str
    source_category_path: str
    top_name: str
    is_book: bool


def clean_text(value: object, max_length: int | None = None) -> str:
    text = html.unescape("" if value is None else str(value))
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if max_length is not None:
        text = text[:max_length].strip()
    return text


def money(value: str | Decimal) -> str:
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def fetch_text(url: str, encoding: str, retries: int, timeout: float, sleep_seconds: float) -> str:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                },
            )
            with urlopen(request, timeout=timeout) as response:
                return response.read().decode(encoding, errors="ignore")
        except (HTTPError, URLError, TimeoutError, IncompleteRead) as exc:
            last_error = exc
            time.sleep(max(sleep_seconds * attempt, 0.5))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def href_category_id(anchor) -> str:
    href = anchor.get("href", "")
    match = re.search(r"frontCategoryId(?:=|&#x3D;)(\d+)", href)
    return match.group(1) if match else ""


def absolute_url(href: str) -> str:
    if not href:
        return ""
    if href.startswith("//"):
        return f"https:{href}"
    if href.startswith("/"):
        return f"https://www.xhsd.com{href}"
    return href


def parse_xhsd_categories(html_text: str) -> list[SourceCategory]:
    soup = BeautifulSoup(html_text, "html.parser")
    categories: list[SourceCategory] = []
    for item in soup.select("li.category-item"):
        parent = item.select_one(".parent-category")
        parent_anchor = item.select_one(".parent-category a.child-category")
        if parent is None or parent_anchor is None:
            continue
        top_name = clean_text(parent.get("title") or parent_anchor.get_text())
        top_id = item.get("data-id", "")
        is_book = top_name in BOOK_PARENT_WEIGHTS
        top_url = absolute_url(parent_anchor.get("href", ""))
        categories.append(
            SourceCategory(top_id, "", top_name, 1, top_name, top_url, top_name, is_book, False)
        )
        for second in item.select(".second-category"):
            second_anchor = second.select_one(".second-name")
            if second_anchor is None:
                continue
            second_name = clean_text(second_anchor.get_text())
            second_id = href_category_id(second_anchor)
            second_path = f"{top_name}>{second_name}"
            child_anchors = second.select("a.child-name")
            categories.append(
                SourceCategory(
                    second_id,
                    top_id,
                    second_name,
                    2,
                    second_path,
                    absolute_url(second_anchor.get("href", "")),
                    top_name,
                    is_book,
                    not child_anchors,
                )
            )
            for child in child_anchors:
                child_name = clean_text(child.get_text())
                child_id = href_category_id(child)
                categories.append(
                    SourceCategory(
                        child_id,
                        second_id,
                        child_name,
                        3,
                        f"{second_path}>{child_name}",
                        absolute_url(child.get("href", "")),
                        top_name,
                        is_book,
                        True,
                    )
                )
    return categories


def parse_dangdang_categories(js_text: str) -> list[dict[str, str]]:
    prefix = "var json_category="
    start = js_text.find(prefix)
    end = js_text.find("\r\nmenudataloaded", start)
    if start < 0 or end < 0:
        raise RuntimeError("Could not locate Dangdang category JSON.")
    data = json.loads(js_text[start + len(prefix) : end].strip())
    parent_by_id: dict[str, str] = {}
    for source_id, row in data.items():
        for child_id in row.get("f", []) + row.get("g", []) + row.get("b", []):
            parent_by_id[str(child_id)] = source_id

    def path_for(source_id: str) -> str:
        names = []
        current = source_id
        seen = set()
        while current and current not in seen and current in data:
            seen.add(current)
            names.append(data[current]["n"])
            current = parent_by_id.get(current, "")
        return ">".join(reversed(names))

    rows = []
    for source_id, row in data.items():
        parent_id = parent_by_id.get(source_id, "")
        rows.append(
            {
                "source_site": "当当网",
                "source_category_id": source_id,
                "parent_source_category_id": parent_id,
                "category_name": row["n"],
                "source_category_path": path_for(source_id),
                "source_url": source_url_from_dangdang(row.get("u", "")),
            }
        )
    return rows


def source_url_from_dangdang(value: str) -> str:
    if not value:
        return ""
    value = value.replace("#dd#", ".dangdang.com/")
    if value.startswith("book."):
        return f"https://{value}"
    if value.startswith("category."):
        return f"https://{value}"
    if value.startswith("search."):
        return f"https://{value}"
    return value


def unique_category_name(name: str, parent_name: str, used: set[str]) -> str:
    candidate = name
    if candidate in used:
        candidate = f"{name}（{parent_name}）"
    suffix = 2
    while candidate in used:
        candidate = f"{name}（{parent_name}{suffix}）"
        suffix += 1
    used.add(candidate)
    return candidate


def build_project_categories(source_categories: list[SourceCategory]) -> tuple[list[dict[str, object]], list[ProjectLeaf]]:
    category_rows: list[dict[str, object]] = []
    leaves: list[ProjectLeaf] = []
    used_names: set[str] = set()
    by_source_id = {row.source_id: row for row in source_categories if row.source_id}
    id_by_source: dict[str, int] = {}
    next_id = 1

    def add_category(source: SourceCategory | None, name: str, parent_id: int | str, is_book: bool, is_leaf: bool) -> int:
        nonlocal next_id
        category_id = next_id
        next_id += 1
        source_id = source.source_id if source else ""
        if source_id:
            id_by_source[source_id] = category_id
        category_rows.append(
            {
                "category_id": category_id,
                "category_name": name,
                "parent_category_id": parent_id,
                "source_site": "新华书店网" if source else "",
                "source_category_id": source_id,
                "source_category_name": source.name if source else name,
                "source_category_path": source.path if source else name,
                "is_book": 1 if is_book else 0,
                "is_leaf": 1 if is_leaf else 0,
            }
        )
        return category_id

    used_names.update({"图书", "通用商品"})
    book_root_id = add_category(None, "图书", "", True, False)
    nonbook_root_id = add_category(None, "通用商品", "", False, False)

    selected_top_names = set(BOOK_PARENT_WEIGHTS) | set(NONBOOK_PARENT_WEIGHTS)
    for source in source_categories:
        if source.top_name not in selected_top_names:
            continue
        if source.level == 1:
            parent_id = book_root_id if source.is_book else nonbook_root_id
        else:
            parent_source = by_source_id.get(source.parent_source_id)
            parent_id = id_by_source.get(source.parent_source_id)
            if parent_id is None or parent_source is None:
                continue
        category_name = unique_category_name(source.name, parent_source.name if source.level > 1 else "", used_names)
        category_id = add_category(source, category_name, parent_id, source.is_book, source.is_leaf)
        if source.is_leaf and source.name not in SKIP_NONBOOK_TERMS:
            leaves.append(
                ProjectLeaf(
                    category_name=category_name,
                    source_category_name=source.name,
                    source_category_id=source.source_id,
                    source_category_path=source.path,
                    top_name=source.top_name,
                    is_book=source.is_book,
                )
            )
    return category_rows, leaves


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{path}: {len(rows)} rows")


def parse_price(text: str) -> str:
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return money(match.group(1) if match else "39.00")


def deterministic_status(identifier: str) -> str:
    value = sum(ord(char) for char in identifier)
    if value % 37 == 0:
        return "discontinued"
    if value % 13 == 0:
        return "offsale"
    return "onsale"


def deterministic_pages(identifier: str, category_name: str) -> str:
    base = 96 + sum(ord(char) for char in identifier + category_name) % 640
    return str(base)


def unit_for_nonbook(category_name: str) -> str:
    if any(word in category_name for word in ["笔", "尺", "口琴"]):
        return "支"
    if any(word in category_name for word in ["本", "纸", "卡", "证书"]):
        return "本"
    if any(word in category_name for word in ["纸巾", "湿巾", "垃圾袋"]):
        return "包"
    return "个"


def normalize_author_name(value: str) -> str:
    value = clean_text(value, 100)
    value = re.sub(r"(著|编著|主编|编|译|绘|出品|等)$", "", value).strip(" ,，;；/")
    return value


def parse_dangdang_products(html_text: str, leaf: ProjectLeaf, is_book: bool) -> list[dict[str, str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    items = soup.select("ul.bigimg li") or soup.select("li[ddt-pit]")
    rows: list[dict[str, str]] = []
    for item in items:
        item_id = (item.get("id") or "").lstrip("p")
        title_anchor = item.select_one('a[name="itemlist-title"]') or item.select_one("p.name a")
        if not item_id and title_anchor:
            match = re.search(r"/(\d+)\.html", title_anchor.get("href", ""))
            item_id = match.group(1) if match else ""
        if not item_id or title_anchor is None:
            continue
        title = clean_text(title_anchor.get("title", "") or title_anchor.get_text(" ", strip=True), 200)
        price = parse_price((item.select_one(".search_now_price") or item.select_one(".price")).get_text(" ", strip=True) if item.select_one(".search_now_price") or item.select_one(".price") else "")
        source_url = f"https://product.dangdang.com/{item_id}.html"

        if is_book:
            authors: list[str] = []
            publisher = "出版社待详情补采"
            publish_date = ""
            author_block = item.select_one("p.search_book_author")
            if author_block is not None:
                spans = author_block.find_all("span", recursive=False)
                if spans:
                    links = spans[0].find_all("a")
                    authors = [
                        name
                        for name in (normalize_author_name(link.get_text()) for link in links)
                        if name and name not in {"当当", "官方正版"}
                    ][:4]
                    if not authors:
                        authors = [
                            name
                            for name in (
                                normalize_author_name(part)
                                for part in re.split(r"[,，;；/ ]+", spans[0].get_text(" ", strip=True))
                            )
                            if name
                        ][:4]
                for span in spans[1:]:
                    text = span.get_text(" ", strip=True)
                    date_match = re.search(r"\d{4}-\d{1,2}-\d{1,2}", text)
                    if date_match:
                        parts = date_match.group(0).split("-")
                        publish_date = f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
                    links = span.find_all("a")
                    if links:
                        publisher = clean_text(links[-1].get_text(), 150)
            if not authors:
                authors = ["作者待详情补采"]
            publish_year = publish_date[:4] if publish_date else ""
            rows.append(
                {
                    "source_site": "当当网",
                    "source_item_id": item_id,
                    "source_query_category": leaf.source_category_name,
                    "source_category_path": leaf.source_category_path,
                    "title": title,
                    "isbn": f"DD{item_id}"[:20],
                    "authors": "; ".join(dict.fromkeys(authors)),
                    "publisher": publisher,
                    "publish_year": publish_year,
                    "publish_date_raw": publish_date,
                    "page_count": deterministic_pages(item_id, leaf.category_name),
                    "language": "中文",
                    "category_name": leaf.category_name,
                    "unit": "本",
                    "suggested_unit_price": price,
                    "status": deterministic_status(item_id),
                    "source_url": source_url,
                }
            )
        else:
            if item.select_one("p.search_book_author") is not None:
                continue
            if re.search(r"(出版社|ISBN|978\d{4}|图书|小说|教材|文学|正版书)", title):
                continue
            if re.search(r"(^|[\s，,、])(著|编著|主编|译)($|[\s，,、])", title):
                continue
            rows.append(
                {
                    "source_site": "当当网",
                    "source_item_id": item_id,
                    "source_query_category": leaf.source_category_name,
                    "source_category_path": leaf.source_category_path,
                    "product_name": title,
                    "barcode": f"DDG{item_id}"[:50],
                    "category_name": leaf.category_name,
                    "unit": unit_for_nonbook(leaf.category_name),
                    "suggested_unit_price": price,
                    "status": deterministic_status(item_id),
                    "source_url": source_url,
                }
            )
    return rows


def dangdang_search_url(term: str, page_index: int, is_book: bool) -> str:
    key = quote_from_bytes(term.encode("gbk", errors="ignore"))
    medium = "&medium=01" if is_book else ""
    return f"{DANGDANG_SEARCH_URL}?key={key}&act=input{medium}&page_index={page_index}"


def xhsd_search_url(source_category_id: str, page_index: int) -> str:
    return f"https://search.xhsd.com/search?frontCategoryId={source_category_id}&pageNo={page_index}"


def parse_xhsd_nonbook_products(html_text: str, leaf: ProjectLeaf) -> list[dict[str, str]]:
    soup = BeautifulSoup(html_text, "html.parser")
    rows: list[dict[str, str]] = []
    for item in soup.select("li.product.js-product"):
        item_id = item.get("data-id", "")
        title_anchor = item.select_one(".product-desc a")
        if not item_id or title_anchor is None:
            continue
        author_node = item.select_one(".product-author")
        if author_node is not None and clean_text(author_node.get_text(" ", strip=True)):
            continue
        title = clean_text(title_anchor.get_text(" ", strip=True), 200)
        if not title:
            continue
        price_node = item.select_one(".product-price span")
        price = parse_price(price_node.get_text(" ", strip=True) if price_node else "")
        rows.append(
            {
                "source_site": "新华书店网",
                "source_item_id": item_id,
                "source_query_category": leaf.source_category_name,
                "source_category_path": leaf.source_category_path,
                "product_name": title,
                "barcode": f"XHSD{item_id}"[:50],
                "category_name": leaf.category_name,
                "unit": unit_for_nonbook(leaf.category_name),
                "suggested_unit_price": price,
                "status": deterministic_status(item_id),
                "source_url": f"https://item.xhsd.com/items/{item_id}",
            }
        )
    return rows


def quota_by_parent(leaves: list[ProjectLeaf], target: int, weights: dict[str, Decimal]) -> dict[str, int]:
    grouped: dict[str, list[ProjectLeaf]] = {}
    for leaf in leaves:
        grouped.setdefault(leaf.top_name, []).append(leaf)
    quotas: dict[str, int] = {}
    for top_name, group in grouped.items():
        parent_target = int((Decimal(target) * weights[top_name]).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        per_leaf = max(40, int((Decimal(parent_target) / Decimal(len(group))).quantize(Decimal("1"), rounding=ROUND_HALF_UP)))
        for leaf in group:
            quotas[leaf.category_name] = per_leaf
    return quotas


def target_by_parent(leaves: list[ProjectLeaf], target: int, weights: dict[str, Decimal]) -> dict[str, int]:
    present_top_names = {leaf.top_name for leaf in leaves}
    targets = {
        top_name: int((Decimal(target) * weight).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        for top_name, weight in weights.items()
        if top_name in present_top_names
    }
    delta = target - sum(targets.values())
    if delta and targets:
        first_key = next(iter(targets))
        targets[first_key] += delta
    return targets


def crawl_products(
    leaves: list[ProjectLeaf],
    target: int,
    is_book: bool,
    retries: int,
    timeout: float,
    sleep_seconds: float,
    max_pages_per_category: int,
) -> list[dict[str, str]]:
    weights = BOOK_PARENT_WEIGHTS if is_book else NONBOOK_PARENT_WEIGHTS
    quotas = quota_by_parent(leaves, target, weights)
    parent_targets = target_by_parent(leaves, target, weights)
    accepted_by_parent = {top_name: 0 for top_name in parent_targets}
    rows: list[dict[str, str]] = []
    seen_item_ids: set[str] = set()

    for leaf in leaves:
        if len(rows) >= target:
            break
        parent_remaining = parent_targets.get(leaf.top_name, target) - accepted_by_parent.get(leaf.top_name, 0)
        if parent_remaining <= 0:
            continue
        quota = min(quotas.get(leaf.category_name, 80), parent_remaining)
        accepted_for_leaf = 0
        for page_index in range(1, max_pages_per_category + 1):
            if accepted_for_leaf >= quota or len(rows) >= target:
                break
            url = dangdang_search_url(leaf.source_category_name, page_index, is_book) if is_book else xhsd_search_url(leaf.source_category_id, page_index)
            try:
                html_text = fetch_text(url, "gb18030" if is_book else "utf-8", retries, timeout, sleep_seconds)
            except RuntimeError as exc:
                print(f"skip {leaf.source_category_name} page={page_index}: {exc}")
                continue
            page_rows = parse_dangdang_products(html_text, leaf, is_book) if is_book else parse_xhsd_nonbook_products(html_text, leaf)
            page_accepted = 0
            for row in page_rows:
                item_id = row["source_item_id"]
                if item_id in seen_item_ids:
                    continue
                seen_item_ids.add(item_id)
                rows.append(row)
                accepted_for_leaf += 1
                accepted_by_parent[leaf.top_name] = accepted_by_parent.get(leaf.top_name, 0) + 1
                page_accepted += 1
                if accepted_for_leaf >= quota or len(rows) >= target:
                    break
            print(
                f"{'book' if is_book else 'nonbook'} {leaf.source_category_path} "
                f"page={page_index} accepted={page_accepted} leaf={accepted_for_leaf}/{quota} total={len(rows)}/{target}"
            )
            time.sleep(sleep_seconds)
    if len(rows) < target:
        print(f"top-up pass for {'book' if is_book else 'nonbook'} rows: {len(rows)}/{target}")
        top_up_start_page = max_pages_per_category + 1 if is_book else 1
        for leaf in leaves:
            if len(rows) >= target:
                break
            for page_index in range(top_up_start_page, max_pages_per_category + 6):
                if len(rows) >= target:
                    break
                url = dangdang_search_url(leaf.source_category_name, page_index, is_book) if is_book else xhsd_search_url(leaf.source_category_id, page_index)
                try:
                    html_text = fetch_text(url, "gb18030" if is_book else "utf-8", retries, timeout, sleep_seconds)
                except RuntimeError as exc:
                    print(f"skip top-up {leaf.source_category_name} page={page_index}: {exc}")
                    continue
                page_rows = parse_dangdang_products(html_text, leaf, is_book) if is_book else parse_xhsd_nonbook_products(html_text, leaf)
                page_accepted = 0
                for row in page_rows:
                    item_id = row["source_item_id"]
                    if item_id in seen_item_ids:
                        continue
                    seen_item_ids.add(item_id)
                    rows.append(row)
                    page_accepted += 1
                    if len(rows) >= target:
                        break
                print(
                    f"top-up {'book' if is_book else 'nonbook'} {leaf.source_category_path} "
                    f"page={page_index} accepted={page_accepted} total={len(rows)}/{target}"
                )
                time.sleep(sleep_seconds)
    if len(rows) < target:
        raise SystemExit(f"Collected {len(rows)} {'book' if is_book else 'nonbook'} rows, below target {target}.")
    return rows[:target]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book-target", type=int, default=12000)
    parser.add_argument("--nonbook-target", type=int, default=1200)
    parser.add_argument("--sleep", type=float, default=0.15)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--max-pages-per-category", type=int, default=5)
    parser.add_argument("--skip-books", action="store_true")
    parser.add_argument("--skip-nonbooks", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    SOURCE_DIR.mkdir(exist_ok=True)

    xhsd_html = fetch_text(XHSD_HOME_URL, "utf-8", args.retries, args.timeout, args.sleep)
    xhsd_categories = parse_xhsd_categories(xhsd_html)
    write_csv(
        XHSD_CATEGORY_PATH,
        [
            "source_site",
            "source_category_id",
            "parent_source_category_id",
            "category_name",
            "level",
            "source_category_path",
            "source_url",
            "top_category_name",
            "is_book",
            "is_leaf",
        ],
        [
            {
                "source_site": "新华书店网",
                "source_category_id": row.source_id,
                "parent_source_category_id": row.parent_source_id,
                "category_name": row.name,
                "level": row.level,
                "source_category_path": row.path,
                "source_url": row.source_url,
                "top_category_name": row.top_name,
                "is_book": 1 if row.is_book else 0,
                "is_leaf": 1 if row.is_leaf else 0,
            }
            for row in xhsd_categories
        ],
    )

    dangdang_js = fetch_text(DANGDANG_CATEGORY_JS_URL, "gb18030", args.retries, args.timeout, args.sleep)
    write_csv(
        DANGDANG_CATEGORY_PATH,
        [
            "source_site",
            "source_category_id",
            "parent_source_category_id",
            "category_name",
            "source_category_path",
            "source_url",
        ],
        parse_dangdang_categories(dangdang_js),
    )

    project_categories, leaves = build_project_categories(xhsd_categories)
    write_csv(PROJECT_CATEGORY_PATH, CSV_CATEGORY_FIELDS, project_categories)

    book_leaves = [leaf for leaf in leaves if leaf.is_book]
    nonbook_root_id = next(row["category_id"] for row in project_categories if row["category_name"] == "通用商品")
    nonbook_leaves = [
        ProjectLeaf(
            category_name=str(row["category_name"]),
            source_category_name=str(row["source_category_name"]),
            source_category_id=str(row["source_category_id"]),
            source_category_path=str(row["source_category_path"]),
            top_name=str(row["category_name"]),
            is_book=False,
        )
        for row in project_categories
        if row["parent_category_id"] == nonbook_root_id and row["category_name"] in NONBOOK_PARENT_WEIGHTS
    ]
    if not args.skip_books:
        book_rows = crawl_products(
            book_leaves,
            args.book_target,
            True,
            args.retries,
            args.timeout,
            args.sleep,
            args.max_pages_per_category,
        )
        write_csv(BOOK_SOURCE_PATH, CSV_BOOK_FIELDS, book_rows)

    if not args.skip_nonbooks:
        nonbook_rows = crawl_products(
            nonbook_leaves,
            args.nonbook_target,
            False,
            args.retries,
            args.timeout,
            args.sleep,
            args.max_pages_per_category,
        )
        write_csv(NONBOOK_SOURCE_PATH, CSV_NONBOOK_FIELDS, nonbook_rows)


if __name__ == "__main__":
    main()
