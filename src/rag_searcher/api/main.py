import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from rag_searcher.db.pool import pool
from rag_searcher.config import settings
from rag_searcher.db.queries.page import get_page_id as db_get_page_id
from rag_searcher.db.queries.embedding import get_embedding_config_id as db_get_embedding_config_id
from rag_searcher.db.queries.page_type import get_page_type_id as db_get_page_type_id
from rag_searcher.db.queries.fetcher import get_fetcher_id as db_get_fetcher_id
from rag_searcher.services.embedder import get_embed
from rag_searcher.services.llm import get_respond
from rag_searcher.api.routers import search

logging.basicConfig(level=logging.WARNING)
logging.getLogger("rag_searcher").setLevel(logging.INFO)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub.utils._http").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()

    page_type_id = db_get_page_type_id(settings.page_type)
    fetcher_id = db_get_fetcher_id(settings.fetcher_name)

    page_id = db_get_page_id(
        settings.page_url,
        page_type_id,
        settings.page_max,
        fetcher_id,
    )
    if page_id is None:
        raise RuntimeError("Brak page_id dla ustawień z .env")

    embedding_config_id = db_get_embedding_config_id(
        settings.embedding_model_name,
        settings.embedding_vector_size,
    )
    if embedding_config_id is None:
        raise RuntimeError("Brak embedding_config_id dla ustawień z .env")
    
    embed = get_embed(embedding_config_id)
    respond = get_respond()

    app.state.page_id = page_id
    app.state.embedding_config_id = embedding_config_id
    app.state.embed = embed
    app.state.respond = respond

    yield

    pool.close()


app = FastAPI(lifespan=lifespan)
app.include_router(search.router)
