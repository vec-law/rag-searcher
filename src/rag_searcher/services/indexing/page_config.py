from rag_searcher.config import settings
from rag_searcher.models.page import Page
from rag_searcher.db.queries.page_type import get_page_type_id as db_get_page_type_id
from rag_searcher.db.queries.fetcher import get_fetcher_id as db_get_fetcher_id
from rag_searcher.db.queries.page import get_page as db_get_page
from rag_searcher.db.queries.page import insert_page as db_insert_page
from rag_searcher.db.queries.page import update_page_embedding_config as db_update_page_embedding_config


def get_page() -> Page:
    url = settings.page_url
    page_max = settings.page_max
    embedding_model_name = settings.embedding_model_name
    embedding_vector_size = settings.embedding_vector_size

    page_type_id = db_get_page_type_id(settings.page_type)
    fetcher_id = db_get_fetcher_id(settings.fetcher_name)

    page = db_get_page(url, page_type_id, page_max, fetcher_id)

    if page is None:
        page = db_insert_page(
            url, page_type_id, page_max, fetcher_id,
            embedding_model_name, embedding_vector_size,
        )
        return page

    if (page.embedding_model_name != embedding_model_name
            or page.embedding_vector_size != embedding_vector_size):
        page = db_update_page_embedding_config(
            page.id, embedding_model_name, embedding_vector_size,
        )

    return page
