from rag_searcher.config import settings

from rag_searcher.db.queries.page_type import get_page_type_id as db_get_page_type_id
from rag_searcher.db.queries.fetcher import get_fetcher_id as db_get_fetcher_id
from rag_searcher.db.queries.page import (
    get_page_id as db_get_page_id,
    insert_page as db_insert_page,
    update_page_embedding_config as db_update_page_embedding_config,
    get_page_embedding_config as db_get_page_embedding_config,
    get_page_settings as db_get_page_settings,
)
from rag_searcher.db.queries.link import (
    delete_expired_page_links as db_delete_expired_page_links,
    save_links as db_save_links,
)
from rag_searcher.db.queries.content import (
    set_page_contents_pending as db_set_page_contents_pending,
    get_page_content_ids as db_get_page_content_ids,
)
from rag_searcher.services.indexing.link import fetch_links_from_paginated


def setup_page() -> int:
    page_type_id = db_get_page_type_id(settings.page_type)
    fetcher_id = db_get_fetcher_id(settings.fetcher_name)

    page_id = db_get_page_id(
        settings.page_url,
        page_type_id,
        settings.page_max,
        fetcher_id
    )

    if page_id is None:
        page_id = db_insert_page(
            settings.page_url,
            page_type_id,
            settings.page_max,
            fetcher_id,
            settings.embedding_model_name,
            settings.embedding_vector_size,
        )
        return page_id
    
    embedding_model_name, embedding_vector_size = db_get_page_embedding_config(page_id)

    if (embedding_model_name != settings.embedding_model_name
            or embedding_vector_size != settings.embedding_vector_size):
        db_update_page_embedding_config(
            settings.embedding_model_name,
            settings.embedding_vector_size
        )

    return page_id

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
