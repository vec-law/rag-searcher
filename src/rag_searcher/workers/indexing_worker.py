import time
import logging

from rag_searcher.db.pool import pool
from rag_searcher.services.indexing.page import (
    setup_page, delete_expired_page_links, fetch_page_links,
    set_page_contents_pending, get_page_content_ids,
)

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    pool.open()
    try:
        page_id = setup_page()

        while True:
            try:
                delete_expired_page_links(page_id)
                fetch_page_links(page_id)
                set_page_contents_pending(page_id)

                content_ids = get_page_content_ids(page_id)

            except Exception:
                logger.exception("Błąd w pętli indeksacyjnej")
                time.sleep(60)
                continue

            time.sleep(3600)

    finally:
        pool.close()


if __name__ == "__main__":
    main()
