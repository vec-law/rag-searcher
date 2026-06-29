import time
import traceback

from rag_searcher.db.pool import pool
from rag_searcher.services.indexing.page import get_page, delete_expired_page_links, set_page_contents_pending


def main():
    pool.open()
    try:
        page = get_page()

        while True:
            try:
                delete_expired_page_links(page.id)
                set_page_contents_pending(page.id)
            except Exception:
                traceback.print_exc()
                time.sleep(60)
                continue

            time.sleep(3600)

    finally:
        pool.close()


if __name__ == "__main__":
    main()
