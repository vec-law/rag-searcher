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
