from rag_searcher.db.pool import pool


def get_embedding_config_id(model_name: str, vector_size: int) -> int | None:
    with pool.connection() as conn:
        row = conn.execute(
            """
            SELECT id
            FROM embedding_config
            WHERE model_name = %s AND vector_size = %s
            """,
            (model_name, vector_size),
        ).fetchone()

    if row is None:
        return None

    return row[0]

def insert_embedding_config(model_name: str, vector_size: int) -> int:
    with pool.connection() as conn:
        row = conn.execute(
            """
            INSERT INTO embedding_config (model_name, vector_size)
            VALUES (%s, %s)
            RETURNING id
            """,
            (model_name, vector_size),
        ).fetchone()

    return row[0]

def insert_page_embedding_config(page_id: int, embedding_config_id: int) -> None:
    with pool.connection() as conn:
        conn.execute(
            """
            INSERT INTO page_embedding_config (page_id, embedding_config_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (page_id, embedding_config_id),
        )

def insert_embedding_vector_table(embedding_config_id: int) -> None:
    with pool.connection() as conn:
        with conn.transaction():
            row = conn.execute(
                "SELECT vector_size FROM embedding_config WHERE id = %s",
                (embedding_config_id,),
            ).fetchone()

            if row is None:
                raise ValueError(f"Brak embedding_config o id: {embedding_config_id}")

            vector_size = row[0]
            table_name = f"embedding_{embedding_config_id}"

            conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE UNIQUE,
                    embedding VECTOR({vector_size}),
                    status_id INTEGER REFERENCES status(id),
                    created_at TIMESTAMP DEFAULT NOW()
                )
                """
            )

            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_content_id ON {table_name}(content_id)"
            )
            conn.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_status_id ON {table_name}(status_id)"
            )

def get_embedding_config(embedding_config_id: int) -> tuple[str, int] | None:
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT model_name, vector_size FROM embedding_config WHERE id = %s",
            (embedding_config_id,),
        ).fetchone()

    if row is None:
        return None

    return row[0], row[1]

def set_embeddings_pending(page_id: int, embedding_config_id: int) -> None:
    table_name = f"embedding_{embedding_config_id}"

    with pool.connection() as conn:
        with conn.transaction():
            conn.execute(
                f"""
                INSERT INTO {table_name} (content_id, status_id)
                SELECT c.id, (SELECT id FROM status WHERE name = 'pending')
                FROM content c
                JOIN link l ON l.id = c.link_id
                WHERE l.page_id = %s
                  AND c.status_id = (SELECT id FROM status WHERE name = 'completed')
                  AND c.content IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM {table_name} e WHERE e.content_id = c.id
                  )
                """,
                (page_id,),
            )

            conn.execute(
                f"""
                UPDATE {table_name}
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
                f"""
                UPDATE {table_name}
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

def get_embedding_ids(page_id: int, embedding_config_id: int) -> list[int]:
    table_name = f"embedding_{embedding_config_id}"

    with pool.connection() as conn:
        rows = conn.execute(
            f"""
            SELECT e.id
            FROM {table_name} e
            JOIN content c ON c.id = e.content_id
            JOIN link l ON l.id = c.link_id
            WHERE l.page_id = %s
              AND e.status_id = (SELECT id FROM status WHERE name = 'pending')
            """,
            (page_id,),
        ).fetchall()

    return [row[0] for row in rows]

def update_embedding(embedding_id: int, embedding_config_id: int, embedding: str | None, status: str) -> None:
    table_name = f"embedding_{embedding_config_id}"

    with pool.connection() as conn:
        conn.execute(
            f"""
            UPDATE {table_name}
            SET embedding = %s::vector,
                status_id = (SELECT id FROM status WHERE name = %s)
            WHERE id = %s
            """,
            (embedding, status, embedding_id),
        )

def get_embedding_context(embedding_id: int, embedding_config_id: int) -> dict | None:
    table_name = f"embedding_{embedding_config_id}"

    with pool.connection() as conn:
        row = conn.execute(
            f"""
            SELECT l.url, l.title, c.content, s.name
            FROM {table_name} e
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

def get_similar_embedding_ids(
        query_embedding: list[float],
        limit: int | None,
        page_id: int,
        embedding_config_id: int
) -> list[int]:
    pass
