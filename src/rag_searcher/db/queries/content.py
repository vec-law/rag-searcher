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

def get_page_content_ids(page_id: int) -> list[int]:
    with pool.connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id
            FROM content c
            JOIN link l ON l.id = c.link_id
            WHERE l.page_id = %s
              AND c.status_id = (SELECT id FROM status WHERE name = 'pending')
            """,
            (page_id,),
        ).fetchall()

    return [row[0] for row in rows]

def get_content_params(content_id: int) -> tuple[str, str]:
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT f.name, l.url
            FROM content c
            JOIN link l ON l.id = c.link_id
            JOIN page p ON p.id = l.page_id
            JOIN fetcher f ON f.id = p.fetcher_id
            WHERE c.id = %s
            """,
            (content_id,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Brak content o id: {content_id}")

    return row

def update_content(content_id: int, content: str | None, status: str) -> None:
    with pool.connection() as conn:
        conn.execute(
            """
            UPDATE content
            SET content = %s,
                status_id = (SELECT id FROM status WHERE name = %s)
            WHERE id = %s
            """,
            (content, status, content_id),
        )
