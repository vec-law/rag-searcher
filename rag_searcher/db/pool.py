from psycopg_pool import ConnectionPool

from rag_searcher.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

pool = ConnectionPool(
    conninfo=f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}",
    min_size=2,
    max_size=10,
    open=False,
    kwargs={"autocommit": True}
)
