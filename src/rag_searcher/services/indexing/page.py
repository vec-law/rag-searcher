from rag_searcher.config import settings

from rag_searcher.db.queries.page import get_page_settings as db_get_page_settings
from rag_searcher.db.queries.link import (
    delete_expired_page_links as db_delete_expired_page_links,
    save_links as db_save_links,
)
from rag_searcher.db.queries.content import (
    set_page_contents_pending as db_set_page_contents_pending,
    get_page_content_ids as db_get_page_content_ids,
)
from rag_searcher.db.queries.embedding import (
    set_page_embeddings_pending as db_set_page_embeddings_pending,
    get_embedding_ids as db_get_embedding_ids,
)
from rag_searcher.services.indexing.link import fetch_links_from_paginated


def delete_expired_page_links(page_id: int) -> None:
    db_delete_expired_page_links(page_id, settings.link_expiry_days)

def fetch_page_links(page_id: int) -> None:
    url, page_max, page_type, fetcher_name = db_get_page_settings(page_id)

    if page_type == "paginated":
        links_dict = fetch_links_from_paginated(url, page_max, fetcher_name)
    else:
        raise ValueError(f"Nieznany typ strony: page_type={page_type}")

    if not links_dict:
        return

    db_save_links(page_id, links_dict)

def set_page_contents_pending(page_id: int) -> None:
    db_set_page_contents_pending(page_id)

def get_page_content_ids(page_id: int) -> list[int]:
    return db_get_page_content_ids(page_id)

def set_page_embeddings_pending(page_id: int) -> None:
    db_set_page_embeddings_pending(page_id)

def get_page_embedding_ids(page_id: int) -> list[int]:
    return db_get_embedding_ids(page_id)
