"""Rebuild clean bookstore seed data from publisher catalog sources.

Inputs:
- data/**/*.xlsx, data/**/*.xlsm, data/**/*.xls
- selected text-readable PDFs
- China Publishing Group fine-book pages
- SDX Joint Publishing book pages

Outputs:
- data/clean/book_source.csv and audit files
- clean sql/data/*.csv matching backend/common/sql.py
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

try:
    import fitz
except ImportError:  # pragma: no cover
    fitz = None


def repo_root() -> Path:
    if Path("sql/tools/rebuild_clean_book_data.py").exists() and Path("data").exists():
        return Path(".")
    return Path(__file__).resolve().parents[2]


REPO_ROOT = repo_root()
SOURCE_DIR = REPO_ROOT / "data"
SQL_DATA_DIR = REPO_ROOT / "sql" / "data"
CLEAN_DIR = SOURCE_DIR / "clean"
RAW_WEB_DIR = SOURCE_DIR / "raw" / "web_catalog"

SOURCE_CSV = CLEAN_DIR / "book_source.csv"
ACCEPTED_CSV = CLEAN_DIR / "books_accepted.csv"
REJECTED_CSV = CLEAN_DIR / "books_rejected.csv"
CATEGORY_AUDIT_CSV = CLEAN_DIR / "category_mapping_audit.csv"
SOURCE_AUDIT_CSV = CLEAN_DIR / "source_file_audit.csv"
REPORT_MD = CLEAN_DIR / "clean_data_report.md"

CSV_HEADERS = {
    "store": ["store_id", "store_name", "city", "address", "phone", "manager_name"],
    "supplier": ["supplier_id", "supplier_name", "contact_name", "phone", "email", "status"],
    "category": ["category_id", "category_name", "parent_category_id"],
    "publisher": ["publisher_id", "publisher_name", "contact_name", "phone", "email", "address", "country", "website"],
    "product": ["product_id", "product_name", "category_id", "unit", "unit_price", "cost_price", "barcode", "status"],
    "book": ["product_id", "isbn", "publisher_id", "publish_date", "edition", "language", "page_count"],
    "author": ["author_id", "author_name", "country"],
    "translator": ["translator_id", "translator_name", "country"],
    "book_author": ["product_id", "author_id", "author_order"],
    "book_translator": ["product_id", "translator_id"],
    "supplier_product": ["supplier_id", "product_id", "supply_price", "min_order_qty", "is_primary"],
    "customer": ["customer_id", "customer_name", "phone", "email", "address", "register_time", "status"],
    "member": ["customer_id", "member_no", "level", "points", "join_date"],
    "system_user": ["user_id", "username", "password_hash", "real_name", "phone", "email", "status"],
    "role": ["role_id", "role_name", "role_desc"],
    "permission": ["permission_id", "permission_code", "permission_name", "module_name"],
    "user_role": ["user_id", "role_id"],
    "role_permission": ["role_id", "permission_id"],
    "purchase_order": ["purchase_order_id", "supplier_id", "store_id", "created_by", "order_time", "status", "total_amount"],
    "purchase_order_item": ["purchase_order_id", "line_no", "product_id", "quantity", "purchase_price", "line_amount"],
    "stock_in": ["stock_in_id", "purchase_order_id", "store_id", "operator_id", "inbound_time", "status"],
    "stock_in_item": ["stock_in_id", "line_no", "product_id", "quantity", "unit_cost", "line_amount"],
    "inventory": ["store_id", "product_id", "stock_qty", "safety_stock_qty"],
    "sale": ["sale_id", "store_id", "customer_id", "sale_time", "payment_method", "total_amount", "discount_amount", "actual_amount"],
    "sale_item": ["sale_id", "line_no", "product_id", "quantity", "unit_price", "line_amount"],
}

MARKETING_OR_BAD_TITLE_TERMS = [
    "包邮",
    "新华书店",
    "当当网",
    "当当自营",
    "自营",
    "旗舰店",
    "点击购买",
    "已撤销",
]

PUBLISHER_BY_PATH = [
    ("人民邮电出版社", "人民邮电出版社", "https://www.ptpress.com.cn/"),
    ("人民卫生出版社", "人民卫生出版社", "https://www.pmph.com/"),
    ("人大社", "中国人民大学出版社", "https://www.crup.com.cn/"),
    ("中国人民大学", "中国人民大学出版社", "https://www.crup.com.cn/"),
    ("北京大学出版社", "北京大学出版社", "https://www.pup.cn/"),
    ("清华社", "清华大学出版社", "https://www.tup.tsinghua.edu.cn/"),
    ("清华大学出版社", "清华大学出版社", "https://www.tup.tsinghua.edu.cn/"),
    ("商务印书馆", "商务印书馆", "https://www.cp.com.cn/"),
    ("外研社", "外语教学与研究出版社", "https://www.fltrp.com/"),
    ("中国社会科学出版社", "中国社会科学出版社", "https://www.csspw.cn/"),
    ("中华书局", "中华书局", "https://www.zhbc.com.cn/"),
    ("高等教育出版社", "高等教育出版社", "https://www.hep.com.cn/"),
    ("复旦大学出版社", "复旦大学出版社", "https://www.fudanpress.com/"),
    ("国家图书馆出版社", "国家图书馆出版社", "https://www.nlcpress.com/"),
    ("法律出版社", "法律出版社", "https://www.lawpress.com.cn/"),
]

PUBLISHER_PROFILES = {
    "世界图书出版公司": {"website": "https://www.wpcbj.com.cn/", "contact_name": "发行部"},
    "东方出版中心": {"website": "https://www.ewen.co/", "contact_name": "发行部"},
    "中华书局": {"website": "https://www.zhbc.com.cn/", "contact_name": "发行部"},
    "中国人民大学出版社": {"website": "https://www.crup.com.cn/", "contact_name": "发行部"},
    "中国大百科全书出版社": {"website": "https://www.ecph.com.cn/", "contact_name": "发行部"},
    "中国民主法制出版社": {"website": "https://www.npcpub.com/", "contact_name": "发行部"},
    "中国社会科学出版社": {"website": "https://www.csspw.cn/", "contact_name": "发行部"},
    "中译出版社": {"website": "http://www.ctpc.com.cn/", "contact_name": "发行部"},
    "人民卫生出版社": {"website": "https://www.pmph.com/", "contact_name": "发行部"},
    "人民文学出版社": {"website": "https://www.rw-cn.com/", "contact_name": "发行部"},
    "人民美术出版社": {"website": "http://www.renmei.com.cn/", "contact_name": "发行部"},
    "人民邮电出版社": {"website": "https://www.ptpress.com.cn/", "contact_name": "发行部"},
    "人民音乐出版社": {"website": "https://www.rymusic.art/", "contact_name": "发行部"},
    "人民音乐电子音像出版社": {"website": "https://www.rymusic.art/", "contact_name": "发行部"},
    "北京交通大学出版社": {"website": "https://press.bjtu.edu.cn/", "contact_name": "发行部"},
    "北京大学出版社": {"website": "https://www.pup.cn/", "contact_name": "发行部"},
    "华文出版社": {"website": "http://www.hwcbs.com.cn/", "contact_name": "发行部"},
    "吉林大学出版社": {"website": "http://www.jlup.com.cn/", "contact_name": "发行部"},
    "商务印书馆": {"website": "https://www.cp.com.cn/", "contact_name": "发行部"},
    "商务印书馆国际有限公司": {"website": "https://www.cp.com.cn/", "contact_name": "发行部"},
    "复旦大学出版社": {"website": "https://www.fudanpress.com/", "contact_name": "发行部"},
    "外语教学与研究出版社": {"website": "https://www.fltrp.com/", "contact_name": "发行部"},
    "天天出版社": {"website": "https://www.rw-cn.com/", "contact_name": "发行部"},
    "清华大学出版社": {"website": "https://www.tup.tsinghua.edu.cn/", "contact_name": "发行部"},
    "现代出版社": {"website": "http://www.modernpress.cn/", "contact_name": "发行部"},
    "现代教育出版社": {"website": "http://www.mepcbs.com/", "contact_name": "发行部"},
    "生活·读书·新知三联书店": {"website": "http://www.sdxjpc.com/", "contact_name": "发行部"},
    "研究出版社": {"website": "http://www.yjcbs.com/", "contact_name": "发行部"},
    "荣宝斋出版社": {"website": "http://www.rongbaozhai.cn/", "contact_name": "发行部"},
    "连环画出版社": {"website": "http://www.lhhcbs.com/", "contact_name": "发行部"},
    "高等教育出版社": {"website": "https://www.hep.com.cn/", "contact_name": "发行部"},
}

PUBLISHER_WEBSITES = {name: profile["website"] for name, profile in PUBLISHER_PROFILES.items()}

PUBLISHER_NORMALIZATION = {
    "三联书店": "生活·读书·新知三联书店",
    "中国民主法制出版社有限公司": "中国民主法制出版社",
    "世界图书出版有限公司": "世界图书出版公司",
    "人民文学出版社\xa0天天出版社": "人民文学出版社",
    "人民文学出版社 天天出版社": "人民文学出版社",
    "人民文学出版社\xa0等": "人民文学出版社",
    "人民文学出版社等": "人民文学出版社",
    "天天出版社等": "天天出版社",
    "研究出版社\xa0等": "研究出版社",
    "商务印书": "商务印书馆",
    "荣宝斋": "荣宝斋出版社",
    "生活·读书·新知三联书店 ...": "生活·读书·新知三联书店",
    "生活书店": "生活·读书·新知三联书店",
    "生活书店出版有限公司": "生活·读书·新知三联书店",
}

BOOK_CATEGORY_TREE = {
    "图书": {
        "教材教辅": ["大学教材", "高职高专教材", "中小学及考试", "职业教育教材"],
        "人文社科": ["历史考古", "哲学宗教", "社会科学", "教育新闻传播", "文化国学"],
        "文学艺术": ["文学作品", "小说散文诗歌", "艺术设计", "音乐影视", "书法绘画"],
        "科技工程": ["计算机与电子", "数学物理", "工业技术", "建筑工程", "农林科学"],
        "医学卫生": ["西医", "中医药学", "健康科普"],
        "经济管理": ["经济金融", "工商管理", "会计营销"],
        "法律政务": ["法律法规", "法学理论", "党政读物"],
        "语言工具": ["汉语工具书", "外语学习", "小语种", "辞书百科"],
        "少儿童书": ["儿童文学", "少儿科普", "启蒙绘本"],
        "生活休闲": ["旅游地理", "运动健身", "生活美育"],
        "古籍文献": ["古籍整理", "文献档案", "图书馆学"],
        "综合图书": ["综合读物"],
    }
}


@dataclass
class SourceBook:
    isbn: str
    title: str
    subtitle: str = ""
    authors_raw: str = ""
    translators_raw: str = ""
    publisher_name: str = ""
    publish_date: str = ""
    price: str = ""
    page_count: str = ""
    edition: str = ""
    series: str = ""
    source_category: str = ""
    source_name: str = ""
    source_file: str = ""
    source_url: str = ""
    source_kind: str = ""
    raw_row_hash: str = ""
    authors: list[str] = field(default_factory=list)
    translators: list[str] = field(default_factory=list)
    category_path: str = ""
    category_reason: str = ""


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).replace("\u3000", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_header(value: Any) -> str:
    return re.sub(r"[\s　:：/（）()、.-]", "", compact(value).lower())


def stable_int(seed: str, modulo: int) -> int:
    return int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12], 16) % modulo


def quantize_money(value: Decimal | str | float | int) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def isbn13_check_digit(prefix12: str) -> str:
    total = sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(prefix12))
    return str((10 - total % 10) % 10)


def validate_isbn13(isbn: str) -> bool:
    return len(isbn) == 13 and isbn.isdigit() and isbn[:3] in {"978", "979"} and isbn13_check_digit(isbn[:12]) == isbn[-1]


def normalize_isbn(value: Any) -> str:
    text = compact(value)
    if not text or text.upper().startswith("DD"):
        return ""
    matches = re.findall(r"(?:97[89][0-9\-\s]{8,25}|[0-9][0-9\-\s]{8,15}[0-9Xx])", text)
    if not matches:
        matches = [text]
    for match in matches:
        token = re.sub(r"(?i)isbn|国际标准书号|书号|条码|条形码", "", match)
        token = re.sub(r"[^0-9Xx]", "", token)
        if len(token) > 13 and token.startswith(("978", "979")):
            token = token[:13]
        if len(token) == 13 and validate_isbn13(token):
            return token
    return ""


def parse_price(value: Any) -> str:
    text = compact(value).replace(",", "")
    if not text:
        return ""
    match = re.search(r"([0-9]+(?:\.[0-9]{1,2})?)", text)
    if not match:
        return ""
    try:
        price = Decimal(match.group(1))
    except InvalidOperation:
        return ""
    if price <= 0 or price > Decimal("5000"):
        return ""
    return quantize_money(price)


def parse_page_count(value: Any) -> str:
    text = compact(value).replace(",", "")
    if not text:
        return ""
    matches = [int(m) for m in re.findall(r"([0-9]{1,5})\s*页", text)]
    if not matches:
        matches = [int(m) for m in re.findall(r"([0-9]{2,5})", text)]
    if not matches:
        return ""
    page_count = max(matches)
    return str(page_count) if 0 < page_count <= 50000 else ""


def parse_date(value: Any) -> str:
    text = compact(value)
    if not text:
        return ""
    if isinstance(value, (datetime, date)):
        return value.strftime("%Y-%m-%d")
    if re.fullmatch(r"[0-9]+(?:\.0)?", text):
        raw = text.split(".")[0]
        if len(raw) == 8:
            return f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"
        if len(raw) == 6:
            return f"{raw[:4]}-{raw[4:6]}-01"
    patterns = [
        r"([12][0-9]{3})[-./年]([01]?[0-9])[-./月]([0-3]?[0-9])",
        r"([12][0-9]{3})[-./年]([01]?[0-9])",
        r"([12][0-9]{3})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        year = int(match.group(1))
        month = int(match.group(2)) if len(match.groups()) >= 2 else 1
        day = int(match.group(3)) if len(match.groups()) >= 3 else 1
        if 1 <= month <= 12 and 1 <= day <= 31:
            return f"{year:04d}-{month:02d}-{day:02d}"
    return ""


def infer_publisher(path_or_name: str, explicit: str = "") -> tuple[str, str]:
    explicit = compact(explicit)
    if explicit and explicit not in {"出版社", "nan"}:
        name = normalize_publisher_name(explicit)
        return name, PUBLISHER_WEBSITES.get(name, "")
    haystack = str(path_or_name)
    for needle, publisher, website in PUBLISHER_BY_PATH:
        if needle in haystack:
            return publisher, website
    return "", ""


def normalize_publisher_name(value: str) -> str:
    name = compact(value).replace("\xa0", " ")
    name = re.sub(r"\s+", " ", name).strip()
    name = PUBLISHER_NORMALIZATION.get(name, name)
    name = re.sub(r"\s*等$", "", name)
    if re.search(r"[，,、；;]", name):
        name = re.split(r"[，,、；;]", name)[0].strip()
    name = PUBLISHER_NORMALIZATION.get(name, name)
    return name[:150]


def clean_title(title: str, subtitle: str = "", volume: str = "", volume_name: str = "") -> str:
    pieces = [compact(title), compact(volume), compact(volume_name)]
    main = " ".join(piece for piece in pieces if piece)
    sub = compact(subtitle)
    if sub and sub not in main:
        main = f"{main}：{sub}" if main else sub
    main = re.sub(r"[【\[]?已撤销[】\]]?", "", main)
    main = re.sub(r"^(全新)?正版[：:：\s-]*", "", main)
    main = re.sub(r"（?另赠[^）)]*[）)]?", "", main)
    main = re.sub(r"（?配在线课程[^）)]*[）)]?", "", main)
    main = re.sub(r"\s+", " ", main).strip(" -_")
    return main[:200]


def is_bad_title(title: str) -> bool:
    if not title or len(title) > 200:
        return True
    if any(term in title for term in MARKETING_OR_BAD_TITLE_TERMS):
        return True
    return bool(re.search(r"(^|[【\[(（\s])正版([】\])）\s]|$|图书|书籍|教材|现货|包邮|全新)", title))


def strip_role_tokens(name: str) -> str:
    name = compact(name)
    name = re.sub(r"^(作者|著者|编者|主编|编著|译者|翻译|原编|修订)[：:]\s*", "", name)
    name = re.sub(r"(著|编著|主编|编|译|校译|点校|校注|绘|整理|撰|曲|供稿|等)$", "", name)
    name = re.sub(r"^(全新)?正版[：:：\s-]*", "", name)
    for term in MARKETING_OR_BAD_TITLE_TERMS:
        name = name.replace(term, "")
    return name.strip(" []【】()（）")


def split_people(text: Any) -> list[str]:
    raw = compact(text)
    if not raw:
        return []
    raw = raw.replace("\n", " ")
    raw = re.sub(r"\[[^\]]{1,20}\]", "", raw)
    raw = re.sub(r"（[^）]{1,40}）", "", raw)
    raw = re.sub(r"\([^)]{1,80}\)", "", raw)
    parts = re.split(r"[、,，;/；|]| 和 | 与 |&|  +", raw)
    people: list[str] = []
    for part in parts:
        name = strip_role_tokens(part)
        if not name or name in {"本书编写组", "编写组", "无", "暂无"}:
            continue
        if re.fullmatch(r"(作者|著者|编者|主编|译者|翻译|原编|修订)[：:]?", name):
            continue
        if re.fullmatch(r"[0-9A-Za-z._ -]+", name) and len(name) < 4:
            continue
        if len(name) > 60:
            continue
        if name not in people:
            people.append(name)
    return people


def split_authors_translators(author_text: Any, translator_text: Any = "") -> tuple[list[str], list[str]]:
    authors: list[str] = []
    translators: list[str] = []
    translator_text = compact(translator_text)
    if translator_text:
        translators.extend(split_people(translator_text))
    raw = compact(author_text)
    if raw:
        chunks = re.split(r"(?<=[，,；;])|(?=译)|(?=翻译)", raw)
        author_buf: list[str] = []
        for chunk in chunks:
            if "译" in chunk or "翻译" in chunk:
                translators.extend(split_people(chunk))
            else:
                author_buf.append(chunk)
        authors.extend(split_people("".join(author_buf)))
    return unique(authors), unique(translators)


def unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def hash_row(values: dict[str, Any]) -> str:
    payload = json.dumps(values, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def find_header_row(df: pd.DataFrame) -> int | None:
    best_idx = None
    best_score = 0
    for idx in range(min(len(df), 30)):
        cells = [normalize_header(v) for v in df.iloc[idx].tolist()]
        score = 0
        if any(c in {"isbn", "书号", "条码书号", "条形码", "条码"} for c in cells):
            score += 4
        if any(c in {"书名", "正题名", "题名"} for c in cells):
            score += 4
        if any(c in {"作者", "责任者", "第一责任者", "著译者", "主编", "作者及著作方式", "作 者".replace(" ", "")} for c in cells):
            score += 2
        if any(c in {"定价", "单价", "估定价", "价格"} for c in cells):
            score += 2
        if score > best_score:
            best_idx = idx
            best_score = score
    return best_idx if best_score >= 6 else None


def col_index(header: list[str], aliases: list[str]) -> int | None:
    normalized_aliases = {normalize_header(alias) for alias in aliases}
    for idx, value in enumerate(header):
        if normalize_header(value) in normalized_aliases:
            return idx
    return None


def value_at(row: list[Any], idx: int | None) -> str:
    if idx is None or idx >= len(row):
        return ""
    return compact(row[idx])


def iter_excel_books(path: Path) -> tuple[list[SourceBook], dict[str, Any]]:
    books: list[SourceBook] = []
    audit = {"source": str(path), "kind": path.suffix.lower(), "rows": 0, "accepted_like": 0, "status": "ok", "notes": ""}
    try:
        xls = pd.ExcelFile(path)
    except Exception as exc:
        audit.update({"status": "read_failed", "notes": f"{type(exc).__name__}: {exc}"})
        return books, audit
    for sheet_name in xls.sheet_names:
        try:
            df = pd.read_excel(path, sheet_name=sheet_name, header=None, dtype=object)
        except Exception as exc:
            audit["notes"] += f" sheet {sheet_name} failed: {type(exc).__name__}: {exc};"
            continue
        if df.empty:
            continue
        header_idx = find_header_row(df)
        if header_idx is None:
            continue
        header = [compact(v) for v in df.iloc[header_idx].tolist()]
        isbn_header_names = {"isbn", "书号", "条码书号", "条形码", "条码", "书号"}
        isbn_indices = [idx for idx, name in enumerate(header) if normalize_header(name) in isbn_header_names]
        idx_isbn = isbn_indices[0] if isbn_indices else None
        idx_title = col_index(header, ["书名", "书  名", "书    名", "正题名", "题名"])
        idx_subtitle = col_index(header, ["副题名", "副书名"])
        idx_volume = col_index(header, ["分册号", "分辑号"])
        idx_volume_name = col_index(header, ["分册名", "分辑名"])
        idx_series = col_index(header, ["丛书名", "丛书名/系列名/其他标注", "丛书名/（系列名）"])
        idx_author = col_index(header, ["作者", "作  者", "责任者", "第一责任者", "著译者", "主编", "作者及著作方式"])
        idx_translator = col_index(header, ["译者", "第二责任者"])
        idx_price = col_index(header, ["定价", "定 价", "单价", "估定价", "价格"])
        idx_publisher = col_index(header, ["出版社"])
        idx_date = col_index(header, ["出版日期", "首版日期", "时间"])
        idx_edition = col_index(header, ["版次"])
        idx_pages = col_index(header, ["页数"])
        category_indices = [
            idx
            for idx, name in enumerate(header)
            if normalize_header(name)
            in {
                "图书分类",
                "发行一级分类",
                "发行二级分类",
                "发行三级分类",
                "专业类别",
                "跨类名称",
                "编目类别",
                "所属部门",
                "分类号",
                "项目",
                "重点项目1",
                "重点项目2",
            }
        ]
        if idx_title is None and idx_isbn is not None and idx_isbn + 1 < len(header):
            idx_title = idx_isbn + 1
        current_section = ""
        for _, series_row in df.iloc[header_idx + 1 :].iterrows():
            row = series_row.tolist()
            audit["rows"] += 1
            title_probe = value_at(row, idx_title)
            isbn = ""
            for idx in isbn_indices:
                isbn = normalize_isbn(value_at(row, idx))
                if isbn:
                    break
            if not isbn:
                isbn = normalize_isbn(" ".join(value_at(row, idx) for idx in isbn_indices))
            if not isbn and title_probe and not parse_price(value_at(row, idx_price)):
                if len(title_probe) <= 60 and not re.search(r"[0-9]{5,}", title_probe):
                    current_section = title_probe
                continue
            if not isbn:
                continue
            raw_title = value_at(row, idx_title)
            title = clean_title(
                raw_title,
                subtitle=value_at(row, idx_subtitle),
                volume=value_at(row, idx_volume),
                volume_name=value_at(row, idx_volume_name),
            )
            if not title:
                continue
            publisher, _ = infer_publisher(str(path), value_at(row, idx_publisher))
            source_category_parts = [sheet_name, current_section]
            source_category_parts.extend(value_at(row, idx) for idx in category_indices)
            source_category = " > ".join(part for part in source_category_parts if part)
            book = SourceBook(
                isbn=isbn,
                title=title,
                subtitle=value_at(row, idx_subtitle),
                authors_raw=value_at(row, idx_author),
                translators_raw=value_at(row, idx_translator),
                publisher_name=publisher,
                publish_date=parse_date(value_at(row, idx_date)),
                price=parse_price(value_at(row, idx_price)),
                page_count=parse_page_count(value_at(row, idx_pages)),
                edition=value_at(row, idx_edition)[:20],
                series=value_at(row, idx_series),
                source_category=source_category,
                source_name=publisher or path.stem,
                source_file=str(path.relative_to(REPO_ROOT)),
                source_kind=path.suffix.lower().lstrip("."),
            )
            book.authors, book.translators = split_authors_translators(book.authors_raw, book.translators_raw)
            book.raw_row_hash = hash_row(book.__dict__)
            books.append(book)
            audit["accepted_like"] += 1
    return books, audit


def iter_zhonghua_pdf(path: Path) -> tuple[list[SourceBook], dict[str, Any]]:
    books: list[SourceBook] = []
    audit = {"source": str(path), "kind": "pdf", "rows": 0, "accepted_like": 0, "status": "ok", "notes": ""}
    audit.update({"status": "skipped", "notes": "PDF text extraction is not reliable enough for clean seed data"})
    return books, audit
    if fitz is None:
        audit.update({"status": "read_failed", "notes": "PyMuPDF unavailable"})
        return books, audit
    if "中华书局" not in path.name:
        audit.update({"status": "skipped", "notes": "PDF text layout is not supported by current parser"})
        return books, audit
    try:
        doc = fitz.open(path)
    except Exception as exc:
        audit.update({"status": "read_failed", "notes": f"{type(exc).__name__}: {exc}"})
        return books, audit
    current_section = ""
    for page_index in range(doc.page_count):
        text = doc.load_page(page_index).get_text("text")
        lines = [compact(line) for line in text.splitlines() if compact(line)]
        for i, line in enumerate(lines):
            if re.fullmatch(r"\d+\..{2,30}", line):
                current_section = line
            match = re.match(r"^(978[0-9]{10})\s+(.+)$", line)
            if not match:
                continue
            isbn = normalize_isbn(match.group(1))
            title = clean_title(match.group(2))
            if not isbn or not title:
                continue
            following = lines[i + 1 : i + 8]
            author_parts: list[str] = []
            price = ""
            for item in following:
                if re.fullmatch(r"(16|32|64|8|24|12)", item):
                    continue
                if re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})", item):
                    price = parse_price(item)
                    break
                if not re.match(r"^9 7 8", item):
                    author_parts.append(item)
            book = SourceBook(
                isbn=isbn,
                title=title,
                authors_raw=" ".join(author_parts[:3]),
                publisher_name="中华书局",
                price=price,
                source_category=current_section,
                source_name="中华书局",
                source_file=str(path.relative_to(REPO_ROOT)),
                source_kind="pdf",
            )
            book.authors, book.translators = split_authors_translators(book.authors_raw)
            book.raw_row_hash = hash_row(book.__dict__)
            books.append(book)
            audit["accepted_like"] += 1
            audit["rows"] += 1
    return books, audit


class CachedWeb:
    def __init__(self, delay: float = 0.2, cache_only: bool = False, timeout: int = 25) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (FDU-Database clean seed crawler)"})
        self.delay = delay
        self.last_at = 0.0
        self.cache_only = cache_only
        self.timeout = timeout

    def path_for(self, url: str) -> Path:
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return RAW_WEB_DIR / f"{key}.html"

    def get(self, url: str) -> str:
        RAW_WEB_DIR.mkdir(parents=True, exist_ok=True)
        path = self.path_for(url)
        if path.exists():
            return path.read_text(encoding="utf-8", errors="ignore")
        if self.cache_only:
            raise FileNotFoundError(f"cache miss for {url}")
        elapsed = time.time() - self.last_at
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        response = self.session.get(url, timeout=self.timeout)
        self.last_at = time.time()
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding
        path.write_text(response.text, encoding="utf-8")
        return response.text


def cnpubg_booklist_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(" ", strip=True)
        href = urljoin(base_url, anchor["href"])
        if "action=finebook" not in href or "booklistid=" not in href:
            continue
        year_match = re.search(r"(20[2][0-6])", text)
        if not year_match:
            continue
        if href not in links:
            links.append(href)
    return links


def cnpubg_parse_detail(html: str, url: str) -> SourceBook | None:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    title = ""
    marker = "图书详细内容"
    if marker in text:
        after = text.split(marker, 1)[1].split("\n")
        title = clean_title(after[0] if after else "")
    if not title:
        title = clean_title((soup.find("h1") or soup.find("title") or soup).get_text(" ", strip=True).split("_")[0])
    fields = {}
    labels = ["作者", "出版社", "出版日期", "ISBN", "定价", "分类", "页数", "版印次"]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for idx, line in enumerate(lines):
        for label in labels:
            if line.startswith(label + "："):
                fields[label] = line.split("：", 1)[1].strip()
            elif line == label + "：" and idx + 1 < len(lines):
                fields[label] = lines[idx + 1]
    isbn = normalize_isbn(fields.get("ISBN", ""))
    price = parse_price(fields.get("定价", ""))
    if not isbn or not title:
        return None
    book = SourceBook(
        isbn=isbn,
        title=title,
        authors_raw=fields.get("作者", ""),
        publisher_name=normalize_publisher_name(fields.get("出版社", "")),
        publish_date=parse_date(fields.get("出版日期", "")),
        price=price,
        page_count=parse_page_count(fields.get("页数", "")),
        edition="",
        source_category=fields.get("分类", ""),
        source_name="中国出版集团好书榜",
        source_url=url,
        source_kind="web",
    )
    book.authors, book.translators = split_authors_translators(book.authors_raw)
    book.raw_row_hash = hash_row(book.__dict__)
    return book


def crawl_cnpubg(max_lists: int = 0) -> tuple[list[SourceBook], dict[str, Any]]:
    base = "http://book.cnpubg.com/?app=book&controller=book&action=finebook&booklistid=461"
    client = CachedWeb()
    books: list[SourceBook] = []
    audit = {"source": base, "kind": "web", "rows": 0, "accepted_like": 0, "status": "ok", "notes": ""}
    try:
        first_html = client.get(base)
        list_links = cnpubg_booklist_links(first_html, base)
        if max_lists:
            list_links = list_links[:max_lists]
        for list_url in list_links:
            seen_details: set[str] = set()
            page = 1
            while True:
                parsed = urlparse(list_url)
                query = parse_qs(parsed.query)
                query["page"] = [str(page)]
                query["pagesize"] = ["10"]
                page_url = urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
                html = client.get(page_url)
                soup = BeautifulSoup(html, "html.parser")
                detail_links = []
                for anchor in soup.find_all("a", href=True):
                    href = urljoin(page_url, anchor["href"])
                    if "action=showfinebook" in href and href not in seen_details:
                        detail_links.append(href)
                        seen_details.add(href)
                if not detail_links:
                    break
                for detail_url in detail_links:
                    detail = cnpubg_parse_detail(client.get(detail_url), detail_url)
                    audit["rows"] += 1
                    if detail:
                        books.append(detail)
                        audit["accepted_like"] += 1
                if "下一页" not in soup.get_text(" ", strip=True):
                    break
                page += 1
                if page > 20:
                    break
    except Exception as exc:
        audit.update({"status": "partial_failed", "notes": f"{type(exc).__name__}: {exc}"})
    return books, audit


def sanlian_parse_detail(html: str, url: str) -> SourceBook | None:
    soup = BeautifulSoup(html, "html.parser")
    lines = [line.strip() for line in soup.get_text("\n", strip=True).splitlines() if line.strip()]
    title = ""
    if "图书详细" in lines:
        idx = lines.index("图书详细")
        if idx + 1 < len(lines):
            title = clean_title(lines[idx + 1])
    fields = {}
    for line in lines:
        for label in ["作者", "ISBN", "出版日期", "定价"]:
            if line.startswith(label + "："):
                fields[label] = line.split("：", 1)[1].strip()
    isbn = normalize_isbn(fields.get("ISBN", ""))
    if not isbn or not title:
        return None
    book = SourceBook(
        isbn=isbn,
        title=title,
        authors_raw=fields.get("作者", ""),
        publisher_name="生活·读书·新知三联书店",
        publish_date=parse_date(fields.get("出版日期", "")),
        price=parse_price(fields.get("定价", "")),
        source_category="三联书店官网",
        source_name="三联书店官网",
        source_url=url,
        source_kind="web",
    )
    book.authors, book.translators = split_authors_translators(book.authors_raw)
    book.raw_row_hash = hash_row(book.__dict__)
    return book


def crawl_sanlian(max_pages: int = 323, workers: int = 8, cache_only: bool = False, stop_after_list_errors: int = 20) -> tuple[list[SourceBook], dict[str, Any]]:
    client = CachedWeb(cache_only=cache_only, timeout=12)
    books: list[SourceBook] = []
    base = "http://www.sdxjpc.com/scrp/book.cfm"
    audit = {
        "source": base,
        "kind": "web",
        "rows": 0,
        "accepted_like": 0,
        "status": "ok",
        "notes": f"max_pages={max_pages}; workers={workers}; cache_only={cache_only}",
    }
    detail_links: list[str] = []
    seen_links: set[str] = set()
    list_errors = 0
    consecutive_list_errors = 0
    try:
        for page in range(1, max_pages + 1):
            page_cache = client.path_for(base + "?post_page=" + str(page))
            if page_cache.exists():
                page_html = page_cache.read_text(encoding="utf-8", errors="ignore")
            else:
                page_html = ""
                last_error: Exception | None = None
                if not cache_only:
                    for attempt in range(3):
                        try:
                            html = client.session.post(
                                base,
                                data={"sFieldName": "bname", "sKeyword": "", "iSortField": "7", "sSortOrder": "desc", "iPage": str(page)},
                                timeout=12,
                            )
                            html.raise_for_status()
                            html.encoding = html.apparent_encoding or html.encoding
                            page_html = html.text
                            page_cache.write_text(page_html, encoding="utf-8")
                            break
                        except Exception as exc:  # pragma: no cover - depends on network state
                            last_error = exc
                            time.sleep(1 + attempt)
                if not page_html:
                    list_errors += 1
                    consecutive_list_errors += 1
                    if list_errors <= 3 and last_error is not None:
                        audit["notes"] += f"; page_{page}_error={type(last_error).__name__}"
                    if consecutive_list_errors >= stop_after_list_errors:
                        audit["notes"] += f"; stopped_after_page={page}"
                        break
                    continue
            consecutive_list_errors = 0
            soup = BeautifulSoup(page_html, "html.parser")
            for anchor in soup.find_all("a", href=True):
                href = urljoin(base, anchor["href"])
                if "bookdetail.cfm?iBookNo=" in href and href not in seen_links:
                    seen_links.add(href)
                    detail_links.append(href)

        def fetch_detail(detail_url: str) -> tuple[SourceBook | None, str]:
            try:
                detail_client = CachedWeb(delay=0.05, cache_only=cache_only, timeout=12)
                return sanlian_parse_detail(detail_client.get(detail_url), detail_url), ""
            except Exception as exc:  # pragma: no cover - depends on network state
                return None, f"{type(exc).__name__}: {exc}"

        errors = 0
        with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            for detail, error in executor.map(fetch_detail, detail_links):
                audit["rows"] += 1
                if error:
                    errors += 1
                elif detail:
                    books.append(detail)
                    audit["accepted_like"] += 1
        if errors:
            audit.update({"status": "partial_failed", "notes": audit["notes"] + f"; detail_errors={errors}"})
        if list_errors:
            audit.update({"status": "partial_failed", "notes": audit["notes"] + f"; list_errors={list_errors}"})
    except Exception as exc:
        audit.update({"status": "partial_failed", "notes": audit["notes"] + f"; {type(exc).__name__}: {exc}"})
    return books, audit


def collect_sources(args: argparse.Namespace) -> tuple[list[SourceBook], list[dict[str, Any]]]:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    all_books: list[SourceBook] = []
    audits: list[dict[str, Any]] = []
    for path in sorted(SOURCE_DIR.rglob("*")):
        if not path.is_file() or "data\\clean" in str(path) or "data\\raw" in str(path):
            continue
        suffix = path.suffix.lower()
        if suffix in {".xlsx", ".xlsm", ".xls"}:
            books, audit = iter_excel_books(path)
        elif suffix == ".pdf":
            books, audit = iter_zhonghua_pdf(path)
        else:
            continue
        all_books.extend(books)
        audits.append(audit)
    if args.crawl_web:
        books, audit = crawl_cnpubg(args.cnpubg_max_lists)
        all_books.extend(books)
        audits.append(audit)
        books, audit = crawl_sanlian(
            args.sanlian_pages,
            args.sanlian_workers,
            cache_only=args.sanlian_cache_only,
            stop_after_list_errors=args.sanlian_stop_after_list_errors,
        )
        all_books.extend(books)
        audits.append(audit)
    return all_books, audits


def rejection_reason(book: SourceBook) -> str:
    book.publisher_name = normalize_publisher_name(book.publisher_name)
    if not book.isbn:
        return "missing_or_invalid_isbn"
    if book.isbn.startswith("978789"):
        return "non_print_or_electronic_publication"
    if is_bad_title(book.title):
        return "bad_or_non_book_title"
    if not book.publisher_name:
        return "missing_publisher"
    if not book.authors:
        return "missing_author"
    if not book.price:
        return "missing_or_abnormal_price"
    return ""


def score_book(book: SourceBook) -> int:
    score = 0
    for value in [book.title, book.publisher_name, book.price, book.publish_date, book.page_count, book.series, book.source_category]:
        if value:
            score += 1
    score += min(len(book.authors), 3)
    score += min(len(book.translators), 2)
    if book.source_kind in {"xlsx", "xlsm", "xls"}:
        score += 2
    return score


def dedupe_books(books: list[SourceBook]) -> tuple[list[SourceBook], list[dict[str, str]]]:
    accepted_by_isbn: dict[str, SourceBook] = {}
    rejected: list[dict[str, str]] = []
    for book in books:
        reason = rejection_reason(book)
        if reason:
            rejected.append(rejected_row(book, reason))
            continue
        existing = accepted_by_isbn.get(book.isbn)
        if existing is None:
            accepted_by_isbn[book.isbn] = book
        elif score_book(book) > score_book(existing):
            rejected.append(rejected_row(existing, "duplicate_replaced_by_better_source"))
            accepted_by_isbn[book.isbn] = book
        else:
            rejected.append(rejected_row(book, "duplicate_isbn_lower_quality"))
    return sorted(accepted_by_isbn.values(), key=lambda b: (b.publisher_name, b.title, b.isbn)), rejected


def rejected_row(book: SourceBook, reason: str) -> dict[str, str]:
    return {
        "reason": reason,
        "isbn": book.isbn,
        "title": book.title,
        "publisher_name": book.publisher_name,
        "price": book.price,
        "source_category": book.source_category,
        "source_file": book.source_file,
        "source_url": book.source_url,
        "source_kind": book.source_kind,
    }


def classify(book: SourceBook) -> tuple[str, str]:
    text = " ".join([book.title, book.subtitle, book.series, book.source_category, book.publisher_name]).lower()
    def has(*keywords: str) -> bool:
        return any(keyword.lower() in text for keyword in keywords)
    if book.publisher_name in {"法律出版社", "中国民主法制出版社"} or has("法律", "法学", "法典", "法规", "司法", "中国法律"):
        return "图书 > 法律政务 > 法律法规", "law publisher/category/title"
    if has("党政", "马克思", "毛泽东", "习近平", "政治理论", "思政", "社会主义"):
        return "图书 > 法律政务 > 党政读物", "political theory keywords"
    if has("教材", "高等教育", "本科", "高职", "职业教育", "课程", "教学", "教辅"):
        if has("高职", "高等职业", "中职"):
            return "图书 > 教材教辅 > 高职高专教材", "vocational textbook keywords"
        return "图书 > 教材教辅 > 大学教材", "textbook keywords"
    if book.publisher_name == "人民卫生出版社" or has("医学", "西医", "临床", "内科学", "外科学", "护理", "口腔", "影像", "卫生"):
        return "图书 > 医学卫生 > 西医", "medical keywords"
    if has("中医", "药学", "药物", "本草"):
        return "图书 > 医学卫生 > 中医药学", "traditional medicine/pharmacy keywords"
    if has("健康", "养生", "科普健康"):
        return "图书 > 医学卫生 > 健康科普", "health keywords"
    if has("计算机", "python", "java", "javascript", "deepseek", "人工智能", "数据", "软件", "电子", "网络", "编程", "算法"):
        return "图书 > 科技工程 > 计算机与电子", "computer/electronics keywords"
    if has("数学", "物理", "化学", "统计", "几何", "微积分", "力学"):
        return "图书 > 科技工程 > 数学物理", "science keywords"
    if has("建筑", "土木", "工程造价", "结构"):
        return "图书 > 科技工程 > 建筑工程", "architecture keywords"
    if has("农林", "植物", "畜牧", "农业"):
        return "图书 > 科技工程 > 农林科学", "agriculture keywords"
    if has("机械", "工业", "自动化", "电工", "制造", "材料"):
        return "图书 > 科技工程 > 工业技术", "industrial keywords"
    if has("英语", "日语", "法语", "德语", "韩语", "俄语", "西班牙语", "外语", "语种"):
        if has("日语", "法语", "德语", "韩语", "俄语", "西班牙语", "葡萄牙语"):
            return "图书 > 语言工具 > 小语种", "language keyword"
        return "图书 > 语言工具 > 外语学习", "foreign language keyword"
    if has("字典", "词典", "辞典", "百科", "工具书"):
        if has("汉字", "汉语", "古汉语"):
            return "图书 > 语言工具 > 汉语工具书", "Chinese reference keyword"
        return "图书 > 语言工具 > 辞书百科", "dictionary keyword"
    if has("古籍", "古代", "中华书局", "整理", "点校", "文献", "档案", "图书馆"):
        if has("图书馆", "档案", "书目"):
            return "图书 > 古籍文献 > 文献档案", "archives/library keywords"
        return "图书 > 古籍文献 > 古籍整理", "ancient texts keywords"
    if has("历史", "中国史", "世界史", "考古", "文物", "传记", "年谱", "史"):
        return "图书 > 人文社科 > 历史考古", "history keywords"
    if has("哲学", "宗教", "伦理", "康德", "道德经", "美学"):
        return "图书 > 人文社科 > 哲学宗教", "philosophy/religion keywords"
    if has("社会学", "社会科学", "心理", "民族", "人类学"):
        return "图书 > 人文社科 > 社会科学", "social science keywords"
    if has("教育", "新闻", "传播", "出版", "编辑", "新媒体"):
        return "图书 > 人文社科 > 教育新闻传播", "education/media keywords"
    if has("文化", "国学", "传统文化", "中国文化"):
        return "图书 > 人文社科 > 文化国学", "culture keywords"
    if has("文学", "小说", "诗", "散文", "鲁迅", "作文", "中国文学"):
        return "图书 > 文学艺术 > 小说散文诗歌", "literature keywords"
    if has("艺术", "美术", "绘画", "书法", "设计", "摄影", "影视", "音乐", "舞蹈"):
        if has("音乐", "舞蹈", "影视", "电影"):
            return "图书 > 文学艺术 > 音乐影视", "music/film keywords"
        if has("书法", "绘画", "美术"):
            return "图书 > 文学艺术 > 书法绘画", "painting/calligraphy keywords"
        return "图书 > 文学艺术 > 艺术设计", "art keywords"
    if has("儿童", "少儿", "绘本", "少年", "启蒙"):
        if has("科普", "百科"):
            return "图书 > 少儿童书 > 少儿科普", "children science keywords"
        if has("绘本", "启蒙"):
            return "图书 > 少儿童书 > 启蒙绘本", "picture book keywords"
        return "图书 > 少儿童书 > 儿童文学", "children keywords"
    if has("经济", "金融", "投资", "财政", "贸易"):
        return "图书 > 经济管理 > 经济金融", "economics keywords"
    if has("管理", "企业", "战略", "组织", "领导"):
        return "图书 > 经济管理 > 工商管理", "management keywords"
    if has("会计", "营销", "财务", "审计"):
        return "图书 > 经济管理 > 会计营销", "accounting/marketing keywords"
    if has("旅游", "地理", "地图"):
        return "图书 > 生活休闲 > 旅游地理", "travel/geography keywords"
    if has("健身", "运动", "体育", "拉伸"):
        return "图书 > 生活休闲 > 运动健身", "sports keywords"
    if has("生活", "美食", "烹饪", "家居"):
        return "图书 > 生活休闲 > 生活美育", "lifestyle keywords"
    return "图书 > 综合图书 > 综合读物", "fallback from source corpus"


def build_categories() -> tuple[list[dict[str, str]], dict[str, str]]:
    rows: list[dict[str, str]] = []
    path_to_id: dict[str, str] = {}
    def add(name: str, parent_id: str, path: str) -> str:
        cid = str(len(rows) + 1)
        rows.append({"category_id": cid, "category_name": name, "parent_category_id": parent_id})
        path_to_id[path] = cid
        return cid
    for root, seconds in BOOK_CATEGORY_TREE.items():
        root_id = add(root, "", root)
        for second, leaves in seconds.items():
            second_path = f"{root} > {second}"
            second_id = add(second, root_id, second_path)
            for leaf in leaves:
                add(leaf, second_id, f"{second_path} > {leaf}")
    return rows, path_to_id


def write_csv(path: Path, rows: list[dict[str, Any]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def source_book_row(book: SourceBook) -> dict[str, Any]:
    return {
        "isbn": book.isbn,
        "title": book.title,
        "subtitle": book.subtitle,
        "authors": "|".join(book.authors),
        "translators": "|".join(book.translators),
        "publisher_name": book.publisher_name,
        "publish_date": book.publish_date,
        "price": book.price,
        "page_count": book.page_count,
        "edition": book.edition,
        "series": book.series,
        "source_category": book.source_category,
        "source_name": book.source_name,
        "source_file": book.source_file,
        "source_url": book.source_url,
        "source_kind": book.source_kind,
        "raw_row_hash": book.raw_row_hash,
        "category_path": book.category_path,
        "category_reason": book.category_reason,
    }


def publisher_profile(name: str) -> dict[str, str]:
    profile = PUBLISHER_PROFILES.get(name, {"website": "", "contact_name": "发行部"})
    return {
        "contact_name": profile.get("contact_name", "发行部") or "发行部",
        "phone": profile.get("phone", "见官网") or "见官网",
        "email": profile.get("email", "见官网") or "见官网",
        "address": profile.get("address", "见官网") or "见官网",
        "website": profile.get("website", "") or PUBLISHER_WEBSITES.get(name, ""),
    }


SEED_SUPPLIERS = [
    {"supplier_id": "1", "supplier_name": "北京人天书店集团股份有限公司", "contact_name": "馆配业务部", "phone": "合同约定", "email": "supplier01@example.local", "status": "active"},
    {"supplier_id": "2", "supplier_name": "湖北三新文化传媒有限公司", "contact_name": "馆配业务部", "phone": "合同约定", "email": "supplier02@example.local", "status": "active"},
    {"supplier_id": "3", "supplier_name": "浙江省新华书店集团馆藏图书有限公司", "contact_name": "馆配业务部", "phone": "合同约定", "email": "supplier03@example.local", "status": "active"},
    {"supplier_id": "4", "supplier_name": "江苏凤凰新华书店集团有限公司", "contact_name": "发行采购部", "phone": "合同约定", "email": "supplier04@example.local", "status": "active"},
    {"supplier_id": "5", "supplier_name": "上海新华传媒连锁有限公司", "contact_name": "发行采购部", "phone": "合同约定", "email": "supplier05@example.local", "status": "active"},
    {"supplier_id": "6", "supplier_name": "中国图书进出口（集团）有限公司", "contact_name": "发行采购部", "phone": "合同约定", "email": "supplier06@example.local", "status": "active"},
    {"supplier_id": "7", "supplier_name": "高等教育出版社直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier07@example.local", "status": "active"},
    {"supplier_id": "8", "supplier_name": "清华大学出版社直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier08@example.local", "status": "active"},
    {"supplier_id": "9", "supplier_name": "人民邮电出版社直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier09@example.local", "status": "active"},
    {"supplier_id": "10", "supplier_name": "商务印书馆直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier10@example.local", "status": "active"},
    {"supplier_id": "11", "supplier_name": "中国人民大学出版社直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier11@example.local", "status": "active"},
    {"supplier_id": "12", "supplier_name": "复旦大学出版社直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier12@example.local", "status": "active"},
    {"supplier_id": "13", "supplier_name": "生活·读书·新知三联书店直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier13@example.local", "status": "active"},
    {"supplier_id": "14", "supplier_name": "人民卫生出版社直供", "contact_name": "发行部", "phone": "见出版社官网", "email": "supplier14@example.local", "status": "active"},
]

DIRECT_SUPPLIER_BY_PUBLISHER = {
    "高等教育出版社": "7",
    "清华大学出版社": "8",
    "人民邮电出版社": "9",
    "商务印书馆": "10",
    "中国人民大学出版社": "11",
    "复旦大学出版社": "12",
    "生活·读书·新知三联书店": "13",
    "人民卫生出版社": "14",
}


def supplier_for_book(book: SourceBook) -> str:
    direct = DIRECT_SUPPLIER_BY_PUBLISHER.get(book.publisher_name)
    if direct:
        return direct
    if any(keyword in book.category_path for keyword in ["外语学习", "小语种", "辞书百科"]):
        return "6"
    distributor_ids = ["1", "2", "3", "4", "5"]
    return distributor_ids[stable_int(book.publisher_name + book.isbn, len(distributor_ids))]


def build_sql_data(books: list[SourceBook]) -> dict[str, list[dict[str, Any]]]:
    category_rows, category_path_to_id = build_categories()
    for book in books:
        book.category_path, book.category_reason = classify(book)
    publisher_names = sorted({book.publisher_name for book in books})
    publisher_id = {name: str(i + 1) for i, name in enumerate(publisher_names)}
    publishers = [
        {
            "publisher_id": publisher_id[name],
            "publisher_name": name,
            "contact_name": publisher_profile(name)["contact_name"],
            "phone": publisher_profile(name)["phone"],
            "email": publisher_profile(name)["email"],
            "address": publisher_profile(name)["address"],
            "country": "中国",
            "website": publisher_profile(name)["website"],
        }
        for name in publisher_names
    ]
    suppliers = SEED_SUPPLIERS
    author_names = sorted({person for book in books for person in book.authors})
    translator_names = sorted({person for book in books for person in book.translators})
    author_id = {name: str(i + 1) for i, name in enumerate(author_names)}
    translator_id = {name: str(i + 1) for i, name in enumerate(translator_names)}
    products: list[dict[str, Any]] = []
    book_rows: list[dict[str, Any]] = []
    book_authors: list[dict[str, Any]] = []
    book_translators: list[dict[str, Any]] = []
    supplier_products: list[dict[str, Any]] = []
    inventory: list[dict[str, Any]] = []
    stores = seed_stores()
    for index, book in enumerate(books, start=1):
        pid = str(index)
        unit_price = Decimal(book.price)
        cost_ratio = Decimal("0.58") + Decimal(stable_int(book.isbn, 1800)) / Decimal("10000")
        cost_price = quantize_money(unit_price * cost_ratio)
        products.append(
            {
                "product_id": pid,
                "product_name": book.title,
                "category_id": category_path_to_id[book.category_path],
                "unit": "本",
                "unit_price": book.price,
                "cost_price": cost_price,
                "barcode": book.isbn,
                "status": "onsale",
            }
        )
        book_rows.append(
            {
                "product_id": pid,
                "isbn": book.isbn,
                "publisher_id": publisher_id[book.publisher_name],
                "publish_date": book.publish_date,
                "edition": book.edition[:20],
                "language": "中文",
                "page_count": book.page_count,
            }
        )
        for order, name in enumerate(book.authors, start=1):
            book_authors.append({"product_id": pid, "author_id": author_id[name], "author_order": str(order)})
        for name in book.translators:
            book_translators.append({"product_id": pid, "translator_id": translator_id[name]})
        supplier_products.append(
            {
                "supplier_id": supplier_for_book(book),
                "product_id": pid,
                "supply_price": cost_price,
                "min_order_qty": str([3, 5, 10, 20][stable_int(book.isbn + "moq", 4)]),
                "is_primary": "1",
            }
        )
        # Keep inventory realistic but not explosive: each title appears in two deterministic stores.
        first_store = stable_int(book.isbn + "store", len(stores))
        store_indices = {first_store, (first_store + 2) % len(stores)}
        for store_index in sorted(store_indices):
            store = stores[store_index]
            inventory.append(
                {
                    "store_id": store["store_id"],
                    "product_id": pid,
                    "stock_qty": str(1 + stable_int(book.isbn + store["store_id"], 25)),
                    "safety_stock_qty": str(1 + stable_int(book.isbn + "safe" + store["store_id"], 5)),
                }
            )
    return {
        "store": stores,
        "supplier": suppliers,
        "category": category_rows,
        "publisher": publishers,
        "product": products,
        "book": book_rows,
        "author": [{"author_id": author_id[name], "author_name": name, "country": ""} for name in author_names],
        "translator": [{"translator_id": translator_id[name], "translator_name": name, "country": ""} for name in translator_names],
        "book_author": book_authors,
        "book_translator": book_translators,
        "supplier_product": supplier_products,
        "customer": [],
        "member": [],
        "system_user": seed_users(),
        "role": seed_roles(),
        "permission": seed_permissions(),
        "user_role": [{"user_id": "1", "role_id": "1"}, {"user_id": "2", "role_id": "2"}, {"user_id": "3", "role_id": "3"}],
        "role_permission": seed_role_permissions(),
        "purchase_order": [],
        "purchase_order_item": [],
        "stock_in": [],
        "stock_in_item": [],
        "inventory": inventory,
        "sale": [],
        "sale_item": [],
    }


def seed_stores() -> list[dict[str, str]]:
    return [
        {"store_id": "1", "store_name": "上海五角场店", "city": "上海", "address": "上海市杨浦区邯郸路220号", "phone": "021-55660001", "manager_name": "陈明"},
        {"store_id": "2", "store_name": "北京中关村店", "city": "北京", "address": "北京市海淀区中关村大街1号", "phone": "010-62550002", "manager_name": "刘洁"},
        {"store_id": "3", "store_name": "广州天河店", "city": "广州", "address": "广州市天河区天河路208号", "phone": "020-38880003", "manager_name": "周洋"},
        {"store_id": "4", "store_name": "南京新街口店", "city": "南京", "address": "南京市秦淮区中山南路89号", "phone": "025-84720004", "manager_name": "王宁"},
        {"store_id": "5", "store_name": "成都春熙路店", "city": "成都", "address": "成都市锦江区春熙路18号", "phone": "028-86660005", "manager_name": "赵琳"},
    ]


def seed_users() -> list[dict[str, str]]:
    return [
        {"user_id": "1", "username": "admin", "password_hash": "demo-only-hash-admin", "real_name": "管理员", "phone": "13900000001", "email": "admin@example.local", "status": "active"},
        {"user_id": "2", "username": "operator", "password_hash": "demo-only-hash-operator", "real_name": "门店操作员", "phone": "13900000002", "email": "operator@example.local", "status": "active"},
        {"user_id": "3", "username": "viewer", "password_hash": "demo-only-hash-viewer", "real_name": "查询用户", "phone": "13900000003", "email": "viewer@example.local", "status": "active"},
    ]


def seed_roles() -> list[dict[str, str]]:
    return [
        {"role_id": "1", "role_name": "admin", "role_desc": "系统管理员"},
        {"role_id": "2", "role_name": "operator", "role_desc": "门店操作员"},
        {"role_id": "3", "role_name": "viewer", "role_desc": "查询用户"},
    ]


def seed_permissions() -> list[dict[str, str]]:
    codes = [
        ("1", "catalog:read", "查看商品", "catalog"),
        ("2", "catalog:write", "维护商品", "catalog"),
        ("3", "inventory:read", "查看库存", "inventory"),
        ("4", "inventory:write", "维护库存", "inventory"),
        ("5", "sales:read", "查看销售", "sales"),
        ("6", "procurement:read", "查看采购", "procurement"),
        ("7", "analytics:read", "查看分析", "analytics"),
    ]
    return [{"permission_id": a, "permission_code": b, "permission_name": c, "module_name": d} for a, b, c, d in codes]


def seed_role_permissions() -> list[dict[str, str]]:
    rows = []
    for permission_id in range(1, 8):
        rows.append({"role_id": "1", "permission_id": str(permission_id)})
    for permission_id in [1, 3, 5, 6, 7]:
        rows.append({"role_id": "2", "permission_id": str(permission_id)})
    for permission_id in [1, 3, 5, 7]:
        rows.append({"role_id": "3", "permission_id": str(permission_id)})
    return rows


def write_sql_csvs(tables: dict[str, list[dict[str, Any]]]) -> None:
    for table, headers in CSV_HEADERS.items():
        write_csv(SQL_DATA_DIR / f"{table}.csv", tables.get(table, []), headers)


def write_outputs(source_books: list[SourceBook], accepted: list[SourceBook], rejected: list[dict[str, str]], audits: list[dict[str, Any]], tables: dict[str, list[dict[str, Any]]]) -> None:
    source_headers = [
        "isbn",
        "title",
        "subtitle",
        "authors",
        "translators",
        "publisher_name",
        "publish_date",
        "price",
        "page_count",
        "edition",
        "series",
        "source_category",
        "source_name",
        "source_file",
        "source_url",
        "source_kind",
        "raw_row_hash",
        "category_path",
        "category_reason",
    ]
    write_csv(SOURCE_CSV, [source_book_row(book) for book in source_books], source_headers)
    write_csv(ACCEPTED_CSV, [source_book_row(book) for book in accepted], source_headers)
    write_csv(REJECTED_CSV, rejected, ["reason", "isbn", "title", "publisher_name", "price", "source_category", "source_file", "source_url", "source_kind"])
    write_csv(SOURCE_AUDIT_CSV, audits, ["source", "kind", "rows", "accepted_like", "status", "notes"])
    write_csv(
        CATEGORY_AUDIT_CSV,
        [
            {"isbn": book.isbn, "title": book.title, "source_category": book.source_category, "category_path": book.category_path, "reason": book.category_reason}
            for book in accepted
        ],
        ["isbn", "title", "source_category", "category_path", "reason"],
    )
    write_report(source_books, accepted, rejected, audits, tables)


def write_report(source_books: list[SourceBook], accepted: list[SourceBook], rejected: list[dict[str, str]], audits: list[dict[str, Any]], tables: dict[str, list[dict[str, Any]]]) -> None:
    publisher_counts = Counter(book.publisher_name for book in accepted)
    category_counts = Counter(book.category_path for book in accepted)
    source_kind_counts = Counter(book.source_kind for book in accepted)
    reject_counts = Counter(row["reason"] for row in rejected)
    author_missing = sum(1 for book in accepted if not book.authors)
    page_missing = sum(1 for book in accepted if not book.page_count)
    date_missing = sum(1 for book in accepted if not book.publish_date)
    def pct(num: int, den: int) -> str:
        return "0.00%" if den == 0 else f"{num / den * 100:.2f}%"
    with REPORT_MD.open("w", encoding="utf-8", newline="\n") as file:
        file.write("# 干净图书数据体系重建报告\n\n")
        file.write(f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}\n")
        file.write(f"- 原始候选记录：{len(source_books)}\n")
        file.write(f"- ISBN 去重后有效图书：{len(accepted)}\n")
        file.write(f"- 拒绝/低质量记录：{len(rejected)}\n")
        file.write(f"- 出版社数量：{len(publisher_counts)}\n")
        file.write(f"- 作者数量：{len(tables['author'])}\n")
        file.write(f"- 译者数量：{len(tables['translator'])}\n")
        file.write("- 已丢弃当当网来源及旧非书商品分类；销售、会员、采购、入库明细清为表头，后续可基于新商品重新生成。\n\n")
        file.write("## 来源文件处理\n\n| 来源 | 类型 | 扫描行 | 候选记录 | 状态 | 备注 |\n|---|---|---:|---:|---|---|\n")
        for row in audits:
            file.write(f"| {row['source']} | {row['kind']} | {row['rows']} | {row['accepted_like']} | {row['status']} | {row['notes']} |\n")
        file.write("\n## 入库来源类型\n\n| 类型 | 数量 |\n|---|---:|\n")
        for key, count in source_kind_counts.most_common():
            file.write(f"| {key} | {count} |\n")
        file.write("\n## 出版社分布 Top 30\n\n| 出版社 | 数量 |\n|---|---:|\n")
        for key, count in publisher_counts.most_common(30):
            file.write(f"| {key} | {count} |\n")
        file.write("\n## 分类分布\n\n| 分类路径 | 数量 |\n|---|---:|\n")
        for key, count in category_counts.most_common():
            file.write(f"| {key} | {count} |\n")
        file.write("\n## 拒绝原因\n\n| 原因 | 数量 |\n|---|---:|\n")
        for key, count in reject_counts.most_common():
            file.write(f"| {key} | {count} |\n")
        file.write("\n## 字段缺失率\n\n| 字段 | 缺失数 | 缺失率 |\n|---|---:|---:|\n")
        file.write(f"| authors | {author_missing} | {pct(author_missing, len(accepted))} |\n")
        file.write(f"| publish_date | {date_missing} | {pct(date_missing, len(accepted))} |\n")
        file.write(f"| page_count | {page_missing} | {pct(page_missing, len(accepted))} |\n")
        file.write("\n## SQL CSV 行数\n\n| 表 | 行数 |\n|---|---:|\n")
        for table in CSV_HEADERS:
            file.write(f"| {table} | {len(tables.get(table, []))} |\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild clean bookstore seed CSVs from publisher catalogs.")
    parser.add_argument("--crawl-web", action="store_true", help="Crawl China Publishing Group and SDX web pages.")
    parser.add_argument("--cnpubg-max-lists", type=int, default=0, help="Limit CNPubG book list pages; 0 means all discovered 2020-2026 lists.")
    parser.add_argument("--sanlian-pages", type=int, default=323, help="Number of SDX list pages to crawl; each page has about 30 detail links.")
    parser.add_argument("--sanlian-workers", type=int, default=8, help="Concurrent workers for SDX detail pages.")
    parser.add_argument("--sanlian-cache-only", action="store_true", help="Parse only cached SDX pages and skip uncached network requests.")
    parser.add_argument("--sanlian-stop-after-list-errors", type=int, default=20, help="Stop SDX list crawling after this many consecutive missing/failed list pages.")
    parser.add_argument("--dry-run", action="store_true", help="Build clean intermediates but do not overwrite sql/data.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_books, audits = collect_sources(args)
    accepted, rejected = dedupe_books(source_books)
    for book in accepted:
        book.category_path, book.category_reason = classify(book)
    tables = build_sql_data(accepted)
    write_outputs(source_books, accepted, rejected, audits, tables)
    if not args.dry_run:
        write_sql_csvs(tables)
    print(f"source_candidates={len(source_books)} accepted={len(accepted)} rejected={len(rejected)}")
    print(f"publishers={len(tables['publisher'])} authors={len(tables['author'])} translators={len(tables['translator'])}")
    print(f"wrote {SOURCE_CSV}")
    if not args.dry_run:
        print(f"rewrote sql/data/*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
