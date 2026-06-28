#!/usr/bin/env python
"""Validate normalized CSV seed data before importing it into MySQL."""

from __future__ import annotations

import csv
import re
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
    ("product", "unit"): 20,
    ("book", "isbn"): 20,
    ("book", "language"): 30,
    ("publisher", "publisher_name"): 150,
    ("author", "author_name"): 100,
}

MINIMUM_ROWS = {
    "store": 50,
    "category": 40,
    "publisher": 10,
    "product": 10000,
    "book": 10000,
    "book_author": 10000,
    "inventory": 10000,
}

FORBIDDEN_MARKETING_TERMS = ["当当网", "当当自营", "新华书店", "包邮", "自营", "旗舰店", "点击购买", "已撤销"]

FLAGSHIP_STORE_IDS = {"1", "2", "5", "9", "10", "14", "15", "16", "17", "20", "21", "23", "24", "27", "35", "38"}


def isbn13_check_digit(prefix12: str) -> str:
    total = sum(int(char) * (1 if index % 2 == 0 else 3) for index, char in enumerate(prefix12))
    return str((10 - total % 10) % 10)


def valid_isbn13(value: str) -> bool:
    return (
        len(value) == 13
        and value.isdigit()
        and value[:3] in {"978", "979"}
        and isbn13_check_digit(value[:12]) == value[-1]
    )


def has_forbidden_marketing_text(value: str) -> bool:
    if any(term in value for term in FORBIDDEN_MARKETING_TERMS):
        return True
    return bool(re.search(r"(^|[【\[(（\s])正版([】\])）\s]|$|图书|书籍|教材|现货|包邮|全新)", value))


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


def category_descendant_ids(rows: list[dict[str, str]], root_id: str) -> set[str]:
    children = defaultdict(list)
    for row in rows:
        children[row["parent_category_id"]].append(row["category_id"])
    descendants = {root_id}
    pending = [root_id]
    while pending:
        current = pending.pop()
        for child in children.get(current, []):
            if child not in descendants:
                descendants.add(child)
                pending.append(child)
    return descendants


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
        if data[table]:
            assert max(len(row[column]) for row in data[table]) <= max_length, f"{table}.{column} is too long."

    for table, minimum in MINIMUM_ROWS.items():
        assert len(data[table]) >= minimum, f"{table} needs at least {minimum} seed rows."

    product_lookup = {row["product_id"]: row for row in data["product"]}
    book_product_ids = {row["product_id"] for row in data["book"]}
    nonbook_product_ids = set(product_lookup) - book_product_ids
    book_isbns = [row["isbn"] for row in data["book"]]
    product_barcodes = [row["barcode"] for row in data["product"]]
    authored_product_ids = {row["product_id"] for row in data["book_author"]}
    supplier_emails = [row["email"] for row in data["supplier"]]
    store_phones = [row["phone"] for row in data["store"]]
    stocked_store_ids = {row["store_id"] for row in data["inventory"]}
    category_names = [row["category_name"] for row in data["category"]]
    supplier_by_name = {row["supplier_name"]: row for row in data["supplier"]}
    category_by_name = {row["category_name"]: row for row in data["category"]}
    supplier_links_by_product = defaultdict(set)
    for row in data["supplier_product"]:
        supplier_links_by_product[row["product_id"]].add(row["supplier_id"])
    assert book_product_ids.issubset(product_lookup), "book rows must reference product rows."
    assert nonbook_product_ids, "seed data should include Deli office stationery products."
    assert len(category_names) == len(set(category_names)), "category names must be unique for the current schema."
    assert all(row["language"] == "中文" for row in data["book"]), "book rows must use Chinese mainland seed data."
    assert all(valid_isbn13(row["isbn"]) for row in data["book"]), "book rows must contain valid ISBN-13 values."
    assert all(not row["isbn"].upper().startswith("DD") for row in data["book"]), "Dangdang product codes are not ISBNs."
    assert len(book_isbns) == len(set(book_isbns)), "book rows contain duplicate ISBNs."
    assert all(row["barcode"] for row in data["product"]), "product rows must contain barcodes or source product codes."
    assert len(product_barcodes) == len(set(product_barcodes)), "product rows contain duplicate barcodes."
    assert {product_lookup[row["product_id"]]["barcode"] for row in data["book"]} == {row["isbn"] for row in data["book"]}, "book product barcode must match ISBN."
    deli_supplier = next((row for name, row in supplier_by_name.items() if name.startswith("得力集实")), None)
    assert deli_supplier is not None, "supplier rows must include Deli JSLink."
    assert "办公文具" in category_by_name, "category rows must include office stationery root."
    office_category_ids = category_descendant_ids(data["category"], category_by_name["办公文具"]["category_id"])
    deli_supplier_id = deli_supplier["supplier_id"]
    assert all(product_lookup[pid]["category_id"] in office_category_ids for pid in nonbook_product_ids), "non-book products must be under office stationery categories."
    assert all(product_lookup[pid]["unit"] != "箱" for pid in nonbook_product_ids), "Deli products with unit 箱 must be removed."
    assert all(supplier_links_by_product[pid] == {deli_supplier_id} for pid in nonbook_product_ids), "Deli products must use 得力集实 as their only supplier."
    assert not any(has_forbidden_marketing_text(row["product_name"]) for row in data["product"]), "product names contain marketing noise."
    assert not any(has_forbidden_marketing_text(row["author_name"]) for row in data["author"]), "author names contain marketing noise."
    assert not any(has_forbidden_marketing_text(row["translator_name"]) for row in data["translator"]), "translator names contain marketing noise."
    assert all(row["website"] and row["contact_name"] and row["phone"] and row["email"] for row in data["publisher"]), "publisher contact profiles must be complete."
    assert all(row["contact_name"] and row["phone"] and row["email"] for row in data["supplier"]), "supplier contact profiles must be complete."
    assert len(supplier_emails) == len(set(supplier_emails)), "supplier rows contain duplicate emails."
    assert len(store_phones) == len(set(store_phones)), "store rows contain duplicate phones."
    assert all(row["store_id"] in stocked_store_ids for row in data["store"]), "every store must have inventory rows."
    assert all(row["product_id"] in authored_product_ids for row in data["book"]), "book rows must have at least one author."

    book_inventory_counts = defaultdict(int)
    stockout_count = 0
    warning_count = 0
    for row in data["inventory"]:
        if row["product_id"] in book_product_ids:
            book_inventory_counts[row["store_id"]] += 1
        stock_qty = int(row["stock_qty"])
        safety_stock_qty = int(row["safety_stock_qty"])
        if stock_qty == 0:
            stockout_count += 1
        if stock_qty <= safety_stock_qty:
            warning_count += 1

    for row in data["store"]:
        store_id = row["store_id"]
        book_count = book_inventory_counts[store_id]
        if store_id in FLAGSHIP_STORE_IDS:
            assert 45000 <= book_count <= 70000, f"flagship store {store_id} has {book_count} book SKUs."
        else:
            assert 15000 <= book_count <= 25000, f"standard store {store_id} has {book_count} book SKUs."

    inventory_count = len(data["inventory"])
    assert 0.01 <= stockout_count / inventory_count <= 0.03, "inventory stockout ratio must stay between 1% and 3%."
    assert warning_count / inventory_count <= 0.15, "inventory warning ratio must not exceed 15%."

    print(f"Validated {sum(len(rows) for rows in data.values())} rows across {len(data)} CSV tables.")
    for table in PRIMARY_KEYS:
        print(f"{table}: {len(data[table])}")


if __name__ == "__main__":
    validate_seed_data()
