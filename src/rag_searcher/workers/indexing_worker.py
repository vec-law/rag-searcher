import time
import traceback

from rag_searcher.db.pool import pool
from rag_searcher.services.indexing.page import setup_page, delete_expired_page_links, fetch_page_links, set_page_contents_pending


def main():
    pool.open()
    try:
        page_id = setup_page()

        while True:
            try:
                delete_expired_page_links(page_id)
                fetch_page_links(page_id)
                set_page_contents_pending(page_id)

            except Exception:
                traceback.print_exc()
                time.sleep(60)
                continue

            time.sleep(3600)

    finally:
        pool.close()


if __name__ == "__main__":
    main()
