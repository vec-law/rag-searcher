from rag_searcher.core.embedder import Embedder
from rag_searcher.config import settings
from rag_searcher.db.queries.embedding import get_embedding_config


def get_embed(embedding_config_id: int):
    config = get_embedding_config(embedding_config_id)
    if config is None:
        raise ValueError(f"Brak embedding_config o id: {embedding_config_id}")

    model_name, _ = config
    if not model_name:
        raise ValueError(f"Brak model_name dla embedding_config o id: {embedding_config_id}")

    embedder = Embedder(
        model_name,
        openai_api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None,
        hf_token=settings.hf_token.get_secret_value() if settings.hf_token else None,
    )
    return embedder.embed
