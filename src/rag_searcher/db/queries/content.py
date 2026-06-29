from rag_searcher.db.pool import pool


def set_page_contents_pending(page_id: int) -> None:
    with pool.connection() as conn:
        with conn.transaction():
            conn.execute(
                """
                INSERT INTO content (link_id, status_id)
                SELECT l.id, (SELECT id FROM status WHERE name = 'pending')
                FROM link l
                WHERE l.page_id = %s
                  AND NOT EXISTS (
                      SELECT 1 FROM content c WHERE c.link_id = l.id
                  )
                """,
                (page_id,),
            )

            conn.execute(
                """
                UPDATE content
                SET status_id = (SELECT id FROM status WHERE name = 'pending')
                WHERE link_id IN (SELECT id FROM link WHERE page_id = %s)
                  AND status_id != (SELECT id FROM status WHERE name = 'completed')
                """,
                (page_id,),
            )

            conn.execute(
                """
                UPDATE content
                SET status_id = (SELECT id FROM status WHERE name = 'pending')
                WHERE link_id IN (SELECT id FROM link WHERE page_id = %s)
                  AND status_id = (SELECT id FROM status WHERE name = 'completed')
                  AND content IS NULL
                """,
                (page_id,),
            )
