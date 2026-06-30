from rag_searcher.db.pool import pool


def delete_expired_page_links(page_id: int, expiry_days: int) -> None:
    with pool.connection() as conn:
        conn.execute(
            """
            DELETE FROM link
            WHERE page_id = %s
              AND created_at < NOW() - INTERVAL '1 day' * %s
            """,
            (page_id, expiry_days),
        )

def save_links(page_id: int, links_dict: dict[str, str]) -> None:
    rows = [(url, title, page_id) for url, title in links_dict.items()]
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO link (url, title, page_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (page_id, url) DO NOTHING
                """,
                rows,
            )
