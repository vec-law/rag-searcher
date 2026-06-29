from rag_searcher.db.pool import pool
from rag_searcher.models.page import Page


def get_page_id(url: str, page_type_id: int, page_max: int, fetcher_id: int) -> int | None:
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM page
            WHERE url = %s AND page_type_id = %s
              AND page_max = %s AND fetcher_id = %s
            """,
            (url, page_type_id, page_max, fetcher_id),
        ).fetchone()

    if row is None:
        return None

    return row[0]

def insert_page(url: str, page_type_id: int, page_max: int, fetcher_id: int,
                embedding_model_name: str, embedding_vector_size: int) -> int:
    with pool.connection() as conn:
        row = conn.execute(
            """
            INSERT INTO page (url, page_type_id, page_max, fetcher_id,
                              embedding_model_name, embedding_vector_size)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (url, page_type_id, page_max, fetcher_id,
             embedding_model_name, embedding_vector_size),
        ).fetchone()

    return row[0]

def update_page_embedding_config(embedding_model_name, embedding_vector_size):
    with pool.connection() as conn:
        with conn.transaction():
            conn.execute("DELETE FROM embedding")

            conn.execute(
                f"ALTER TABLE embedding ALTER COLUMN embedding TYPE VECTOR({embedding_vector_size})"
            )

            conn.execute(
                """
                UPDATE page
                SET embedding_model_name = %s, embedding_vector_size = %s
                """,
                (embedding_model_name, embedding_vector_size),
            )

def get_page_embedding_config(page_id: int) -> tuple[str, int]:
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT embedding_model_name, embedding_vector_size
            FROM page
            WHERE id = %s
            """,
            (page_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Brak page o id: {page_id}")

    return row