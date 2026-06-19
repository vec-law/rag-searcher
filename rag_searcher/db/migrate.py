from pathlib import Path

import psycopg

from rag_searcher.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def migrate():
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True
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
