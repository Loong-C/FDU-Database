import pymysql
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from common.sql import load_sql_script, split_sql_statements, strip_use_statements


class Command(BaseCommand):
    help = "Bootstrap the MySQL business database from the SQL scripts."

    def add_arguments(self, parser):
        parser.add_argument("--seed", action="store_true", help="Load sample data.")
        parser.add_argument("--views", action="store_true", help="Create analytics views.")

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.mysql":
            raise CommandError("bootstrap_business_db only supports MySQL.")

        connection_kwargs = {
            "host": database["HOST"],
            "port": int(database["PORT"]),
            "user": database["USER"],
            "password": database["PASSWORD"],
            "charset": database["OPTIONS"].get("charset", "utf8mb4"),
            "autocommit": False,
        }

        self.stdout.write("Creating database...")
        with pymysql.connect(**connection_kwargs) as conn:
            self._execute_script(conn, load_sql_script("create_database.sql"))

        self.stdout.write(f"Initializing schema in {database['NAME']}...")
        with pymysql.connect(database=database["NAME"], **connection_kwargs) as conn:
            self._execute_script(conn, load_sql_script("create_tables.sql"))
            if options["seed"]:
                self.stdout.write("Loading sample data...")
                self._execute_script(conn, load_sql_script("insert_sample_data.sql"))
            if options["views"]:
                self.stdout.write("Creating analytics views...")
                self._execute_script(conn, load_sql_script("views_or_reports.sql"))

        self.stdout.write(self.style.SUCCESS("Business database bootstrapped successfully."))

    def _execute_script(self, connection, sql: str) -> None:
        cleaned_sql = strip_use_statements(sql)
        with connection.cursor() as cursor:
            for statement in split_sql_statements(cleaned_sql):
                cursor.execute(statement)
        connection.commit()
