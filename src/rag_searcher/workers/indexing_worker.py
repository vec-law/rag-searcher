import time
import logging
from concurrent.futures import ThreadPoolExecutor

from rag_searcher.db.pool import pool
from rag_searcher.services.page_setup import setup_page
from rag_searcher.services.indexing.page import (
    delete_expired_page_links, fetch_page_links,
    set_page_contents_pending, get_page_content_ids,
)
from rag_searcher.services.indexing.content import fetch_content
from rag_searcher.services.embedder import get_compute_embedding

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    pool.open()
    try:
        page_id = setup_page()
        compute_embedding = get_compute_embedding(page_id)

        while True:
            try:
                delete_expired_page_links(page_id)
                fetch_page_links(page_id)
                set_page_contents_pending(page_id)

                content_ids = get_page_content_ids(page_id)
                with ThreadPoolExecutor(max_workers=2) as executor:
                    executor.map(fetch_content, content_ids)

            except Exception:
                logger.exception("Błąd w pętli indeksującej")
                time.sleep(60)
                continue

            time.sleep(3600)

    finally:
        pool.close()


if __name__ == "__main__":
    main()
