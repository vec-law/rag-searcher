from rag_searcher.db.pool import pool


def get_fetcher_id(name: str) -> int:
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT id FROM fetcher WHERE name = %s",
            (name,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Brak fetcher o nazwie: {name}")

    return row[0]
