from rag_searcher.db.pool import pool
from rag_searcher.services.indexing.page import get_page, delete_expired_page_links


def main():
    pool.open()
    try:
        page = get_page()
        delete_expired_page_links(page.id)

        # TODO: pętla indeksacyjna

    finally:
        pool.close()


if __name__ == "__main__":
    main()
