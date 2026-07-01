from rag_searcher.core.embedder import Embedder
from rag_searcher.config import settings
from rag_searcher.db.queries.page import get_page_embedding_config


def get_compute_embedding(page_id: int):
    model_name, _ = get_page_embedding_config(page_id)
    embedder = Embedder(model_name, settings.openai_api_key.get_secret_value())
    return embedder.compute_embedding
