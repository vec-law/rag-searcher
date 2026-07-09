import time
import logging
from concurrent.futures import ThreadPoolExecutor

from rag_searcher.db.pool import pool
from rag_searcher.services.initialization import init
from rag_searcher.services.indexing.page import (
    delete_expired_page_links, fetch_page_links,
    set_page_contents_pending, get_page_content_ids,
)
from rag_searcher.services.indexing.content import fetch_content
from rag_searcher.services.indexing.embedding import (
    set_embeddings_pending, compute_embedding,
    get_embedding_ids
)
from rag_searcher.services.embedder import get_embed

logging.basicConfig(level=logging.WARNING)
logging.getLogger("rag_searcher").setLevel(logging.INFO)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub.utils._http").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

def main():
    pool.open()
    try:
        page_id, embedding_config_id = init()
        embed = get_embed(embedding_config_id)

        while True:
            try:
                delete_expired_page_links(page_id)
                fetch_page_links(page_id)
                
                set_page_contents_pending(page_id)
                content_ids = get_page_content_ids(page_id)

                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [executor.submit(fetch_content, content_id) for content_id in content_ids]
                    for future in futures:
                        try:
                            future.result()
                        except Exception:
                            logger.exception("Błąd podczas fetch_content")

                set_embeddings_pending(page_id, embedding_config_id)
                embedding_ids = get_embedding_ids(page_id, embedding_config_id)

                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [
                        executor.submit(
                            compute_embedding,
                            embed,
                            embedding_id,
                            embedding_config_id
                        ) for embedding_id in embedding_ids
                    ]
                    for future in futures:
                        try:
                            future.result()
                        except Exception:
                            logger.exception("Błąd podczas compute_embedding")

            except Exception:
                logger.exception("Błąd w pętli indeksującej")
                time.sleep(60)
                continue

            time.sleep(3600)

    finally:
        pool.close()


if __name__ == "__main__":
    main()
