from pathlib import Path

import psycopg

from rag_searcher.config import settings


def migrate():
    conn = psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password.get_secret_value(),
        autocommit=True,
    )

    migrations_dir = Path(__file__).parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    for migration_file in migration_files:
        print(f"Executing {migration_file.name}...")
        sql = migration_file.read_text()
        conn.execute(sql)
        print(f"Done {migration_file.name}")

    conn.close()
    print("All migrations executed.")


migrate()
