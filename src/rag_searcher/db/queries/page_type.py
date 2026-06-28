from rag_searcher.db.pool import pool


def get_page_type_id(name: str) -> int:
    with pool.connection() as conn:
        row = conn.execute(
            "SELECT id FROM page_type WHERE name = %s",
            (name,),
        ).fetchone()

    if row is None:
        raise ValueError(f"Brak page_type o nazwie: {name}")

    return row[0]
