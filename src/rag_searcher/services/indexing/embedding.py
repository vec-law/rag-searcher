import logging

from rag_searcher.db.queries.embedding import (
    update_embedding as db_update_embedding,
    get_embedding_context as db_get_embedding_context,
    set_embeddings_pending as db_set_embeddings_pending,
    get_embedding_ids as db_get_embedding_ids
)
from typing import Callable

logger = logging.getLogger(__name__)

def set_embeddings_pending(page_id: int, embedding_config_id: int) -> None:
    db_set_embeddings_pending(page_id, embedding_config_id)

def get_embedding_ids(page_id: int, embedding_config_id: int) -> list[int]:
    return db_get_embedding_ids(page_id, embedding_config_id)

def compute_embedding(
    embed: Callable[[str], list[float]],
    embedding_id: int,
    embedding_config_id: int,
) -> None:
    db_update_embedding(embedding_id, embedding_config_id, None, "running")
    logger.info("[id: %s]", embedding_id)
    context = db_get_embedding_context(embedding_id, embedding_config_id)
    if not context:
        db_update_embedding(embedding_id, embedding_config_id, None, "failed")
        return
    if context["status"] != "completed" or not context["content"]:
        db_update_embedding(embedding_id, embedding_config_id, None, "failed")
        return
    title = context["title"]
    content = context["content"]
    embedding = embed(f"{title}\n{content}" if title else content)
    if not embedding:
        db_update_embedding(embedding_id, embedding_config_id, None, "failed")
        return
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    db_update_embedding(embedding_id, embedding_config_id, embedding_str, "completed")
