from rag_searcher.db.pool import pool
from rag_searcher.services.indexing.page_config import get_page


def main():
    pool.open()
    try:
        page = get_page()

        # TODO: pętla indeksacyjna

    finally:
        pool.close()


if __name__ == "__main__":
    main()
