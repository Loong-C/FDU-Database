#!/usr/bin/env python
"""Generate customer, member, sales, purchase order and stock-in seed CSVs.

The script only rewrites transactional/customer CSVs. It reads the existing
store, supplier, product, category, supplier_product and inventory data as the
business base, and does not touch publisher/supplier/store/product/book data.
"""

from __future__ import annotations

import bisect
import csv
import hashlib
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


SQL_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = SQL_DIR / "data"
CLEAN_DIR = SQL_DIR.parent / "data" / "clean"

RNG = random.Random(20260630)

CUSTOMER_COUNT = 100_000
MEMBER_COUNT = 65_000
SALES_START = date(2026, 1, 1)
SALES_END = date(2026, 6, 30)
PROCUREMENT_START = date(2025, 12, 1)
PROCUREMENT_END = date(2026, 6, 30)
MAX_TRANSACTION_PRICE_CENTS = 200_000

FLAGSHIP_STORE_IDS = {1, 2, 5, 9, 10, 14, 15, 16, 17, 20, 21, 23, 24, 27, 35, 38}

CUSTOMER_FIELDS = ["customer_id", "customer_name", "phone", "email", "address", "register_time", "status"]
MEMBER_FIELDS = ["customer_id", "member_no", "level", "points", "join_date"]
SALE_FIELDS = ["sale_id", "store_id", "customer_id", "sale_time", "payment_method", "total_amount", "discount_amount", "actual_amount"]
SALE_ITEM_FIELDS = ["sale_id", "line_no", "product_id", "quantity", "unit_price", "line_amount"]
PURCHASE_ORDER_FIELDS = ["purchase_order_id", "supplier_id", "store_id", "created_by", "order_time", "status", "total_amount"]
PURCHASE_ORDER_ITEM_FIELDS = ["purchase_order_id", "line_no", "product_id", "quantity", "purchase_price", "line_amount"]
STOCK_IN_FIELDS = ["stock_in_id", "purchase_order_id", "store_id", "operator_id", "inbound_time", "status"]
STOCK_IN_ITEM_FIELDS = ["stock_in_id", "line_no", "product_id", "quantity", "unit_cost", "line_amount"]

SURNAMES = "王李张刘陈杨赵黄周吴徐孙胡朱高林何郭马罗梁宋郑谢韩唐冯于董萧程曹袁邓许傅沈曾彭吕苏卢蒋蔡贾丁魏薛叶阎余潘杜戴夏钟汪田任姜范方石姚谭廖邹熊金陆郝孔白崔康毛邱秦江史顾侯邵孟龙万段雷钱汤尹黎易常武乔贺赖龚文庞樊兰殷施陶洪翟安颜倪严牛温芦季俞章鲁葛伍韦申尤毕聂丛焦向柳邢路岳齐沿梅莫庄辛管祝左涂谷祁时舒耿牟卜路詹关苗凌费纪靳盛童欧甄项曲成游阳裴席卫查屈鲍位覃霍翁隋植甘景薄单包司柏宁柯阮桂闵欧阳"
GIVEN_NAMES = [
    "一鸣", "子涵", "梓萱", "思远", "嘉怡", "明轩", "雨桐", "浩然", "欣怡", "子墨",
    "若曦", "宇航", "诗涵", "泽宇", "佳宁", "晨曦", "奕辰", "语嫣", "书瑶", "景行",
    "知远", "安然", "予安", "启航", "云舒", "承泽", "沐阳", "清扬", "星辰", "闻舟",
    "以宁", "修远", "怀瑾", "明哲", "嘉言", "向榆", "念初", "南星", "舒然", "卓然",
]
CITY_DISTRICTS = {
    "上海": ["杨浦区", "静安区", "徐汇区", "浦东新区", "普陀区"],
    "北京": ["海淀区", "朝阳区", "东城区", "西城区", "丰台区"],
    "广州": ["天河区", "越秀区", "海珠区", "荔湾区"],
    "深圳": ["南山区", "福田区", "罗湖区", "宝安区"],
    "杭州": ["上城区", "拱墅区", "西湖区", "滨江区"],
    "南京": ["玄武区", "秦淮区", "鼓楼区", "建邺区"],
    "成都": ["锦江区", "武侯区", "青羊区", "成华区"],
    "武汉": ["江汉区", "硚口区", "武昌区", "洪山区"],
    "重庆": ["渝中区", "江北区", "南岸区", "九龙坡区"],
}
FALLBACK_DISTRICTS = ["中心城区", "高新区", "开发区", "新城区"]

MONTH_FACTORS = {
    1: 1.08,
    2: 0.78,
    3: 0.96,
    4: 1.03,
    5: 1.12,
    6: 1.24,
    12: 1.16,
}
WEEKDAY_FACTORS = {
    0: 0.86,
    1: 0.88,
    2: 0.94,
    3: 1.00,
    4: 1.10,
    5: 1.36,
    6: 1.28,
}
CITY_FACTORS = {
    "上海": 1.18,
    "北京": 1.16,
    "深圳": 1.13,
    "广州": 1.10,
    "杭州": 1.06,
    "南京": 1.04,
    "成都": 1.04,
    "武汉": 1.02,
    "重庆": 1.00,
    "苏州": 1.02,
    "青岛": 0.98,
    "大连": 0.96,
}
TOP_CATEGORY_WEIGHTS = {
    "教材教辅": 1.22,
    "人文社科": 1.05,
    "文学艺术": 1.42,
    "科技工程": 0.86,
    "医学卫生": 0.58,
    "经济管理": 0.92,
    "法律政务": 0.48,
    "语言工具": 0.52,
    "少儿童书": 0.95,
    "生活休闲": 1.08,
    "古籍文献": 0.22,
    "综合图书": 0.62,
    "书写用品": 1.55,
    "会议展示用品": 0.55,
    "办公用纸": 1.42,
    "学生用品": 0.88,
    "文件管理": 1.25,
    "文房四宝": 0.36,
    "本册纸品": 1.20,
    "桌面文具": 1.05,
    "画具画材": 0.62,
    "胶粘用品": 0.78,
    "财务行政用品": 0.54,
}
PAYMENT_METHODS = [("wechat", 42), ("alipay", 36), ("card", 13), ("cash", 6), ("mixed", 3)]
MEMBER_DISCOUNT_BPS = {"bronze": 200, "silver": 500, "gold": 800, "platinum": 1000}
LEVEL_BASE_POINTS = {"bronze": 120, "silver": 1_200, "gold": 5_200, "platinum": 20_000}


@dataclass(frozen=True)
class ProductInfo:
    product_id: int
    category_id: int
    unit: str
    price_cents: int
    cost_cents: int
    is_book: bool
    top_category: str
    leaf_category: str


@dataclass
class WeightedPool:
    product_ids: list[int]
    cumulative_weights: list[float]
    total_weight: float

    def choose(self, rng: random.Random) -> int:
        needle = rng.random() * self.total_weight
        index = bisect.bisect_left(self.cumulative_weights, needle)
        if index >= len(self.product_ids):
            index = len(self.product_ids) - 1
        return self.product_ids[index]


def stable_int(seed: str, modulo: int) -> int:
    digest = hashlib.blake2b(seed.encode("utf-8"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % modulo


def cents(value: str) -> int:
    text = value.strip()
    yuan, _, fen = text.partition(".")
    return int(yuan) * 100 + int((fen + "00")[:2])


def money(value_cents: int) -> str:
    return f"{value_cents // 100}.{value_cents % 100:02d}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def weighted_choice(weighted_items: list[tuple[str, int]], rng: random.Random) -> str:
    total = sum(weight for _, weight in weighted_items)
    needle = rng.randint(1, total)
    running = 0
    for item, weight in weighted_items:
        running += weight
        if needle <= running:
            return item
    return weighted_items[-1][0]


def daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def datetime_on_day(day: date, rng: random.Random, business_kind: str = "sale") -> datetime:
    if business_kind == "sale":
        hours = [(10, 4), (11, 5), (12, 7), (13, 6), (14, 7), (15, 7), (16, 8), (17, 10), (18, 13), (19, 15), (20, 13), (21, 5)]
    else:
        hours = [(9, 6), (10, 9), (11, 8), (13, 8), (14, 9), (15, 8), (16, 6)]
    hour = int(weighted_choice([(str(h), w) for h, w in hours], rng))
    return datetime(day.year, day.month, day.day, hour, rng.randint(0, 59), rng.randint(0, 59))


def category_paths(categories: dict[int, dict[str, str]]) -> dict[int, list[str]]:
    paths: dict[int, list[str]] = {}

    def build(category_id: int) -> list[str]:
        if category_id in paths:
            return paths[category_id]
        row = categories[category_id]
        parent_id = row["parent_category_id"].strip()
        if parent_id:
            path = [*build(int(parent_id)), row["category_name"]]
        else:
            path = [row["category_name"]]
        paths[category_id] = path
        return path

    for category_id in categories:
        build(category_id)
    return paths


def top_category_for(path: list[str]) -> str:
    if len(path) >= 2:
        return path[1]
    return path[0]


def heat_multiplier(product_id: int) -> float:
    bucket = stable_int(f"sales-heat:{product_id}", 100_000)
    if bucket < 90:
        return 240.0
    if bucket < 550:
        return 85.0
    if bucket < 2_800:
        return 24.0
    if bucket < 12_000:
        return 6.5
    if bucket < 42_000:
        return 1.8
    return 0.62


def product_sales_weight(product: ProductInfo, stock_qty: int, safety_stock_qty: int) -> float:
    category_weight = TOP_CATEGORY_WEIGHTS.get(product.top_category, 0.75)
    leaf_boost = 1.0
    if product.leaf_category in {"大学教材", "中性笔/签字笔", "复印纸", "档案盒/文件盒", "生活美育", "教育新闻传播"}:
        leaf_boost = 1.18
    elif product.top_category in {"古籍文献", "文房四宝", "会议展示用品"}:
        leaf_boost = 0.72
    stock_weight = 1.0
    if stock_qty <= safety_stock_qty:
        stock_weight = 0.48
    elif stock_qty >= max(10, safety_stock_qty * 8):
        stock_weight = 1.08
    channel_weight = 1.0
    if not product.is_book:
        channel_weight = 0.38
        if product.price_cents > 20_000:
            channel_weight *= 0.35
    elif product.price_cents > 30_000:
        channel_weight = 0.62
    return max(0.01, category_weight * leaf_boost * heat_multiplier(product.product_id) * stock_weight * channel_weight)


def load_business_base():
    stores = read_csv(DATA_DIR / "store.csv")
    categories = {int(row["category_id"]): row for row in read_csv(DATA_DIR / "category.csv")}
    paths = category_paths(categories)
    book_ids = {int(row["product_id"]) for row in read_csv(DATA_DIR / "book.csv")}
    products: dict[int, ProductInfo] = {}
    for row in read_csv(DATA_DIR / "product.csv"):
        product_id = int(row["product_id"])
        category_id = int(row["category_id"])
        path = paths[category_id]
        products[product_id] = ProductInfo(
            product_id=product_id,
            category_id=category_id,
            unit=row["unit"],
            price_cents=cents(row["unit_price"]),
            cost_cents=cents(row["cost_price"]),
            is_book=product_id in book_ids,
            top_category=top_category_for(path),
            leaf_category=path[-1],
        )

    supply_prices: dict[tuple[int, int], int] = {}
    primary_supplier_by_product: dict[int, int] = {}
    supplier_products: dict[int, list[int]] = defaultdict(list)
    for row in read_csv(DATA_DIR / "supplier_product.csv"):
        supplier_id = int(row["supplier_id"])
        product_id = int(row["product_id"])
        supply_prices[(supplier_id, product_id)] = cents(row["supply_price"])
        supplier_products[supplier_id].append(product_id)
        if row["is_primary"] in {"1", "true", "True"}:
            primary_supplier_by_product[product_id] = supplier_id

    store_product_ids: dict[int, list[int]] = defaultdict(list)
    store_supplier_products: dict[tuple[int, int], list[int]] = defaultdict(list)
    weighted_parts: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for row in read_csv(DATA_DIR / "inventory.csv"):
        stock_qty = int(row["stock_qty"])
        if stock_qty <= 0:
            continue
        store_id = int(row["store_id"])
        product_id = int(row["product_id"])
        product = products[product_id]
        if product.price_cents > MAX_TRANSACTION_PRICE_CENTS:
            continue
        supplier_id = primary_supplier_by_product.get(product_id)
        store_product_ids[store_id].append(product_id)
        if supplier_id is not None:
            store_supplier_products[(store_id, supplier_id)].append(product_id)
        weight = product_sales_weight(product, stock_qty, int(row["safety_stock_qty"]))
        weighted_parts[store_id].append((product_id, weight))

    store_sales_pools: dict[int, WeightedPool] = {}
    for store_id, parts in weighted_parts.items():
        product_ids: list[int] = []
        cumulative_weights: list[float] = []
        running = 0.0
        for product_id, weight in parts:
            running += weight
            product_ids.append(product_id)
            cumulative_weights.append(running)
        store_sales_pools[store_id] = WeightedPool(product_ids, cumulative_weights, running)

    return stores, products, store_sales_pools, store_supplier_products, supply_prices


def customer_city(customer_id: int, stores: list[dict[str, str]]) -> str:
    if customer_id <= 55_000:
        city_weights = [
            ("上海", 14), ("北京", 13), ("深圳", 10), ("广州", 10), ("杭州", 7), ("南京", 6),
            ("成都", 6), ("武汉", 5), ("重庆", 4), ("苏州", 4), ("青岛", 3), ("西安", 3),
        ]
        return weighted_choice(city_weights, random.Random(9_000_000 + customer_id))
    return stores[(customer_id * 17) % len(stores)]["city"]


def generate_customers_and_member_profiles(stores: list[dict[str, str]]):
    customers: list[dict[str, str]] = []
    member_profiles: dict[int, dict[str, str]] = {}
    member_ids_by_level: dict[str, list[int]] = defaultdict(list)
    active_member_ids_by_level: dict[str, list[int]] = defaultdict(list)
    active_nonmember_ids: list[int] = []

    level_sizes = [
        ("bronze", round(MEMBER_COUNT * 0.60)),
        ("silver", round(MEMBER_COUNT * 0.25)),
        ("gold", round(MEMBER_COUNT * 0.11)),
    ]
    assigned_level_count = sum(count for _, count in level_sizes)
    level_sizes.append(("platinum", MEMBER_COUNT - assigned_level_count))
    level_thresholds: list[tuple[str, int]] = []
    cumulative_count = 0
    for level, count in level_sizes:
        cumulative_count += count
        level_thresholds.append((level, cumulative_count))

    for customer_id in range(1, CUSTOMER_COUNT + 1):
        rng = random.Random(1_000_000 + customer_id)
        city = customer_city(customer_id, stores)
        districts = CITY_DISTRICTS.get(city, FALLBACK_DISTRICTS)
        district = districts[stable_int(f"district:{customer_id}", len(districts))]
        register_day = date(2024, 1, 1) + timedelta(days=stable_int(f"register:{customer_id}", 730))
        register_time = datetime_on_day(register_day, rng, "purchase")
        status = "inactive" if stable_int(f"customer-status:{customer_id}", 100) < 2 else "active"
        name = f"{SURNAMES[stable_int(f'surname:{customer_id}', len(SURNAMES))]}{GIVEN_NAMES[stable_int(f'given:{customer_id}', len(GIVEN_NAMES))]}"
        customers.append(
            {
                "customer_id": str(customer_id),
                "customer_name": name,
                "phone": f"13{customer_id:09d}",
                "email": f"customer{customer_id:06d}@example.local",
                "address": f"{city}市{district}人民路{100 + stable_int(f'addr:{customer_id}', 900)}号",
                "register_time": register_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
            }
        )

        if customer_id <= MEMBER_COUNT:
            level = "platinum"
            for candidate, threshold in level_thresholds:
                if customer_id <= threshold:
                    level = candidate
                    break
            join_day = max(register_day, date(2024, 1, 1)) + timedelta(days=stable_int(f"join:{customer_id}", 90))
            if join_day > date(2025, 12, 31):
                join_day = date(2025, 12, 31) - timedelta(days=stable_int(f"join-back:{customer_id}", 120))
            member_profiles[customer_id] = {
                "customer_id": str(customer_id),
                "member_no": f"M2026{customer_id:06d}",
                "level": level,
                "points": "0",
                "join_date": join_day.isoformat(),
            }
            member_ids_by_level[level].append(customer_id)
            if status == "active":
                active_member_ids_by_level[level].append(customer_id)
        elif status == "active":
            active_nonmember_ids.append(customer_id)

    return customers, member_profiles, member_ids_by_level, active_member_ids_by_level, active_nonmember_ids


def repeated_member_pool(active_member_ids_by_level: dict[str, list[int]]) -> list[int]:
    weights = {"bronze": 3, "silver": 6, "gold": 12, "platinum": 24}
    pool: list[int] = []
    for level, ids in active_member_ids_by_level.items():
        for customer_id in ids:
            pool.extend([customer_id] * weights[level])
    return pool


def store_daily_base(store: dict[str, str]) -> float:
    store_id = int(store["store_id"])
    city_factor = CITY_FACTORS.get(store["city"], 0.88)
    if store_id in FLAGSHIP_STORE_IDS:
        base = 68 + stable_int(f"flagship-base:{store_id}", 24)
    else:
        base = 22 + stable_int(f"standard-base:{store_id}", 18)
    return base * city_factor


def sale_count_for_store_day(store: dict[str, str], day: date, rng: random.Random) -> int:
    mean = store_daily_base(store) * MONTH_FACTORS[day.month] * WEEKDAY_FACTORS[day.weekday()]
    if day in {date(2026, 1, 1), date(2026, 5, 1), date(2026, 6, 18)}:
        mean *= 1.35
    if date(2026, 2, 16) <= day <= date(2026, 2, 22):
        mean *= 0.68
    spread = max(2.0, math.sqrt(mean) * 0.72)
    return max(0, int(rng.gauss(mean, spread)))


def line_count_for_sale(rng: random.Random) -> int:
    return int(weighted_choice([("1", 54), ("2", 30), ("3", 11), ("4", 4), ("5", 1)], rng))


def quantity_for(product: ProductInfo, rng: random.Random) -> int:
    if product.is_book:
        if product.top_category == "教材教辅":
            return int(weighted_choice([("1", 78), ("2", 17), ("3", 5)], rng))
        return int(weighted_choice([("1", 94), ("2", 5), ("3", 1)], rng))
    if product.top_category in {"办公用纸", "文件管理"}:
        return int(weighted_choice([("1", 38), ("2", 30), ("3", 18), ("4", 9), ("5", 5)], rng))
    return int(weighted_choice([("1", 46), ("2", 29), ("3", 15), ("4", 7), ("5", 3)], rng))


def pick_customer(
    rng: random.Random,
    member_pool: list[int],
    active_nonmember_ids: list[int],
    member_profiles: dict[int, dict[str, str]],
) -> tuple[str, str | None]:
    segment = weighted_choice([("member", 58), ("customer", 17), ("guest", 25)], rng)
    if segment == "guest":
        return "", None
    if segment == "member":
        customer_id = member_pool[rng.randrange(len(member_pool))]
        return str(customer_id), member_profiles[customer_id]["level"]
    customer_id = active_nonmember_ids[rng.randrange(len(active_nonmember_ids))]
    return str(customer_id), None


def discount_bps_for(level: str | None, total_cents: int, rng: random.Random) -> int:
    bps = MEMBER_DISCOUNT_BPS.get(level or "", 0)
    if total_cents >= 30_000:
        bps += 150
    if rng.random() < 0.10:
        bps += int(weighted_choice([("100", 4), ("200", 4), ("300", 2)], rng))
    return min(bps, 1_500)


def generate_sales(
    stores: list[dict[str, str]],
    products: dict[int, ProductInfo],
    store_sales_pools: dict[int, WeightedPool],
    member_profiles: dict[int, dict[str, str]],
    active_member_ids_by_level: dict[str, list[int]],
    active_nonmember_ids: list[int],
):
    member_pool = repeated_member_pool(active_member_ids_by_level)
    member_spending_cents = Counter()
    member_order_counts = Counter()
    category_sales_cents = Counter()
    product_sales_cents = Counter()
    monthly_sales_cents = Counter()
    store_sales_cents = Counter()
    payment_counts = Counter()
    sale_count = 0
    sale_item_count = 0

    sale_path = DATA_DIR / "sale.csv"
    sale_item_path = DATA_DIR / "sale_item.csv"
    with sale_path.open("w", encoding="utf-8", newline="") as sale_file, sale_item_path.open("w", encoding="utf-8", newline="") as item_file:
        sale_writer = csv.DictWriter(sale_file, fieldnames=SALE_FIELDS, lineterminator="\n")
        item_writer = csv.DictWriter(item_file, fieldnames=SALE_ITEM_FIELDS, lineterminator="\n")
        sale_writer.writeheader()
        item_writer.writeheader()

        sale_id = 1
        for day in daterange(SALES_START, SALES_END):
            for store in stores:
                store_id = int(store["store_id"])
                pool = store_sales_pools[store_id]
                order_count = sale_count_for_store_day(store, day, RNG)
                for _ in range(order_count):
                    customer_id, level = pick_customer(RNG, member_pool, active_nonmember_ids, member_profiles)
                    used_products: set[int] = set()
                    line_rows: list[dict[str, str]] = []
                    total_cents = 0
                    for line_no in range(1, line_count_for_sale(RNG) + 1):
                        product_id = pool.choose(RNG)
                        retry_count = 0
                        while product_id in used_products and retry_count < 4:
                            product_id = pool.choose(RNG)
                            retry_count += 1
                        used_products.add(product_id)
                        product = products[product_id]
                        quantity = quantity_for(product, RNG)
                        line_amount_cents = product.price_cents * quantity
                        total_cents += line_amount_cents
                        line_rows.append(
                            {
                                "sale_id": str(sale_id),
                                "line_no": str(line_no),
                                "product_id": str(product_id),
                                "quantity": str(quantity),
                                "unit_price": money(product.price_cents),
                                "line_amount": money(line_amount_cents),
                            }
                        )
                        category_sales_cents[product.leaf_category] += line_amount_cents
                        product_sales_cents[product_id] += line_amount_cents

                    discount_cents = round(total_cents * discount_bps_for(level, total_cents, RNG) / 10_000)
                    actual_cents = total_cents - discount_cents
                    sale_time = datetime_on_day(day, RNG, "sale")
                    payment_method = weighted_choice(PAYMENT_METHODS, RNG)
                    sale_writer.writerow(
                        {
                            "sale_id": str(sale_id),
                            "store_id": str(store_id),
                            "customer_id": customer_id,
                            "sale_time": sale_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "payment_method": payment_method,
                            "total_amount": money(total_cents),
                            "discount_amount": money(discount_cents),
                            "actual_amount": money(actual_cents),
                        }
                    )
                    item_writer.writerows(line_rows)

                    sale_count += 1
                    sale_item_count += len(line_rows)
                    payment_counts[payment_method] += 1
                    monthly_sales_cents[day.strftime("%Y-%m")] += actual_cents
                    store_sales_cents[store_id] += actual_cents
                    if customer_id and level:
                        member_spending_cents[int(customer_id)] += actual_cents
                        member_order_counts[int(customer_id)] += 1
                    sale_id += 1

    return {
        "sale_count": sale_count,
        "sale_item_count": sale_item_count,
        "member_spending_cents": member_spending_cents,
        "member_order_counts": member_order_counts,
        "category_sales_cents": category_sales_cents,
        "product_sales_cents": product_sales_cents,
        "monthly_sales_cents": monthly_sales_cents,
        "store_sales_cents": store_sales_cents,
        "payment_counts": payment_counts,
    }


def finalize_members(member_profiles: dict[int, dict[str, str]], sales_stats: dict[str, object]) -> list[dict[str, str]]:
    spending: Counter[int] = sales_stats["member_spending_cents"]  # type: ignore[assignment]
    order_counts: Counter[int] = sales_stats["member_order_counts"]  # type: ignore[assignment]
    rows: list[dict[str, str]] = []
    for customer_id, profile in member_profiles.items():
        level = profile["level"]
        earned_points = spending[customer_id] // 100
        repeat_bonus = order_counts[customer_id] * {"bronze": 5, "silver": 9, "gold": 15, "platinum": 25}[level]
        profile = dict(profile)
        profile["points"] = str(LEVEL_BASE_POINTS[level] + earned_points + repeat_bonus + stable_int(f"points:{customer_id}", 500))
        rows.append(profile)
    return rows


def month_starts(start: date, end: date) -> list[date]:
    months: list[date] = []
    current = date(start.year, start.month, 1)
    while current <= end:
        months.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def random_day_in_month(month_start: date, end: date, rng: random.Random) -> date:
    if month_start.month == 12:
        next_month = date(month_start.year + 1, 1, 1)
    else:
        next_month = date(month_start.year, month_start.month + 1, 1)
    month_end = min(end, next_month - timedelta(days=1))
    if month_start < PROCUREMENT_START:
        month_start = PROCUREMENT_START
    return month_start + timedelta(days=rng.randint(0, (month_end - month_start).days))


def purchase_order_count(store: dict[str, str], month_start: date) -> int:
    store_id = int(store["store_id"])
    base = 10 + stable_int(f"po-flagship:{store_id}:{month_start}", 5) if store_id in FLAGSHIP_STORE_IDS else 4 + stable_int(f"po-standard:{store_id}:{month_start}", 4)
    return max(1, round(base * MONTH_FACTORS[month_start.month]))


def choose_supplier_for_store(store_id: int, store_supplier_products: dict[tuple[int, int], list[int]], rng: random.Random) -> int:
    choices: list[tuple[str, int]] = []
    for supplier_id in range(1, 16):
        count = len(store_supplier_products.get((store_id, supplier_id), []))
        if count == 0:
            continue
        weight = max(1, round(math.sqrt(count)))
        if supplier_id == 15:
            weight = max(1, round(weight * 0.95))
        choices.append((str(supplier_id), weight))
    return int(weighted_choice(choices, rng))


def purchase_quantity(product: ProductInfo, supplier_id: int, month_start: date, rng: random.Random) -> int:
    month_boost = 1.15 if month_start.month in {12, 1, 6} else 1.0
    if supplier_id == 15:
        base = int(weighted_choice([("12", 28), ("24", 35), ("48", 24), ("72", 10), ("120", 3)], rng))
    elif product.top_category == "教材教辅":
        base = int(weighted_choice([("20", 30), ("40", 35), ("80", 22), ("120", 10), ("200", 3)], rng))
    elif heat_multiplier(product.product_id) >= 24:
        base = int(weighted_choice([("12", 25), ("24", 32), ("48", 30), ("80", 10), ("120", 3)], rng))
    else:
        base = int(weighted_choice([("5", 28), ("10", 34), ("20", 25), ("40", 10), ("60", 3)], rng))
    return max(1, round(base * month_boost))


def generate_procurement(
    stores: list[dict[str, str]],
    products: dict[int, ProductInfo],
    store_supplier_products: dict[tuple[int, int], list[int]],
    supply_prices: dict[tuple[int, int], int],
):
    po_path = DATA_DIR / "purchase_order.csv"
    po_item_path = DATA_DIR / "purchase_order_item.csv"
    stock_in_path = DATA_DIR / "stock_in.csv"
    stock_in_item_path = DATA_DIR / "stock_in_item.csv"

    purchase_counts = Counter()
    supplier_amounts = Counter()
    monthly_purchase_cents = Counter()

    with (
        po_path.open("w", encoding="utf-8", newline="") as po_file,
        po_item_path.open("w", encoding="utf-8", newline="") as po_item_file,
        stock_in_path.open("w", encoding="utf-8", newline="") as stock_file,
        stock_in_item_path.open("w", encoding="utf-8", newline="") as stock_item_file,
    ):
        po_writer = csv.DictWriter(po_file, fieldnames=PURCHASE_ORDER_FIELDS, lineterminator="\n")
        po_item_writer = csv.DictWriter(po_item_file, fieldnames=PURCHASE_ORDER_ITEM_FIELDS, lineterminator="\n")
        stock_writer = csv.DictWriter(stock_file, fieldnames=STOCK_IN_FIELDS, lineterminator="\n")
        stock_item_writer = csv.DictWriter(stock_item_file, fieldnames=STOCK_IN_ITEM_FIELDS, lineterminator="\n")
        po_writer.writeheader()
        po_item_writer.writeheader()
        stock_writer.writeheader()
        stock_item_writer.writeheader()

        purchase_order_id = 1
        stock_in_id = 1
        for month_start in month_starts(PROCUREMENT_START, PROCUREMENT_END):
            for store in stores:
                store_id = int(store["store_id"])
                for _ in range(purchase_order_count(store, month_start)):
                    supplier_id = choose_supplier_for_store(store_id, store_supplier_products, RNG)
                    product_pool = store_supplier_products[(store_id, supplier_id)]
                    if supplier_id == 15:
                        line_count = min(len(product_pool), RNG.randint(18, 34))
                    else:
                        line_count = min(len(product_pool), RNG.randint(8, 22))
                    product_ids = RNG.sample(product_pool, line_count)
                    order_day = random_day_in_month(month_start, PROCUREMENT_END, RNG)
                    order_time = datetime_on_day(order_day, RNG, "purchase")
                    line_rows: list[dict[str, str]] = []
                    total_cents = 0
                    for line_no, product_id in enumerate(product_ids, start=1):
                        product = products[product_id]
                        price_cents = supply_prices[(supplier_id, product_id)]
                        quantity = purchase_quantity(product, supplier_id, month_start, RNG)
                        line_amount_cents = price_cents * quantity
                        total_cents += line_amount_cents
                        line_rows.append(
                            {
                                "purchase_order_id": str(purchase_order_id),
                                "line_no": str(line_no),
                                "product_id": str(product_id),
                                "quantity": str(quantity),
                                "purchase_price": money(price_cents),
                                "line_amount": money(line_amount_cents),
                            }
                        )

                    late_june = order_day >= date(2026, 6, 24)
                    if late_june:
                        status = weighted_choice([("received", 64), ("approved", 24), ("submitted", 7), ("cancelled", 5)], RNG)
                    else:
                        status = weighted_choice([("received", 92), ("approved", 4), ("submitted", 2), ("cancelled", 2)], RNG)

                    po_writer.writerow(
                        {
                            "purchase_order_id": str(purchase_order_id),
                            "supplier_id": str(supplier_id),
                            "store_id": str(store_id),
                            "created_by": "2",
                            "order_time": order_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "status": status,
                            "total_amount": money(total_cents),
                        }
                    )
                    po_item_writer.writerows(line_rows)

                    purchase_counts[status] += 1
                    supplier_amounts[supplier_id] += total_cents
                    monthly_purchase_cents[order_day.strftime("%Y-%m")] += total_cents

                    if status == "received":
                        inbound_day = min(PROCUREMENT_END, order_day + timedelta(days=RNG.randint(1, 5)))
                        inbound_time = datetime_on_day(inbound_day, RNG, "purchase")
                        stock_writer.writerow(
                            {
                                "stock_in_id": str(stock_in_id),
                                "purchase_order_id": str(purchase_order_id),
                                "store_id": str(store_id),
                                "operator_id": "2",
                                "inbound_time": inbound_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "status": "approved",
                            }
                        )
                        for row in line_rows:
                            stock_item_writer.writerow(
                                {
                                    "stock_in_id": str(stock_in_id),
                                    "line_no": row["line_no"],
                                    "product_id": row["product_id"],
                                    "quantity": row["quantity"],
                                    "unit_cost": row["purchase_price"],
                                    "line_amount": row["line_amount"],
                                }
                            )
                        stock_in_id += 1

                    purchase_order_id += 1

    return {
        "purchase_order_count": purchase_order_id - 1,
        "stock_in_count": stock_in_id - 1,
        "purchase_counts": purchase_counts,
        "supplier_amounts": supplier_amounts,
        "monthly_purchase_cents": monthly_purchase_cents,
    }


def write_audit_report(
    customers: list[dict[str, str]],
    member_rows: list[dict[str, str]],
    sales_stats: dict[str, object],
    procurement_stats: dict[str, object],
) -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    category_sales: Counter[str] = sales_stats["category_sales_cents"]  # type: ignore[assignment]
    product_sales: Counter[int] = sales_stats["product_sales_cents"]  # type: ignore[assignment]
    monthly_sales: Counter[str] = sales_stats["monthly_sales_cents"]  # type: ignore[assignment]
    payment_counts: Counter[str] = sales_stats["payment_counts"]  # type: ignore[assignment]
    purchase_counts: Counter[str] = procurement_stats["purchase_counts"]  # type: ignore[assignment]
    supplier_amounts: Counter[int] = procurement_stats["supplier_amounts"]  # type: ignore[assignment]
    monthly_purchase: Counter[str] = procurement_stats["monthly_purchase_cents"]  # type: ignore[assignment]

    category_rows = [
        {"category_name": name, "sales_amount": money(amount)}
        for name, amount in category_sales.most_common(30)
    ]
    write_rows(CLEAN_DIR / "business_activity_category_sales_top30.csv", ["category_name", "sales_amount"], category_rows)

    monthly_rows = []
    for month in sorted(set(monthly_sales) | set(monthly_purchase)):
        monthly_rows.append(
            {
                "month": month,
                "sales_amount": money(monthly_sales[month]),
                "purchase_amount": money(monthly_purchase[month]),
            }
        )
    write_rows(CLEAN_DIR / "business_activity_monthly_summary.csv", ["month", "sales_amount", "purchase_amount"], monthly_rows)

    report_path = CLEAN_DIR / "business_activity_audit.md"
    member_levels = Counter(row["level"] for row in member_rows)
    active_customers = sum(1 for row in customers if row["status"] == "active")
    top_product_amounts = [amount for _, amount in product_sales.most_common(10)]
    top_category_amounts = [amount for _, amount in category_sales.most_common(10)]
    with report_path.open("w", encoding="utf-8", newline="\n") as report:
        report.write("# 业务流水种子数据审计\n\n")
        report.write(f"- 客户数：{len(customers):,}，活跃客户：{active_customers:,}\n")
        report.write(f"- 会员数：{len(member_rows):,}，会员占客户比例：{len(member_rows) / len(customers):.2%}\n")
        report.write("- 会员等级：")
        report.write("，".join(f"{level} {count:,}" for level, count in sorted(member_levels.items())))
        report.write("\n")
        report.write(f"- 销售单：{sales_stats['sale_count']:,}，销售明细：{sales_stats['sale_item_count']:,}\n")
        report.write(f"- 采购单：{procurement_stats['purchase_order_count']:,}，入库单：{procurement_stats['stock_in_count']:,}\n")
        report.write("- 支付方式订单数：")
        report.write("，".join(f"{method} {count:,}" for method, count in payment_counts.most_common()))
        report.write("\n")
        report.write("- 采购状态：")
        report.write("，".join(f"{status} {count:,}" for status, count in purchase_counts.most_common()))
        report.write("\n")
        report.write(f"- 销售额 Top10 商品金额互异数量：{len(set(top_product_amounts))}/10\n")
        report.write(f"- 销售额 Top10 分类最高/最低金额比：{(max(top_category_amounts) / min(top_category_amounts)):.2f}\n")
        report.write("- 采购额 Top5 供应商：")
        report.write("，".join(f"{supplier_id}: {money(amount)}" for supplier_id, amount in supplier_amounts.most_common(5)))
        report.write("\n")


def rebuild_business_activity() -> None:
    stores, products, store_sales_pools, store_supplier_products, supply_prices = load_business_base()
    customers, member_profiles, _, active_member_ids_by_level, active_nonmember_ids = generate_customers_and_member_profiles(stores)
    write_rows(DATA_DIR / "customer.csv", CUSTOMER_FIELDS, customers)

    sales_stats = generate_sales(
        stores,
        products,
        store_sales_pools,
        member_profiles,
        active_member_ids_by_level,
        active_nonmember_ids,
    )
    member_rows = finalize_members(member_profiles, sales_stats)
    write_rows(DATA_DIR / "member.csv", MEMBER_FIELDS, member_rows)

    procurement_stats = generate_procurement(stores, products, store_supplier_products, supply_prices)
    write_audit_report(customers, member_rows, sales_stats, procurement_stats)

    print(f"Wrote {len(customers):,} customers and {len(member_rows):,} members.")
    print(f"Wrote {sales_stats['sale_count']:,} sales and {sales_stats['sale_item_count']:,} sale items.")
    print(f"Wrote {procurement_stats['purchase_order_count']:,} purchase orders and {procurement_stats['stock_in_count']:,} stock-in records.")
    print(f"Wrote business activity audit files under {CLEAN_DIR}.")


if __name__ == "__main__":
    rebuild_business_activity()
