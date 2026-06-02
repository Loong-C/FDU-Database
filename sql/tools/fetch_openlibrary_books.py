#!/usr/bin/env python
"""Fetch Open Library book metadata for seed data generation."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SQL_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = SQL_DIR / "source"
OUTPUT_PATH = SOURCE_DIR / "books_openlibrary.csv"
SEARCH_URL = "https://openlibrary.org/search.json"
CURRENT_YEAR = 2026
FIELDS = [
    "key",
    "title",
    "author_name",
    "publisher",
    "first_publish_year",
    "publish_year",
    "publish_date",
    "number_of_pages_median",
    "language",
    "isbn",
]
CSV_FIELDS = [
    "source_query_category",
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
    "openlibrary_key",
]
QUERY_SPECS = [
    ("数据库", "subject:database"),
    ("编程语言", "subject:programming"),
    ("编程语言", "subject:programming languages"),
    ("人工智能", "subject:artificial intelligence"),
    ("人工智能", "subject:machine learning"),
    ("算法与数据结构", "subject:algorithms"),
    ("算法与数据结构", "subject:data structures"),
    ("操作系统与网络", "subject:operating systems"),
    ("操作系统与网络", "subject:computer networks"),
    ("软件工程", "subject:software engineering"),
    ("软件工程", "subject:software"),
    ("数学", "subject:mathematics"),
    ("科学技术", "subject:science"),
    ("科学技术", "subject:engineering"),
    ("文学", "subject:fiction"),
    ("文学", "subject:literature"),
    ("文学", "subject:novel"),
    ("文学", "subject:poetry"),
    ("文学", "subject:drama"),
    ("文学", "subject:mystery"),
    ("文学", "subject:fantasy"),
    ("文学", "subject:romance"),
    ("文学", "subject:adventure"),
    ("文学", "subject:short stories"),
    ("图书", "subject:history"),
    ("教育", "subject:education"),
    ("经济管理", "subject:business"),
    ("经济管理", "subject:economics"),
    ("医学健康", "subject:medicine"),
    ("心理哲学", "subject:psychology"),
    ("心理哲学", "subject:philosophy"),
    ("传记", "subject:biography"),
    ("计算机", "subject:computer science"),
    ("计算机", "subject:computers"),
]


def clean_text(value: object, max_length: int | None = None) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFC", text)
    text = "".join(
        " " if char in "\r\n\t" else char
        for char in text
        if unicodedata.category(char)[0] != "C" or char in "\r\n\t"
    )
    text = re.sub(r"\s+", " ", text).strip()
    if max_length is not None:
        text = text[:max_length].strip()
    return text


def valid_isbn10(value: str) -> bool:
    if len(value) != 10 or not re.fullmatch(r"\d{9}[\dXx]", value):
        return False
    total = 0
    for index, char in enumerate(value.upper(), start=1):
        digit = 10 if char == "X" else int(char)
        total += index * digit
    return total % 11 == 0


def valid_isbn13(value: str) -> bool:
    if len(value) != 13 or not value.isdigit():
        return False
    total = sum((1 if index % 2 == 0 else 3) * int(char) for index, char in enumerate(value[:12]))
    check_digit = (10 - total % 10) % 10
    return check_digit == int(value[-1])


def isbn10_to_isbn13(value: str) -> str:
    stem = "978" + value[:9]
    total = sum((1 if index % 2 == 0 else 3) * int(char) for index, char in enumerate(stem))
    return stem + str((10 - total % 10) % 10)


def normalize_isbn(raw_values: object, seen_isbns: set[str]) -> str:
    values = raw_values if isinstance(raw_values, list) else [raw_values]
    candidates: list[str] = []
    for raw_value in values:
        value = re.sub(r"[^0-9Xx]", "", str(raw_value or ""))
        if len(value) == 13 and valid_isbn13(value):
            candidates.append(value)
        elif len(value) == 10 and valid_isbn10(value):
            candidates.append(isbn10_to_isbn13(value.upper()))
    for candidate in candidates:
        if candidate not in seen_isbns:
            return candidate
    return ""


def first_list_value(value: object) -> object:
    if isinstance(value, list):
        return value[0] if value else ""
    return value


def parse_year(doc: dict[str, object]) -> int | None:
    values: list[object] = []
    if doc.get("first_publish_year"):
        values.append(doc["first_publish_year"])
    publish_year = doc.get("publish_year")
    if isinstance(publish_year, list):
        values.extend(publish_year)
    elif publish_year:
        values.append(publish_year)
    for value in values:
        match = re.search(r"\d{4}", str(value))
        if match:
            year = int(match.group(0))
            if 1000 <= year <= CURRENT_YEAR:
                return year
    return None


def parse_page_count(value: object) -> str:
    try:
        count = int(first_list_value(value))
    except (TypeError, ValueError):
        return ""
    return str(count) if 0 < count <= 5000 else ""


def parse_languages(value: object) -> str:
    values = value if isinstance(value, list) else [value]
    languages = [clean_text(item, 10) for item in values if clean_text(item, 10)]
    return ",".join(languages[:3])[:30]


def suggested_price(isbn: str, category_name: str) -> str:
    seed = sum(int(char) for char in isbn if char.isdigit())
    base = {
        "数据库": Decimal("89.00"),
        "编程语言": Decimal("79.00"),
        "软件工程": Decimal("82.00"),
        "人工智能": Decimal("92.00"),
        "算法与数据结构": Decimal("85.00"),
        "操作系统与网络": Decimal("88.00"),
        "计算机": Decimal("79.00"),
        "数学": Decimal("69.00"),
        "科学技术": Decimal("59.00"),
        "经济管理": Decimal("58.00"),
        "历史社科": Decimal("52.00"),
        "医学健康": Decimal("65.00"),
        "心理哲学": Decimal("49.00"),
        "教育": Decimal("45.00"),
        "传记": Decimal("48.00"),
        "文学": Decimal("39.00"),
    }.get(category_name, Decimal("49.00"))
    increment = Decimal(seed % 45)
    value = base + increment
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def status_for_isbn(isbn: str) -> str:
    seed = sum(int(char) for char in isbn if char.isdigit())
    if seed % 29 == 0:
        return "discontinued"
    if seed % 11 == 0:
        return "offsale"
    return "onsale"


def row_from_doc(category_name: str, doc: dict[str, object], seen_isbns: set[str]) -> dict[str, str] | None:
    isbn = normalize_isbn(doc.get("isbn"), seen_isbns)
    if not isbn:
        return None

    title = clean_text(doc.get("title"), 200)
    if not title:
        return None

    author_values = doc.get("author_name")
    authors = author_values if isinstance(author_values, list) else [author_values]
    author_names = []
    for author in authors:
        author_name = clean_text(author, 100)
        if author_name and author_name not in author_names:
            author_names.append(author_name)
    if not author_names:
        return None

    publisher_values = doc.get("publisher")
    publishers = publisher_values if isinstance(publisher_values, list) else [publisher_values]
    publisher = next((clean_text(item, 150) for item in publishers if clean_text(item, 150)), "")
    if not publisher:
        publisher = "Unknown Publisher"

    year = parse_year(doc)
    return {
        "source_query_category": category_name,
        "title": title,
        "isbn": isbn,
        "authors": "; ".join(author_names[:4]),
        "publisher": publisher,
        "publish_year": str(year or ""),
        "publish_date_raw": f"{year}-01-01" if year else "",
        "page_count": parse_page_count(doc.get("number_of_pages_median")),
        "language": parse_languages(doc.get("language")),
        "category_name": category_name,
        "unit": "本",
        "suggested_unit_price": suggested_price(isbn, category_name),
        "status": status_for_isbn(isbn),
        "openlibrary_key": clean_text(doc.get("key"), 80),
    }


def fetch_json(query: str, page: int, page_size: int, user_agent: str, timeout: float) -> dict[str, object]:
    params = {
        "q": query,
        "fields": ",".join(FIELDS),
        "limit": page_size,
        "page": page,
    }
    url = f"{SEARCH_URL}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def read_existing_rows(path: Path, target: int) -> list[dict[str, str]]:
    if not path.exists():
        return []

    rows: list[dict[str, str]] = []
    seen_isbns: set[str] = set()
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            isbn = clean_text(row.get("isbn"))
            if not isbn or isbn in seen_isbns:
                continue
            rows.append({field: row.get(field, "") for field in CSV_FIELDS})
            seen_isbns.add(isbn)
            if len(rows) >= target:
                break
    return rows


def fetch_rows(
    target: int,
    page_size: int,
    sleep_seconds: float,
    max_pages_per_query: int,
    timeout: float,
    retries: int,
    initial_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = list(initial_rows or [])
    seen_isbns = {row["isbn"] for row in rows if row.get("isbn")}
    for category_name, query in QUERY_SPECS:
        if len(rows) >= target:
            break
        print(f"query={query!r}, category={category_name}, collected={len(rows)}")
        for page in range(1, max_pages_per_query + 1):
            if len(rows) >= target:
                break
            payload: dict[str, object] | None = None
            for attempt in range(1, retries + 1):
                try:
                    payload = fetch_json(
                        query=query,
                        page=page,
                        page_size=page_size,
                        user_agent="FDU-Database-SeedData/1.0 (educational course project)",
                        timeout=timeout,
                    )
                    break
                except (HTTPError, URLError, TimeoutError, IncompleteRead, json.JSONDecodeError) as exc:
                    print(f"  page={page} attempt={attempt} failed: {exc}")
                    time.sleep(max(sleep_seconds * 3, 1.0))
            if payload is None:
                continue

            docs = payload.get("docs") or []
            if not isinstance(docs, list) or not docs:
                break

            accepted = 0
            for doc in docs:
                if not isinstance(doc, dict):
                    continue
                row = row_from_doc(category_name, doc, seen_isbns)
                if row is None:
                    continue
                seen_isbns.add(row["isbn"])
                rows.append(row)
                accepted += 1
                if len(rows) >= target:
                    break

            print(f"  page={page}, docs={len(docs)}, accepted={accepted}, collected={len(rows)}")
            num_found = int(payload.get("numFound") or payload.get("num_found") or 0)
            start = int(payload.get("start") or (page - 1) * page_size)
            if num_found and start + len(docs) >= num_found:
                break
            time.sleep(sleep_seconds)
    return rows


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=int, default=10000, help="minimum number of source rows to collect")
    parser.add_argument("--page-size", type=int, default=100, help="Open Library search page size")
    parser.add_argument("--sleep", type=float, default=0.4, help="seconds to wait between successful requests")
    parser.add_argument("--max-pages-per-query", type=int, default=80)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--replace", action="store_true", help="ignore existing output rows instead of preserving them")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    initial_rows = [] if args.replace else read_existing_rows(args.output, args.target)
    if initial_rows:
        print(f"preserved {len(initial_rows)} existing rows from {args.output}")
    rows = fetch_rows(
        target=args.target,
        page_size=args.page_size,
        sleep_seconds=args.sleep,
        max_pages_per_query=args.max_pages_per_query,
        timeout=args.timeout,
        retries=args.retries,
        initial_rows=initial_rows,
    )
    if len(rows) < args.target:
        raise SystemExit(f"Collected {len(rows)} rows, below target {args.target}.")
    write_rows(args.output, rows)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
