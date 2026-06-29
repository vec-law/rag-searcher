from rag_searcher.db.pool import pool
from rag_searcher.models.page import Page


def get_page(url, page_type_id, page_max, fetcher_id):
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT id, url, page_type_id, page_max, fetcher_id,
                   embedding_model_name, embedding_vector_size
            FROM page
            WHERE url = %s AND page_type_id = %s
              AND page_max = %s AND fetcher_id = %s
            """,
            (url, page_type_id, page_max, fetcher_id),
        ).fetchone()

    if row is None:
        return None

    return Page(*row)

def insert_page(url, page_type_id, page_max, fetcher_id,
                embedding_model_name, embedding_vector_size):
    with pool.connection() as conn:
        row = conn.execute(
            """
            INSERT INTO page (url, page_type_id, page_max, fetcher_id,
                              embedding_model_name, embedding_vector_size)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, url, page_type_id, page_max, fetcher_id,
                      embedding_model_name, embedding_vector_size
            """,
            (url, page_type_id, page_max, fetcher_id,
             embedding_model_name, embedding_vector_size),
        ).fetchone()

    return Page(*row)

def update_page_embedding_config(page_id, embedding_model_name, embedding_vector_size):
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

            row = conn.execute(
                """
                SELECT id, url, page_type_id, page_max, fetcher_id,
                       embedding_model_name, embedding_vector_size
                FROM page
                WHERE id = %s
                """,
                (page_id,),
            ).fetchone()
    return Page(*row)
