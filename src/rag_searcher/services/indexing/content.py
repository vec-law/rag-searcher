import time
import logging

from rag_searcher.core.fetcher import fetch_url
from rag_searcher.core.content_extractor import extract_content
from rag_searcher.db.queries.content import (
    get_content_params as db_get_content_params,
    update_content as db_update_content,
)

logger = logging.getLogger(__name__)


def fetch_content(content_id: int) -> None:
    time.sleep(5)

    fetcher_name, content_url = db_get_content_params(content_id)
    db_update_content(content_id, None, "running")

    if not content_url:
        db_update_content(content_id, None, "failed")
        return

    content_html, status_code = fetch_url(content_url, fetcher_name)
    logger.info("[id: %s, status: %s] %s", content_id, status_code, content_url[:50])

    if status_code != 200 or not content_html:
        db_update_content(content_id, None, "failed")
        return

    content = extract_content(content_html)

    if not content:
        db_update_content(content_id, None, "failed")
        return

    db_update_content(content_id, content, "completed")
