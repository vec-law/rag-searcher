from rag_searcher.db.pool import pool


def set_page_embeddings_pending(page_id: int) -> None:
    with pool.connection() as conn:
        with conn.transaction():
            conn.execute(
                """
                INSERT INTO embedding (content_id, status_id)
                SELECT c.id, (SELECT id FROM status WHERE name = 'pending')
                FROM content c
                JOIN link l ON l.id = c.link_id
                WHERE l.page_id = %s
                  AND c.status_id = (SELECT id FROM status WHERE name = 'completed')
                  AND c.content IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM embedding e WHERE e.content_id = c.id
                  )
                """,
                (page_id,),
            )

            conn.execute(
                """
                UPDATE embedding
                SET status_id = (SELECT id FROM status WHERE name = 'pending')
                WHERE content_id IN (
                    SELECT c.id FROM content c
                    JOIN link l ON l.id = c.link_id
                    WHERE l.page_id = %s
                      AND c.status_id = (SELECT id FROM status WHERE name = 'completed')
                      AND c.content IS NOT NULL
                )
                AND status_id != (SELECT id FROM status WHERE name = 'completed')
                """,
                (page_id,),
            )

            conn.execute(
                """
                UPDATE embedding
                SET status_id = (SELECT id FROM status WHERE name = 'pending')
                WHERE content_id IN (
                    SELECT c.id FROM content c
                    JOIN link l ON l.id = c.link_id
                    WHERE l.page_id = %s
                      AND c.status_id = (SELECT id FROM status WHERE name = 'completed')
                      AND c.content IS NOT NULL
                )
                AND status_id = (SELECT id FROM status WHERE name = 'completed')
                AND embedding IS NULL
                """,
                (page_id,),
            )

def get_embedding_ids(page_id: int) -> list[int]:
    with pool.connection() as conn:
        rows = conn.execute(
            """
            SELECT e.id
            FROM embedding e
            JOIN content c ON c.id = e.content_id
            JOIN link l ON l.id = c.link_id
            WHERE l.page_id = %s
              AND e.status_id = (SELECT id FROM status WHERE name = 'pending')
            """,
            (page_id,),
        ).fetchall()

    return [row[0] for row in rows]

def get_embedding_context(embedding_id: int) -> dict | None:
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT l.url, l.title, c.content, s.name
            FROM embedding e
            JOIN content c ON c.id = e.content_id
            JOIN status s ON s.id = c.status_id
            JOIN link l ON l.id = c.link_id
            WHERE e.id = %s
            """,
            (embedding_id,),
        ).fetchone()

    if row is None:
        return None

    return {"url": row[0], "title": row[1], "content": row[2], "status": row[3]}

def update_embedding(embedding_id: int, embedding: str | None, status: str) -> None:
    with pool.connection() as conn:
        conn.execute(
            """
            UPDATE embedding
            SET embedding = %s::vector,
                status_id = (SELECT id FROM status WHERE name = %s)
            WHERE id = %s
            """,
            (embedding, status, embedding_id),
        )
