from rag_searcher.config import settings
from rag_searcher.models.page import Page
from rag_searcher.db.queries.page_type import get_page_type_id as db_get_page_type_id
from rag_searcher.db.queries.fetcher import get_fetcher_id as db_get_fetcher_id
from rag_searcher.db.queries.page import get_page_id as db_get_page_id
from rag_searcher.db.queries.page import insert_page as db_insert_page


def get_page() -> Page:
    url = settings.page_url
    page_max = settings.page_max
    embedding_model_name = settings.embedding_model_name
    embedding_vector_size = settings.embedding_vector_size

    page_type_id = db_get_page_type_id(settings.page_type)
    fetcher_id = db_get_fetcher_id(settings.fetcher_name)

    page_id = db_get_page_id(url, page_type_id, page_max, fetcher_id)

    if page_id is None:
        page_id = db_insert_page(
            url, page_type_id, page_max, fetcher_id,
            embedding_model_name, embedding_vector_size,
        )

    return Page(
        id=page_id,
        url=url,
        page_type_id=page_type_id,
        page_max=page_max,
        fetcher_id=fetcher_id,
        embedding_model_name=embedding_model_name,
        embedding_vector_size=embedding_vector_size,
    )
