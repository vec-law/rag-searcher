from rag_searcher.db.pool import pool


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

def insert_page(url: str, page_type_id: int, page_max: int, fetcher_id: int) -> int:
    with pool.connection() as conn:
        row = conn.execute(
            """
            INSERT INTO page (url, page_type_id, page_max, fetcher_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (url, page_type_id, page_max, fetcher_id),
        ).fetchone()

    return row[0]

def get_page_settings(page_id: int) -> tuple[str, int, str, str]:
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT p.url, p.page_max, pt.name, f.name
            FROM page p
            JOIN page_type pt ON pt.id = p.page_type_id
            JOIN fetcher f ON f.id = p.fetcher_id
            WHERE p.id = %s
            """,
            (page_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Brak page o id: {page_id}")

    return row
