#!/usr/bin/env python
"""Align preserved legacy business rows with the mainland product catalog."""

from __future__ import annotations

import csv
from pathlib import Path


SQL_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = SQL_DIR / "source"
LEGACY_DIR = SOURCE_DIR / "legacy"
BOOK_PRODUCT_ID_START = 120


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def limit_text(value: str, max_length: int) -> str:
    return " ".join(value.split())[:max_length].strip()


def product_metadata() -> dict[str, dict[str, str]]:
    _, rows = read_csv(SOURCE_DIR / "books_mainland.csv")
    metadata: dict[str, dict[str, str]] = {}
    for product_id, row in enumerate(rows, start=BOOK_PRODUCT_ID_START):
        metadata[str(product_id)] = {
            "product_barcode": row["isbn"],
            "product_name": limit_text(row["title"], 200),
        }
    return metadata


def align_legacy_product_columns() -> None:
    metadata = product_metadata()
    total_updates = 0
    for path in sorted(LEGACY_DIR.glob("*.csv")):
        fields, rows = read_csv(path)
        if not {"product_id", "product_barcode", "product_name"}.issubset(fields):
            continue

        updates = 0
        for row in rows:
            replacement = metadata.get(row["product_id"])
            if replacement is None:
                continue
            for column, value in replacement.items():
                if row[column] != value:
                    row[column] = value
                    updates += 1

        if updates:
            write_csv(path, fields, rows)
            total_updates += updates
            print(f"{path}: updated {updates} product metadata cells")

    print(f"Updated {total_updates} legacy product metadata cells.")


if __name__ == "__main__":
    align_legacy_product_columns()
