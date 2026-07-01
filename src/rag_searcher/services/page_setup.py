from rag_searcher.config import settings

from rag_searcher.db.queries.page_type import get_page_type_id as db_get_page_type_id
from rag_searcher.db.queries.fetcher import get_fetcher_id as db_get_fetcher_id
from rag_searcher.db.queries.page import (
    get_page_id as db_get_page_id,
    insert_page as db_insert_page,
    update_page_embedding_config as db_update_page_embedding_config,
    get_page_embedding_config as db_get_page_embedding_config,
)


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


def get_page_id() -> int:
    page_type_id = db_get_page_type_id(settings.page_type)
    fetcher_id = db_get_fetcher_id(settings.fetcher_name)

    page_id = db_get_page_id(
        settings.page_url,
        page_type_id,
        settings.page_max,
        fetcher_id
    )

    if page_id is None:
        raise ValueError("Strona o podanej konfiguracji nie istnieje.")

    return page_id
