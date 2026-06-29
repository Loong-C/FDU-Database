#!/usr/bin/env python
"""Rebuild store inventory from the current product, book, category and store CSVs.

This script is intentionally scoped to inventory only. It must not rewrite
publisher, supplier, store, product, book or relationship CSVs because those
tables can contain hand-curated real data.
"""

from __future__ import annotations

import csv
import hashlib
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


SQL_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = SQL_DIR / "data"
CLEAN_DIR = SQL_DIR.parent / "data" / "clean"

INVENTORY_FIELDS = ["store_id", "product_id", "stock_qty", "safety_stock_qty"]

FLAGSHIP_STORE_IDS = {
    1,   # 上海五角场店
    2,   # 上海静安嘉里店
    5,   # 北京中关村店
    9,   # 北京国贸商城店
    10,  # 广州天河太古汇店
    14,  # 南京德基广场店
    15,  # 成都春熙路店
    16,  # 成都太古里店
    17,  # 深圳万象天地店
    20,  # 武汉恒隆广场店
    21,  # 杭州湖滨银泰店
    23,  # 青岛万象城店
    24,  # 重庆来福士店
    27,  # 苏州中心店
    35,  # 西安赛格国际店
    38,  # 长沙IFS店
}

TEXTBOOK_KEYWORDS = (
    "教材",
    "教辅",
    "考试",
    "考研",
    "四六级",
    "资格",
    "高中",
    "初中",
    "小学",
    "课标",
    "高职",
)

BOOK_STOCK_BANDS = {
    "普通图书": (1, 6),
    "重点图书": (6, 15),
    "畅销图书": (15, 40),
    "教材考试类": (20, 50),
}

DELI_STOCK_BANDS = {
    "高频": (50, 150),
    "常规": (15, 60),
    "低频": (2, 20),
}


@dataclass(frozen=True)
class StockBand:
    label: str
    low: int
    high: int


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def stable_int(seed: str, modulo: int) -> int:
    if modulo <= 0:
        raise ValueError("modulo must be positive")
    digest = hashlib.blake2b(seed.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % modulo


def stable_sample(items: list[int], count: int, seed: str) -> list[int]:
    count = min(count, len(items))
    rng = random.Random(stable_int(seed, 2**63 - 1))
    return rng.sample(items, count)


def count_in_range(seed: str, low: int, high: int) -> int:
    return low + stable_int(seed, high - low + 1)


def category_paths(categories: dict[int, dict[str, str]]) -> dict[int, list[str]]:
    paths: dict[int, list[str]] = {}

    def path_for(category_id: int) -> list[str]:
        if category_id in paths:
            return paths[category_id]
        row = categories[category_id]
        parent_id = row["parent_category_id"].strip()
        if parent_id:
            path = [*path_for(int(parent_id)), row["category_name"]]
        else:
            path = [row["category_name"]]
        paths[category_id] = path
        return path

    for category_id in categories:
        path_for(category_id)
    return paths


def classify_book(product: dict[str, str], path_names: list[str]) -> StockBand:
    searchable = " ".join([*path_names, product["product_name"]])
    if any(keyword in searchable for keyword in TEXTBOOK_KEYWORDS):
        label = "教材考试类"
    else:
        bucket = stable_int(f"book-band:{product['product_id']}", 100)
        if bucket < 10:
            label = "畅销图书"
        elif bucket < 32:
            label = "重点图书"
        else:
            label = "普通图书"
    low, high = BOOK_STOCK_BANDS[label]
    return StockBand(label, low, high)


def row_state(store_id: int, product_id: int) -> str:
    bucket = stable_int(f"stock-state:{store_id}:{product_id}", 10_000)
    if bucket < 200:
        return "stockout"
    if bucket < 1_200:
        return "warning"
    if bucket < 1_900:
        return "overstock"
    return "normal"


def quantity_and_safety(store_id: int, product_id: int, band: StockBand) -> tuple[int, int]:
    state = row_state(store_id, product_id)
    seed = f"stock-qty:{store_id}:{product_id}:{band.label}"

    if state == "stockout":
        safety = max(1, min(band.high, max(1, band.low // 2)))
        return 0, safety

    if state == "warning":
        warning_high = min(band.high, band.low + max(0, (band.high - band.low) // 5))
        stock_qty = count_in_range(f"{seed}:warning", band.low, warning_high)
        safety_delta_max = max(1, min(5, band.high - stock_qty))
        safety_stock_qty = min(
            band.high,
            stock_qty + count_in_range(f"{seed}:warning-safe", 1, safety_delta_max),
        )
        return stock_qty, max(stock_qty, safety_stock_qty)

    if state == "overstock":
        overstock_low = max(band.low, band.high - max(1, (band.high - band.low) // 5))
        stock_qty = count_in_range(f"{seed}:overstock", overstock_low, band.high)
    else:
        stock_qty = count_in_range(f"{seed}:normal", band.low, band.high)

    target_safety = max(1, round(band.high * 0.18))
    safety_stock_qty = min(target_safety, max(0, stock_qty - 1))
    return stock_qty, safety_stock_qty


def store_tier(store_id: int) -> str:
    return "旗舰店" if store_id in FLAGSHIP_STORE_IDS else "标准店"


def book_target_count(store_id: int) -> int:
    if store_id in FLAGSHIP_STORE_IDS:
        return count_in_range(f"book-target:{store_id}", 45_000, 65_000)
    return count_in_range(f"book-target:{store_id}", 15_000, 23_000)


def deli_target_count(store_id: int) -> int:
    if store_id in FLAGSHIP_STORE_IDS:
        return count_in_range(f"deli-target:{store_id}", 5_000, 8_000)
    return count_in_range(f"deli-target:{store_id}", 1_500, 3_000)


def split_deli_products(deli_product_ids: list[int]) -> dict[str, list[int]]:
    ranked = sorted(deli_product_ids, key=lambda product_id: stable_int(f"deli-frequency:{product_id}", 10**12))
    high_count = round(len(ranked) * 0.20)
    regular_count = round(len(ranked) * 0.50)
    return {
        "高频": ranked[:high_count],
        "常规": ranked[high_count : high_count + regular_count],
        "低频": ranked[high_count + regular_count :],
    }


def selected_deli_products(store_id: int, frequency_groups: dict[str, list[int]], target_count: int) -> list[tuple[int, StockBand]]:
    high_count = round(target_count * 0.20)
    regular_count = round(target_count * 0.50)
    low_count = target_count - high_count - regular_count
    frequency_counts = {"高频": high_count, "常规": regular_count, "低频": low_count}

    selected: list[tuple[int, StockBand]] = []
    for label in ("高频", "常规", "低频"):
        low, high = DELI_STOCK_BANDS[label]
        band = StockBand(label, low, high)
        for product_id in stable_sample(frequency_groups[label], frequency_counts[label], f"deli:{store_id}:{label}"):
            selected.append((product_id, band))
    return selected


def write_inventory() -> None:
    stores = read_csv(DATA_DIR / "store.csv")
    products = {int(row["product_id"]): row for row in read_csv(DATA_DIR / "product.csv")}
    book_product_ids = sorted(int(row["product_id"]) for row in read_csv(DATA_DIR / "book.csv"))
    categories = {int(row["category_id"]): row for row in read_csv(DATA_DIR / "category.csv")}
    paths = category_paths(categories)

    book_product_id_set = set(book_product_ids)
    deli_product_ids = sorted(product_id for product_id in products if product_id not in book_product_id_set)
    deli_frequency_groups = split_deli_products(deli_product_ids)

    book_bands = {
        product_id: classify_book(products[product_id], paths[int(products[product_id]["category_id"])])
        for product_id in book_product_ids
    }

    inventory_path = DATA_DIR / "inventory.csv"
    audit_rows: list[dict[str, str]] = []
    global_counts = Counter()
    total_rows = 0

    with inventory_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=INVENTORY_FIELDS, lineterminator="\n")
        writer.writeheader()

        for store in stores:
            store_id = int(store["store_id"])
            selected_books = stable_sample(book_product_ids, book_target_count(store_id), f"books:{store_id}")
            selected_deli = selected_deli_products(store_id, deli_frequency_groups, deli_target_count(store_id))
            store_counts = Counter()

            for product_id in selected_books:
                band = book_bands[product_id]
                stock_qty, safety_stock_qty = quantity_and_safety(store_id, product_id, band)
                state = row_state(store_id, product_id)
                writer.writerow(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "stock_qty": stock_qty,
                        "safety_stock_qty": safety_stock_qty,
                    }
                )
                store_counts["book_skus"] += 1
                store_counts[f"book_{band.label}"] += 1
                store_counts[state] += 1
                if stock_qty <= safety_stock_qty:
                    store_counts["warning_total"] += 1

            for product_id, band in selected_deli:
                stock_qty, safety_stock_qty = quantity_and_safety(store_id, product_id, band)
                state = row_state(store_id, product_id)
                writer.writerow(
                    {
                        "store_id": store_id,
                        "product_id": product_id,
                        "stock_qty": stock_qty,
                        "safety_stock_qty": safety_stock_qty,
                    }
                )
                store_counts["deli_skus"] += 1
                store_counts[f"deli_{band.label}"] += 1
                store_counts[state] += 1
                if stock_qty <= safety_stock_qty:
                    store_counts["warning_total"] += 1

            row_count = store_counts["book_skus"] + store_counts["deli_skus"]
            total_rows += row_count
            global_counts.update(store_counts)
            audit_rows.append(
                {
                    "store_id": str(store_id),
                    "store_name": store["store_name"],
                    "city": store["city"],
                    "store_tier": store_tier(store_id),
                    "book_sku_count": str(store_counts["book_skus"]),
                    "stationery_sku_count": str(store_counts["deli_skus"]),
                    "total_sku_count": str(row_count),
                    "book_normal_count": str(store_counts["book_普通图书"]),
                    "book_key_count": str(store_counts["book_重点图书"]),
                    "book_bestseller_count": str(store_counts["book_畅销图书"]),
                    "book_textbook_exam_count": str(store_counts["book_教材考试类"]),
                    "deli_high_frequency_count": str(store_counts["deli_高频"]),
                    "deli_regular_count": str(store_counts["deli_常规"]),
                    "deli_low_frequency_count": str(store_counts["deli_低频"]),
                    "stockout_rows": str(store_counts["stockout"]),
                    "warning_rows": str(store_counts["warning_total"]),
                    "overstock_rows": str(store_counts["overstock"]),
                    "stockout_ratio": f"{store_counts['stockout'] / row_count:.4%}",
                    "warning_ratio": f"{store_counts['warning_total'] / row_count:.4%}",
                    "overstock_ratio": f"{store_counts['overstock'] / row_count:.4%}",
                }
            )

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    audit_path = CLEAN_DIR / "inventory_rebuild_audit.csv"
    audit_fields = list(audit_rows[0])
    with audit_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=audit_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(audit_rows)

    print(f"Wrote {total_rows:,} inventory rows to {inventory_path}.")
    print(f"Wrote store inventory audit to {audit_path}.")
    print(f"Stores: {len(stores)} ({len(FLAGSHIP_STORE_IDS)} flagship, {len(stores) - len(FLAGSHIP_STORE_IDS)} standard).")
    print(f"Book SKUs by store: flagship 45,000-65,000; standard 15,000-23,000.")
    print(f"Deli SKU frequency mix: 20% high, 50% regular, 30% low per store.")
    print(f"Stockout ratio: {global_counts['stockout'] / total_rows:.4%}.")
    print(f"Warning ratio including stockout: {global_counts['warning_total'] / total_rows:.4%}.")
    print(f"Overstock/stagnant ratio: {global_counts['overstock'] / total_rows:.4%}.")


if __name__ == "__main__":
    write_inventory()
