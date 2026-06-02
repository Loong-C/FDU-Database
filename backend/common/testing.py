from django.db import connection

from common.sql import (
    BUSINESS_TABLES,
    BUSINESS_VIEWS,
    load_csv_seed_data,
    load_sql_script,
    split_sql_statements,
    strip_use_statements,
)


def execute_script(sql: str) -> None:
    cleaned_sql = strip_use_statements(sql)
    with connection.cursor() as cursor:
        for statement in split_sql_statements(cleaned_sql):
            cursor.execute(statement)


def reset_business_schema() -> None:
    with connection.cursor() as cursor:
        for view_name in BUSINESS_VIEWS:
            cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table_name in BUSINESS_TABLES:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def bootstrap_business_schema(include_seed: bool = True, include_views: bool = True) -> None:
    reset_business_schema()
    execute_script(load_sql_script("create_tables.sql"))
    if include_seed:
        load_csv_seed_data(connection)
    if include_views:
        execute_script(load_sql_script("views_or_reports.sql"))
