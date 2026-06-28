from rag_searcher.db.pool import pool


def get_page_id(url, page_type_id, page_max, fetcher_id):
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT id FROM page
            WHERE url = %s AND page_type_id = %s
              AND page_max = %s AND fetcher_id = %s
            """,
            (url, page_type_id, page_max, fetcher_id),
        ).fetchone()

    if row is None:
        return None

    return row[0]

def insert_page(url, page_type_id, page_max, fetcher_id,
                embedding_model_name, embedding_vector_size):
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
