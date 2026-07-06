from rag_searcher.config import settings

from rag_searcher.db.queries.page_type import get_page_type_id as db_get_page_type_id
from rag_searcher.db.queries.fetcher import get_fetcher_id as db_get_fetcher_id
from rag_searcher.db.queries.page import (
    get_page_id as db_get_page_id,
    insert_page as db_insert_page,
)
from rag_searcher.db.queries.embedding import (
    get_embedding_config_id as db_get_embedding_config_id,
    insert_embedding_config as db_insert_embedding_config,
    insert_page_embedding_config as db_insert_page_embedding_config,
    insert_embedding_vector_table as db_insert_embedding_vector_table
)

def init():
    page_id = _init_page()
    embedding_config_id = _init_embedding_config()
    db_insert_page_embedding_config(page_id, embedding_config_id)
    db_insert_embedding_vector_table(embedding_config_id)

    return page_id, embedding_config_id

def _init_page():
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
            fetcher_id
        )

    return page_id

def _init_embedding_config():
    embedding_config_id = db_get_embedding_config_id(
        settings.embedding_model_name,
        settings.embedding_vector_size
    )

    if embedding_config_id is None:
        embedding_config_id = db_insert_embedding_config(
        settings.embedding_model_name,
        settings.embedding_vector_size
        )
        
    return embedding_config_id
