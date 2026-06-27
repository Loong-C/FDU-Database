#!/usr/bin/env python
"""Build normalized sql/data CSV files from the preserved source datasets."""

from __future__ import annotations

import csv
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


SQL_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = SQL_DIR / "source"
LEGACY_DIR = SOURCE_DIR / "legacy"
DATA_DIR = SQL_DIR / "data"
SOURCE_BOOK_PRODUCT_ID_START = 120
NONBOOK_PRODUCT_ID_START = 20000

NONBOOK_SUPPLIERS = [
    {
        "supplier_id": 301,
        "supplier_name": "新华文具学习用品供应商",
        "contact_name": "吴倩",
        "phone": "010-73010001",
        "email": "stationery@example.com",
        "status": "active",
    },
    {
        "supplier_id": 302,
        "supplier_name": "生活文创综合供货商",
        "contact_name": "郑涛",
        "phone": "021-73020002",
        "email": "lifestyle@example.com",
        "status": "active",
    },
    {
        "supplier_id": 303,
        "supplier_name": "数码学习设备供应商",
        "contact_name": "孙悦",
        "phone": "0755-73030003",
        "email": "digital@example.com",
        "status": "active",
    },
    {
        "supplier_id": 304,
        "supplier_name": "礼品卡服务供应商",
        "contact_name": "高铭",
        "phone": "400-7304004",
        "email": "giftcard@example.com",
        "status": "active",
    },
]

NONBOOK_SUPPLIER_BY_CATEGORY = {
    "学习用品": 301,
    "家居/生活用品": 302,
    "3C数码": 303,
    "礼品卡": 304,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def write_csv(table: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    path = DATA_DIR / f"{table}.csv"
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{table}: {len(rows)} rows")


def project(rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    return [{field: row.get(field, "") for field in fields} for row in rows]


def money(value: str | Decimal) -> str:
    return str(Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def collation_key(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).casefold()


def limit_text(value: str, max_length: int) -> str:
    return " ".join(value.split())[:max_length].strip()


def stable_int(value: str) -> int:
    return sum((index + 1) * ord(char) for index, char in enumerate(value))


def legacy_product_overrides() -> dict[str, dict[str, str]]:
    overrides: dict[str, dict[str, str]] = {}
    for path in LEGACY_DIR.glob("*.csv"):
        for row in read_csv(path):
            if "product_id" in row and "product_barcode" in row and "product_name" in row:
                overrides.setdefault(
                    row["product_id"],
                    {
                        "barcode": row["product_barcode"],
                        "product_name": row["product_name"],
                    },
                )
    return overrides


def build_seed_data() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    source_books = read_csv(SOURCE_DIR / "books_mainland.csv")
    source_nonbooks = read_csv(SOURCE_DIR / "nonbook_mainland.csv")
    product_overrides = legacy_product_overrides()

    stores = [
        {
            "store_id": 1,
            "store_name": "北京朝阳店",
            "city": "北京",
            "address": "朝阳区建国路88号",
            "phone": "010-88880001",
            "manager_name": "王丽",
        },
        {
            "store_id": 2,
            "store_name": "上海浦东店",
            "city": "上海",
            "address": "浦东新区世纪大道200号",
            "phone": "021-88880002",
            "manager_name": "张强",
        },
    ]
    write_csv("store", ["store_id", "store_name", "city", "address", "phone", "manager_name"], stores)

    supplier_fields = ["supplier_id", "supplier_name", "contact_name", "phone", "email", "status"]
    suppliers = [
        {
            "supplier_id": 1,
            "supplier_name": "华北图书供应链",
            "contact_name": "刘洋",
            "phone": "010-60010001",
            "email": "hb_supplier@example.com",
            "status": "active",
        },
        {
            "supplier_id": 2,
            "supplier_name": "华东文化供货商",
            "contact_name": "陈晨",
            "phone": "021-60020002",
            "email": "hd_supplier@example.com",
            "status": "active",
        },
        {
            "supplier_id": 3,
            "supplier_name": "旧版图书清结商",
            "contact_name": "赵宁",
            "phone": "0755-60030003",
            "email": "oldbooks@example.com",
            "status": "inactive",
        },
    ]
    suppliers += NONBOOK_SUPPLIERS
    suppliers += project(read_csv(LEGACY_DIR / "supplier.csv"), supplier_fields)
    write_csv("supplier", supplier_fields, suppliers)

    category_fields = ["category_id", "category_name", "parent_category_id"]
    categories = project(read_csv(SOURCE_DIR / "categories_mainland.csv"), category_fields)
    write_csv("category", category_fields, categories)
    category_ids = {row["category_name"]: row["category_id"] for row in categories}

    publisher_fields = [
        "publisher_id",
        "publisher_name",
        "contact_name",
        "phone",
        "email",
        "address",
        "country",
        "website",
    ]
    publishers = [
        {
            "publisher_id": 1,
            "publisher_name": "人民邮电出版社",
            "contact_name": "李编辑",
            "phone": "010-12340001",
            "email": "contact@ptpress.com.cn",
            "address": "北京市丰台区成寿寺路11号",
            "country": "中国",
            "website": "https://www.ptpress.com.cn",
        },
        {
            "publisher_id": 2,
            "publisher_name": "机械工业出版社",
            "contact_name": "王编辑",
            "phone": "010-12340002",
            "email": "contact@cmpbook.com",
            "address": "北京市西城区百万庄大街22号",
            "country": "中国",
            "website": "https://www.cmpbook.com",
        },
        {
            "publisher_id": 3,
            "publisher_name": "译林出版社",
            "contact_name": "周编辑",
            "phone": "025-12340003",
            "email": "contact@yilinpress.com",
            "address": "南京市鼓楼区湖南路1号",
            "country": "中国",
            "website": "https://www.yilinpress.com",
        },
    ]
    publisher_ids = {row["publisher_name"]: row["publisher_id"] for row in publishers}
    publisher_collation_ids = {
        collation_key(row["publisher_name"]): row["publisher_id"]
        for row in publishers
    }
    for publisher_name in sorted({row["publisher"] for row in source_books}):
        key = collation_key(publisher_name)
        if key not in publisher_collation_ids:
            publisher_id = len(publishers) + 1
            publishers.append(
                {
                    "publisher_id": publisher_id,
                    "publisher_name": limit_text(publisher_name, 150),
                    "contact_name": "",
                    "phone": "",
                    "email": "",
                    "address": "",
                    "country": "",
                    "website": "",
                }
            )
            publisher_collation_ids[key] = publisher_id
        publisher_ids[publisher_name] = publisher_collation_ids[key]
    write_csv("publisher", publisher_fields, publishers)

    product_fields = [
        "product_id",
        "product_name",
        "category_id",
        "unit",
        "unit_price",
        "cost_price",
        "barcode",
        "status",
    ]
    products = [
        {
            "product_id": 1,
            "product_name": "数据库系统概论（第6版）",
            "category_id": category_ids["计算机类"],
            "unit": "本",
            "unit_price": "88.00",
            "cost_price": "55.00",
            "barcode": "9787111000001",
            "status": "onsale",
        },
        {
            "product_id": 2,
            "product_name": "深入理解计算机系统",
            "category_id": category_ids["计算机类"],
            "unit": "本",
            "unit_price": "129.00",
            "cost_price": "80.00",
            "barcode": "9787111000002",
            "status": "onsale",
        },
        {
            "product_id": 3,
            "product_name": "百年孤独",
            "category_id": category_ids["外国小说"],
            "unit": "本",
            "unit_price": "59.00",
            "cost_price": "35.00",
            "barcode": "9787111000003",
            "status": "onsale",
        },
        {
            "product_id": 4,
            "product_name": "黑色中性笔",
            "category_id": category_ids["中性笔"],
            "unit": "支",
            "unit_price": "3.50",
            "cost_price": "1.20",
            "barcode": "690123450001",
            "status": "onsale",
        },
        {
            "product_id": 5,
            "product_name": "A4笔记本",
            "category_id": category_ids["笔记本/记事本"],
            "unit": "本",
            "unit_price": "12.00",
            "cost_price": "6.00",
            "barcode": "690123450002",
            "status": "offsale",
        },
    ]
    for product_id, row in enumerate(source_books, start=SOURCE_BOOK_PRODUCT_ID_START):
        override = product_overrides.get(str(product_id), {})
        products.append(
            {
                "product_id": product_id,
                "product_name": limit_text(override.get("product_name") or row["title"], 200),
                "category_id": category_ids[row["category_name"]],
                "unit": row["unit"],
                "unit_price": money(row["suggested_unit_price"]),
                "cost_price": money(Decimal(row["suggested_unit_price"]) * Decimal("0.65")),
                "barcode": override.get("barcode") or row["isbn"],
                "status": row["status"],
            }
        )
    for product_id, row in enumerate(source_nonbooks, start=NONBOOK_PRODUCT_ID_START):
        products.append(
            {
                "product_id": product_id,
                "product_name": limit_text(row["product_name"], 200),
                "category_id": category_ids[row["category_name"]],
                "unit": row["unit"],
                "unit_price": money(row["suggested_unit_price"]),
                "cost_price": money(Decimal(row["suggested_unit_price"]) * Decimal("0.70")),
                "barcode": row["barcode"],
                "status": row["status"],
            }
        )
    write_csv("product", product_fields, products)

    book_fields = ["product_id", "isbn", "publisher_id", "publish_date", "edition", "language", "page_count"]
    books = [
        {
            "product_id": 1,
            "isbn": "9787111000001",
            "publisher_id": 1,
            "publish_date": "2023-08-01",
            "edition": "第6版",
            "language": "中文",
            "page_count": 420,
        },
        {
            "product_id": 2,
            "isbn": "9787111000002",
            "publisher_id": 2,
            "publish_date": "2022-05-15",
            "edition": "第1版",
            "language": "中文",
            "page_count": 720,
        },
        {
            "product_id": 3,
            "isbn": "9787111000003",
            "publisher_id": 3,
            "publish_date": "2021-11-20",
            "edition": "第1版",
            "language": "中文",
            "page_count": 360,
        },
    ]
    for product_id, row in enumerate(source_books, start=SOURCE_BOOK_PRODUCT_ID_START):
        override = product_overrides.get(str(product_id), {})
        books.append(
            {
                "product_id": product_id,
                "isbn": override.get("barcode") or row["isbn"],
                "publisher_id": publisher_ids[row["publisher"]],
                "publish_date": row["publish_date_raw"],
                "edition": "",
                "language": row["language"],
                "page_count": row["page_count"],
            }
        )
    write_csv("book", book_fields, books)

    author_fields = ["author_id", "author_name", "country"]
    authors = [
        {"author_id": 1, "author_name": "王强", "country": "中国"},
        {"author_id": 2, "author_name": "Randal E. Bryant", "country": "美国"},
        {"author_id": 3, "author_name": "加西亚·马尔克斯", "country": "哥伦比亚"},
    ]
    author_ids = {row["author_name"]: row["author_id"] for row in authors}
    source_author_names = {
        name.strip()
        for row in source_books
        for name in row["authors"].split(";")
        if name.strip()
    }
    for author_name in sorted(source_author_names):
        if author_name not in author_ids:
            author_id = len(authors) + 1
            authors.append({"author_id": author_id, "author_name": limit_text(author_name, 100), "country": ""})
            author_ids[author_name] = author_id
    write_csv("author", author_fields, authors)

    translators = [
        {"translator_id": 1, "translator_name": "裴小龙", "country": "中国"},
        {"translator_id": 2, "translator_name": "范晔", "country": "中国"},
    ]
    write_csv("translator", ["translator_id", "translator_name", "country"], translators)

    book_authors = [
        {"product_id": 1, "author_id": 1, "author_order": 1},
        {"product_id": 2, "author_id": 2, "author_order": 1},
        {"product_id": 3, "author_id": 3, "author_order": 1},
    ]
    for product_id, row in enumerate(source_books, start=SOURCE_BOOK_PRODUCT_ID_START):
        names = list(dict.fromkeys(name.strip() for name in row["authors"].split(";") if name.strip()))
        for author_order, author_name in enumerate(names, start=1):
            book_authors.append(
                {
                    "product_id": product_id,
                    "author_id": author_ids[author_name],
                    "author_order": author_order,
                }
            )
    write_csv("book_author", ["product_id", "author_id", "author_order"], book_authors)

    write_csv(
        "book_translator",
        ["product_id", "translator_id"],
        [{"product_id": 2, "translator_id": 1}, {"product_id": 3, "translator_id": 2}],
    )

    supplier_product_fields = ["supplier_id", "product_id", "supply_price", "min_order_qty", "is_primary"]
    supplier_products = [
        {"supplier_id": 1, "product_id": 1, "supply_price": "54.00", "min_order_qty": 20, "is_primary": 1},
        {"supplier_id": 1, "product_id": 4, "supply_price": "1.10", "min_order_qty": 100, "is_primary": 1},
        {"supplier_id": 2, "product_id": 2, "supply_price": "78.00", "min_order_qty": 15, "is_primary": 1},
        {"supplier_id": 2, "product_id": 3, "supply_price": "33.00", "min_order_qty": 30, "is_primary": 1},
        {"supplier_id": 2, "product_id": 5, "supply_price": "5.50", "min_order_qty": 80, "is_primary": 0},
        {"supplier_id": 3, "product_id": 3, "supply_price": "25.00", "min_order_qty": 100, "is_primary": 0},
    ]
    supplier_products += project(read_csv(LEGACY_DIR / "supplier_product.csv"), supplier_product_fields)
    supplier_product_keys = {
        (str(row["supplier_id"]), str(row["product_id"]))
        for row in supplier_products
    }
    for product_id, row in enumerate(source_nonbooks, start=NONBOOK_PRODUCT_ID_START):
        supplier_id = NONBOOK_SUPPLIER_BY_CATEGORY.get(row["category_name"], 302)
        key = (str(supplier_id), str(product_id))
        if key in supplier_product_keys:
            continue
        supplier_product_keys.add(key)
        supplier_products.append(
            {
                "supplier_id": supplier_id,
                "product_id": product_id,
                "supply_price": money(Decimal(row["suggested_unit_price"]) * Decimal("0.70")),
                "min_order_qty": 60 if row["category_name"] == "学习用品" else 12,
                "is_primary": 1,
            }
        )
    write_csv("supplier_product", supplier_product_fields, supplier_products)

    customer_fields = ["customer_id", "customer_name", "phone", "email", "address", "register_time", "status"]
    customers = [
        {
            "customer_id": 1,
            "customer_name": "李明",
            "phone": "13800000001",
            "email": "liming@example.com",
            "address": "北京市海淀区学院路1号",
            "register_time": "2025-10-01 10:00:00",
            "status": "active",
        },
        {
            "customer_id": 2,
            "customer_name": "韩梅梅",
            "phone": "13800000002",
            "email": "hanmeimei@example.com",
            "address": "上海市浦东新区花木路8号",
            "register_time": "2025-10-03 15:30:00",
            "status": "active",
        },
        {
            "customer_id": 3,
            "customer_name": "Tom",
            "phone": "13800000003",
            "email": "tom@example.com",
            "address": "北京市朝阳区望京路9号",
            "register_time": "2025-11-10 09:20:00",
            "status": "inactive",
        },
    ]
    customers += project(read_csv(LEGACY_DIR / "customer.csv"), customer_fields)
    write_csv("customer", customer_fields, customers)

    member_fields = ["customer_id", "member_no", "level", "points", "join_date"]
    members = [
        {"customer_id": 1, "member_no": "M20250001", "level": "gold", "points": 1200, "join_date": "2025-10-02"},
        {"customer_id": 2, "member_no": "M20250002", "level": "silver", "points": 450, "join_date": "2025-10-04"},
    ]
    members += project(read_csv(LEGACY_DIR / "member.csv"), member_fields)
    write_csv("member", member_fields, members)

    write_csv(
        "system_user",
        ["user_id", "username", "password_hash", "real_name", "phone", "email", "status"],
        [
            {
                "user_id": 1,
                "username": "admin",
                "password_hash": "pbkdf2_sha256$demo$admin",
                "real_name": "系统管理员",
                "phone": "13900000001",
                "email": "admin@example.com",
                "status": "active",
            },
            {
                "user_id": 2,
                "username": "operator",
                "password_hash": "pbkdf2_sha256$demo$operator",
                "real_name": "门店操作员",
                "phone": "13900000002",
                "email": "operator@example.com",
                "status": "active",
            },
            {
                "user_id": 3,
                "username": "viewer",
                "password_hash": "pbkdf2_sha256$demo$viewer",
                "real_name": "查询用户",
                "phone": "13900000003",
                "email": "viewer@example.com",
                "status": "active",
            },
        ],
    )
    write_csv(
        "role",
        ["role_id", "role_name", "role_desc"],
        [
            {"role_id": 1, "role_name": "admin", "role_desc": "全局维护与审核"},
            {"role_id": 2, "role_name": "operator", "role_desc": "门店销售、客户维护、采购入库操作"},
            {"role_id": 3, "role_name": "viewer", "role_desc": "只读统计分析"},
        ],
    )
    write_csv(
        "permission",
        ["permission_id", "permission_code", "permission_name", "module_name"],
        [
            {"permission_id": 1, "permission_code": "store.manage", "permission_name": "门店维护", "module_name": "store"},
            {
                "permission_id": 2,
                "permission_code": "catalog.manage",
                "permission_name": "商品与图书维护",
                "module_name": "catalog",
            },
            {
                "permission_id": 3,
                "permission_code": "customer.manage",
                "permission_name": "客户会员维护",
                "module_name": "customer",
            },
            {"permission_id": 4, "permission_code": "sale.write", "permission_name": "销售录入", "module_name": "sale"},
            {
                "permission_id": 5,
                "permission_code": "purchase.write",
                "permission_name": "采购入库",
                "module_name": "purchase",
            },
            {
                "permission_id": 6,
                "permission_code": "analytics.read",
                "permission_name": "统计分析查看",
                "module_name": "analytics",
            },
            {
                "permission_id": 7,
                "permission_code": "inventory.read",
                "permission_name": "库存查看",
                "module_name": "inventory",
            },
        ],
    )
    write_csv(
        "user_role",
        ["user_id", "role_id"],
        [{"user_id": 1, "role_id": 1}, {"user_id": 2, "role_id": 2}, {"user_id": 3, "role_id": 3}],
    )
    write_csv(
        "role_permission",
        ["role_id", "permission_id"],
        [
            {"role_id": 1, "permission_id": 1},
            {"role_id": 1, "permission_id": 2},
            {"role_id": 1, "permission_id": 3},
            {"role_id": 1, "permission_id": 4},
            {"role_id": 1, "permission_id": 5},
            {"role_id": 1, "permission_id": 6},
            {"role_id": 1, "permission_id": 7},
            {"role_id": 2, "permission_id": 3},
            {"role_id": 2, "permission_id": 4},
            {"role_id": 2, "permission_id": 5},
            {"role_id": 2, "permission_id": 6},
            {"role_id": 2, "permission_id": 7},
            {"role_id": 3, "permission_id": 6},
            {"role_id": 3, "permission_id": 7},
        ],
    )

    purchase_order_fields = [
        "purchase_order_id",
        "supplier_id",
        "store_id",
        "created_by",
        "order_time",
        "status",
        "total_amount",
    ]
    purchase_orders = [
        {
            "purchase_order_id": 1,
            "supplier_id": 1,
            "store_id": 1,
            "created_by": 1,
            "order_time": "2026-04-08 09:00:00",
            "status": "received",
            "total_amount": "1080.00",
        },
        {
            "purchase_order_id": 2,
            "supplier_id": 2,
            "store_id": 2,
            "created_by": 2,
            "order_time": "2026-04-09 10:30:00",
            "status": "approved",
            "total_amount": "2340.00",
        },
    ]
    purchase_orders += project(read_csv(LEGACY_DIR / "purchase_order.csv"), purchase_order_fields)
    write_csv("purchase_order", purchase_order_fields, purchase_orders)

    purchase_item_fields = [
        "purchase_order_id",
        "line_no",
        "product_id",
        "quantity",
        "purchase_price",
        "line_amount",
    ]
    purchase_items = [
        {
            "purchase_order_id": 1,
            "line_no": 1,
            "product_id": 1,
            "quantity": 20,
            "purchase_price": "54.00",
            "line_amount": "1080.00",
        },
        {
            "purchase_order_id": 2,
            "line_no": 1,
            "product_id": 2,
            "quantity": 30,
            "purchase_price": "78.00",
            "line_amount": "2340.00",
        },
    ]
    purchase_items += project(read_csv(LEGACY_DIR / "purchase_order_item.csv"), purchase_item_fields)
    write_csv("purchase_order_item", purchase_item_fields, purchase_items)

    stock_in_fields = ["stock_in_id", "purchase_order_id", "store_id", "operator_id", "inbound_time", "status"]
    stock_ins = [
        {
            "stock_in_id": 1,
            "purchase_order_id": 1,
            "store_id": 1,
            "operator_id": 2,
            "inbound_time": "2026-04-09 16:00:00",
            "status": "approved",
        },
        {
            "stock_in_id": 2,
            "purchase_order_id": 2,
            "store_id": 2,
            "operator_id": 2,
            "inbound_time": "2026-04-10 15:30:00",
            "status": "pending",
        },
    ]
    stock_ins += project(read_csv(LEGACY_DIR / "stock_in.csv"), stock_in_fields)
    write_csv("stock_in", stock_in_fields, stock_ins)

    stock_item_fields = ["stock_in_id", "line_no", "product_id", "quantity", "unit_cost", "line_amount"]
    stock_items = [
        {
            "stock_in_id": 1,
            "line_no": 1,
            "product_id": 1,
            "quantity": 20,
            "unit_cost": "54.00",
            "line_amount": "1080.00",
        },
        {
            "stock_in_id": 2,
            "line_no": 1,
            "product_id": 2,
            "quantity": 30,
            "unit_cost": "78.00",
            "line_amount": "2340.00",
        },
    ]
    stock_items += project(read_csv(LEGACY_DIR / "stock_in_item.csv"), stock_item_fields)
    write_csv("stock_in_item", stock_item_fields, stock_items)

    inventory_fields = ["store_id", "product_id", "stock_qty", "safety_stock_qty"]
    inventory = [
        {"store_id": 1, "product_id": 1, "stock_qty": 120, "safety_stock_qty": 20},
        {"store_id": 1, "product_id": 2, "stock_qty": 35, "safety_stock_qty": 10},
        {"store_id": 1, "product_id": 3, "stock_qty": 25, "safety_stock_qty": 10},
        {"store_id": 1, "product_id": 4, "stock_qty": 500, "safety_stock_qty": 50},
        {"store_id": 1, "product_id": 5, "stock_qty": 300, "safety_stock_qty": 30},
        {"store_id": 2, "product_id": 1, "stock_qty": 30, "safety_stock_qty": 10},
        {"store_id": 2, "product_id": 2, "stock_qty": 60, "safety_stock_qty": 15},
        {"store_id": 2, "product_id": 3, "stock_qty": 90, "safety_stock_qty": 20},
        {"store_id": 2, "product_id": 4, "stock_qty": 80, "safety_stock_qty": 20},
        {"store_id": 2, "product_id": 5, "stock_qty": 8, "safety_stock_qty": 10},
    ]
    inventory += project(read_csv(LEGACY_DIR / "inventory.csv"), inventory_fields)
    inventory_keys = {
        (str(row["store_id"]), str(row["product_id"]))
        for row in inventory
    }
    for product_id, row in enumerate(source_nonbooks, start=NONBOOK_PRODUCT_ID_START):
        seed = stable_int(row["barcode"])
        for store_id in (1, 2):
            key = (str(store_id), str(product_id))
            if key in inventory_keys:
                continue
            inventory_keys.add(key)
            base_qty = 18 if row["category_name"] == "学习用品" else 8
            stock_qty = base_qty + ((seed + store_id * 7) % (36 if row["category_name"] == "学习用品" else 18))
            safety_stock_qty = max(3, stock_qty // 4)
            inventory.append(
                {
                    "store_id": store_id,
                    "product_id": product_id,
                    "stock_qty": stock_qty,
                    "safety_stock_qty": safety_stock_qty,
                }
            )
    write_csv("inventory", inventory_fields, inventory)

    sale_fields = [
        "sale_id",
        "store_id",
        "customer_id",
        "sale_time",
        "payment_method",
        "total_amount",
        "discount_amount",
        "actual_amount",
    ]
    sales = [
        {
            "sale_id": 1,
            "store_id": 1,
            "customer_id": 1,
            "sale_time": "2026-04-10 10:15:00",
            "payment_method": "wechat",
            "total_amount": "147.00",
            "discount_amount": "10.00",
            "actual_amount": "137.00",
        },
        {
            "sale_id": 2,
            "store_id": 1,
            "customer_id": "",
            "sale_time": "2026-04-10 14:20:00",
            "payment_method": "cash",
            "total_amount": "35.00",
            "discount_amount": "0.00",
            "actual_amount": "35.00",
        },
        {
            "sale_id": 3,
            "store_id": 2,
            "customer_id": 2,
            "sale_time": "2026-04-11 16:05:00",
            "payment_method": "alipay",
            "total_amount": "188.00",
            "discount_amount": "20.00",
            "actual_amount": "168.00",
        },
    ]
    sales += project(read_csv(LEGACY_DIR / "sale.csv"), sale_fields)
    write_csv("sale", sale_fields, sales)

    sale_item_fields = ["sale_id", "line_no", "product_id", "quantity", "unit_price", "line_amount"]
    sale_items = [
        {"sale_id": 1, "line_no": 1, "product_id": 1, "quantity": 1, "unit_price": "88.00", "line_amount": "88.00"},
        {"sale_id": 1, "line_no": 2, "product_id": 4, "quantity": 10, "unit_price": "3.50", "line_amount": "35.00"},
        {"sale_id": 1, "line_no": 3, "product_id": 5, "quantity": 2, "unit_price": "12.00", "line_amount": "24.00"},
        {"sale_id": 2, "line_no": 1, "product_id": 4, "quantity": 10, "unit_price": "3.50", "line_amount": "35.00"},
        {"sale_id": 3, "line_no": 1, "product_id": 2, "quantity": 1, "unit_price": "129.00", "line_amount": "129.00"},
        {"sale_id": 3, "line_no": 2, "product_id": 3, "quantity": 1, "unit_price": "59.00", "line_amount": "59.00"},
    ]
    sale_items += project(read_csv(LEGACY_DIR / "sale_item.csv"), sale_item_fields)
    write_csv("sale_item", sale_item_fields, sale_items)


if __name__ == "__main__":
    build_seed_data()
