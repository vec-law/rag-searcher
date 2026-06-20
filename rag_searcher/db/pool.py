from psycopg_pool import ConnectionPool

from rag_searcher.config import settings

pool = ConnectionPool(
    conninfo=(
        f"host={settings.db_host} "
        f"port={settings.db_port} "
        f"dbname={settings.db_name} "
        f"user={settings.db_user} "
        f"password={settings.db_password.get_secret_value()}"
    ),
    min_size=2,
    max_size=10,
    open=False,
    kwargs={"autocommit": True},
)
