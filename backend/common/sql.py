import csv
from dataclasses import dataclass

from django.conf import settings


SQL_DIR = settings.REPO_ROOT / "sql"
CSV_DATA_DIR = SQL_DIR / "data"
BUSINESS_TABLES = [
    "stock_in_item",
    "stock_in",
    "purchase_order_item",
    "purchase_order",
    "role_permission",
    "user_role",
    "permission",
    "role",
    "system_user",
    "inventory",
    "sale_item",
    "sale",
    "member",
    "customer",
    "book_translator",
    "book_author",
    "book",
    "supplier_product",
    "translator",
    "author",
    "product",
    "publisher",
    "category",
    "supplier",
    "store",
]
BUSINESS_VIEWS = [
    "v_store_sales_daily",
    "v_product_sales_rank",
    "v_member_spending_rank",
    "v_category_sales_summary",
    "v_inventory_warning",
    "v_store_inventory_summary",
]


@dataclass(frozen=True)
class CSVSeedFile:
    table: str
    columns: tuple[str, ...]

    @property
    def path(self):
        return CSV_DATA_DIR / f"{self.table}.csv"


CSV_SEED_FILES = [
    CSVSeedFile("store", ("store_id", "store_name", "city", "address", "phone", "manager_name")),
    CSVSeedFile("supplier", ("supplier_id", "supplier_name", "contact_name", "phone", "email", "status")),
    CSVSeedFile("category", ("category_id", "category_name", "parent_category_id")),
    CSVSeedFile(
        "publisher",
        ("publisher_id", "publisher_name", "contact_name", "phone", "email", "address", "country", "website"),
    ),
    CSVSeedFile(
        "product",
        ("product_id", "product_name", "category_id", "unit", "unit_price", "cost_price", "barcode", "status"),
    ),
    CSVSeedFile("book", ("product_id", "isbn", "publisher_id", "publish_date", "edition", "language", "page_count")),
    CSVSeedFile("author", ("author_id", "author_name", "country")),
    CSVSeedFile("translator", ("translator_id", "translator_name", "country")),
    CSVSeedFile("book_author", ("product_id", "author_id", "author_order")),
    CSVSeedFile("book_translator", ("product_id", "translator_id")),
    CSVSeedFile("supplier_product", ("supplier_id", "product_id", "supply_price", "min_order_qty", "is_primary")),
    CSVSeedFile("customer", ("customer_id", "customer_name", "phone", "email", "address", "register_time", "status")),
    CSVSeedFile("member", ("customer_id", "member_no", "level", "points", "join_date")),
    CSVSeedFile("system_user", ("user_id", "username", "password_hash", "real_name", "phone", "email", "status")),
    CSVSeedFile("role", ("role_id", "role_name", "role_desc")),
    CSVSeedFile("permission", ("permission_id", "permission_code", "permission_name", "module_name")),
    CSVSeedFile("user_role", ("user_id", "role_id")),
    CSVSeedFile("role_permission", ("role_id", "permission_id")),
    CSVSeedFile(
        "purchase_order",
        ("purchase_order_id", "supplier_id", "store_id", "created_by", "order_time", "status", "total_amount"),
    ),
    CSVSeedFile(
        "purchase_order_item",
        ("purchase_order_id", "line_no", "product_id", "quantity", "purchase_price", "line_amount"),
    ),
    CSVSeedFile("stock_in", ("stock_in_id", "purchase_order_id", "store_id", "operator_id", "inbound_time", "status")),
    CSVSeedFile("stock_in_item", ("stock_in_id", "line_no", "product_id", "quantity", "unit_cost", "line_amount")),
    CSVSeedFile("inventory", ("store_id", "product_id", "stock_qty", "safety_stock_qty")),
    CSVSeedFile(
        "sale",
        ("sale_id", "store_id", "customer_id", "sale_time", "payment_method", "total_amount", "discount_amount", "actual_amount"),
    ),
    CSVSeedFile("sale_item", ("sale_id", "line_no", "product_id", "quantity", "unit_price", "line_amount")),
]


def load_sql_script(filename: str) -> str:
    return (SQL_DIR / filename).read_text(encoding="utf-8")


def load_csv_seed_data(connection) -> dict[str, int]:
    imported_rows: dict[str, int] = {}
    with connection.cursor() as cursor:
        for seed_file in CSV_SEED_FILES:
            rows = _read_csv_rows(seed_file)
            if rows:
                columns = ", ".join(f"`{column}`" for column in seed_file.columns)
                placeholders = ", ".join(["%s"] * len(seed_file.columns))
                cursor.executemany(
                    f"INSERT INTO `{seed_file.table}` ({columns}) VALUES ({placeholders})",
                    rows,
                )
            imported_rows[seed_file.table] = len(rows)
    return imported_rows


def _read_csv_rows(seed_file: CSVSeedFile) -> list[tuple[str | None, ...]]:
    with seed_file.path.open(encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = tuple(reader.fieldnames or ())
        if fieldnames != seed_file.columns:
            raise ValueError(
                f"{seed_file.path.name} columns must be {seed_file.columns}, got {fieldnames}."
            )
        return [
            tuple(row[column] if row[column] != "" else None for column in seed_file.columns)
            for row in reader
        ]


def split_sql_statements(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    escape = False

    for char in sql:
        if char == "\\" and (in_single or in_double):
            current.append(char)
            escape = not escape
            continue
        if char == "'" and not in_double and not escape:
            in_single = not in_single
        elif char == '"' and not in_single and not escape:
            in_double = not in_double

        if char == ";" and not in_single and not in_double:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)
        if char != "\\":
            escape = False

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)
    return statements


def strip_use_statements(sql: str) -> str:
    kept_lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("USE "):
            continue
        kept_lines.append(line)
    return "\n".join(kept_lines)
