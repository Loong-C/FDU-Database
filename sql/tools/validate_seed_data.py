#!/usr/bin/env python
"""Validate normalized CSV seed data before importing it into MySQL."""

from __future__ import annotations

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path


SQL_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = SQL_DIR / "data"
LEGACY_DIR = SQL_DIR / "source" / "legacy"

PRIMARY_KEYS = {
    "store": ("store_id",),
    "supplier": ("supplier_id",),
    "category": ("category_id",),
    "publisher": ("publisher_id",),
    "product": ("product_id",),
    "book": ("product_id",),
    "author": ("author_id",),
    "translator": ("translator_id",),
    "book_author": ("product_id", "author_id"),
    "book_translator": ("product_id", "translator_id"),
    "supplier_product": ("supplier_id", "product_id"),
    "customer": ("customer_id",),
    "member": ("customer_id",),
    "system_user": ("user_id",),
    "role": ("role_id",),
    "permission": ("permission_id",),
    "user_role": ("user_id", "role_id"),
    "role_permission": ("role_id", "permission_id"),
    "purchase_order": ("purchase_order_id",),
    "purchase_order_item": ("purchase_order_id", "line_no"),
    "stock_in": ("stock_in_id",),
    "stock_in_item": ("stock_in_id", "line_no"),
    "inventory": ("store_id", "product_id"),
    "sale": ("sale_id",),
    "sale_item": ("sale_id", "line_no"),
}

FOREIGN_KEYS = [
    ("category", ("parent_category_id",), "category", ("category_id",)),
    ("product", ("category_id",), "category", ("category_id",)),
    ("book", ("product_id",), "product", ("product_id",)),
    ("book", ("publisher_id",), "publisher", ("publisher_id",)),
    ("book_author", ("product_id",), "book", ("product_id",)),
    ("book_author", ("author_id",), "author", ("author_id",)),
    ("book_translator", ("product_id",), "book", ("product_id",)),
    ("book_translator", ("translator_id",), "translator", ("translator_id",)),
    ("supplier_product", ("supplier_id",), "supplier", ("supplier_id",)),
    ("supplier_product", ("product_id",), "product", ("product_id",)),
    ("member", ("customer_id",), "customer", ("customer_id",)),
    ("user_role", ("user_id",), "system_user", ("user_id",)),
    ("user_role", ("role_id",), "role", ("role_id",)),
    ("role_permission", ("role_id",), "role", ("role_id",)),
    ("role_permission", ("permission_id",), "permission", ("permission_id",)),
    ("purchase_order", ("supplier_id",), "supplier", ("supplier_id",)),
    ("purchase_order", ("store_id",), "store", ("store_id",)),
    ("purchase_order", ("created_by",), "system_user", ("user_id",)),
    ("purchase_order_item", ("purchase_order_id",), "purchase_order", ("purchase_order_id",)),
    ("purchase_order_item", ("product_id",), "product", ("product_id",)),
    ("stock_in", ("purchase_order_id",), "purchase_order", ("purchase_order_id",)),
    ("stock_in", ("store_id",), "store", ("store_id",)),
    ("stock_in", ("operator_id",), "system_user", ("user_id",)),
    ("stock_in_item", ("stock_in_id",), "stock_in", ("stock_in_id",)),
    ("stock_in_item", ("product_id",), "product", ("product_id",)),
    ("inventory", ("store_id",), "store", ("store_id",)),
    ("inventory", ("product_id",), "product", ("product_id",)),
    ("sale", ("store_id",), "store", ("store_id",)),
    ("sale", ("customer_id",), "customer", ("customer_id",)),
    ("sale_item", ("sale_id",), "sale", ("sale_id",)),
    ("sale_item", ("product_id",), "product", ("product_id",)),
]

MAX_LENGTHS = {
    ("product", "product_name"): 200,
    ("product", "barcode"): 50,
    ("book", "isbn"): 20,
    ("book", "language"): 30,
    ("publisher", "publisher_name"): 150,
    ("author", "author_name"): 100,
}

MINIMUM_ROWS = {
    "product": 10000,
    "book": 10000,
    "book_author": 10000,
    "inventory": 20,
    "sale": 10,
    "sale_item": 20,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def row_ids(data: dict[str, list[dict[str, str]]], table: str, columns: tuple[str, ...]):
    return [tuple(row[column] for column in columns) for row in data[table]]


def line_totals(rows: list[dict[str, str]], key: str) -> dict[str, Decimal]:
    totals = defaultdict(Decimal)
    for row in rows:
        totals[row[key]] += Decimal(row["line_amount"])
    return totals


def validate_seed_data() -> None:
    data = {path.stem: read_csv(path) for path in DATA_DIR.glob("*.csv")}
    assert set(data) == set(PRIMARY_KEYS), "sql/data must contain exactly one CSV for each business table."

    for table, columns in PRIMARY_KEYS.items():
        keys = row_ids(data, table, columns)
        assert len(keys) == len(set(keys)), f"{table} contains duplicate primary keys."

    for table, columns, parent_table, parent_columns in FOREIGN_KEYS:
        parent_ids = set(row_ids(data, parent_table, parent_columns))
        for row in data[table]:
            key = tuple(row[column] for column in columns)
            if all(key) and key not in parent_ids:
                raise AssertionError(f"{table} references missing {parent_table} row {key}.")

    line_specs = [
        ("purchase_order_item", "quantity", "purchase_price"),
        ("stock_in_item", "quantity", "unit_cost"),
        ("sale_item", "quantity", "unit_price"),
    ]
    for table, quantity_column, price_column in line_specs:
        for row in data[table]:
            expected = Decimal(row[quantity_column]) * Decimal(row[price_column])
            assert Decimal(row["line_amount"]) == expected, f"{table} contains an invalid line amount."

    purchase_totals = line_totals(data["purchase_order_item"], "purchase_order_id")
    for row in data["purchase_order"]:
        assert Decimal(row["total_amount"]) == purchase_totals[row["purchase_order_id"]], "Invalid purchase order total."

    sale_totals = line_totals(data["sale_item"], "sale_id")
    for row in data["sale"]:
        assert Decimal(row["total_amount"]) == sale_totals[row["sale_id"]], "Invalid sale total."
        expected = Decimal(row["total_amount"]) - Decimal(row["discount_amount"])
        assert Decimal(row["actual_amount"]) == expected, "Invalid sale actual amount."

    for (table, column), max_length in MAX_LENGTHS.items():
        assert max(len(row[column]) for row in data[table]) <= max_length, f"{table}.{column} is too long."

    for table, minimum in MINIMUM_ROWS.items():
        assert len(data[table]) >= minimum, f"{table} needs at least {minimum} seed rows."

    product_lookup = {row["product_id"]: row for row in data["product"]}
    for path in LEGACY_DIR.glob("*.csv"):
        for row in read_csv(path):
            if "product_id" in row and "product_barcode" in row:
                product = product_lookup[row["product_id"]]
                assert product["barcode"] == row["product_barcode"], f"{path.name} contains a mismatched barcode."
                assert product["product_name"] == row["product_name"], f"{path.name} contains a mismatched product name."

    print(f"Validated {sum(len(rows) for rows in data.values())} rows across {len(data)} CSV tables.")
    for table in PRIMARY_KEYS:
        print(f"{table}: {len(data[table])}")


if __name__ == "__main__":
    validate_seed_data()
