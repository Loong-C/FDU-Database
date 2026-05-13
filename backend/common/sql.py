from django.conf import settings


SQL_DIR = settings.REPO_ROOT / "sql"
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


def load_sql_script(filename: str) -> str:
    return (SQL_DIR / filename).read_text(encoding="utf-8")


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
