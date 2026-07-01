import logging

from rag_searcher.db.queries.embedding import (
    update_embedding as db_update_embedding,
    get_embedding_context as db_get_embedding_context,
)

logger = logging.getLogger(__name__)


def compute_embedding(embed, embedding_id):
    db_update_embedding(embedding_id, None, "running")
    logger.info("[id: %s]", embedding_id)
    context = db_get_embedding_context(embedding_id)
    if not context:
        db_update_embedding(embedding_id, None, "failed")
        return
    if context["status"] != "completed" or not context["content"]:
        db_update_embedding(embedding_id, None, "failed")
        return
    title = context["title"]
    content = context["content"]
    embedding = embed(f"{title}\n{content}" if title else content)
    if not embedding:
        db_update_embedding(embedding_id, None, "failed")
        return
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    db_update_embedding(embedding_id, embedding_str, "completed")
