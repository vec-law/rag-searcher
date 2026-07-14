import logging

from fastapi import APIRouter, HTTPException, Query, Request
from rag_searcher.db.queries.embedding import get_similar_embedding_ids as db_get_similar_embedding_ids
from rag_searcher.db.queries.embedding import get_embedding_context as db_get_embedding_context

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search")
def search_endpoint(
    request: Request,
    query: str = Query(pattern=r".*\S.*"),
    limit: int | None = Query(default=None, gt=0, le=100)
):
    page_id = request.app.state.page_id
    embedding_config_id = request.app.state.embedding_config_id
    embed = request.app.state.embed

    try:
        query_embedding = embed(query, text_type="query")
    except Exception as e:
        logger.error("Błąd podczas liczenia embeddingu: %s", e)
        raise HTTPException(status_code=500, detail="Nie udało się policzyć embeddingu dla zapytania")

    if not query_embedding:
        raise HTTPException(status_code=500, detail="Nie udało się policzyć embeddingu dla zapytania")
    
    embedding_ids = db_get_similar_embedding_ids(
        query_embedding,
        limit,
        page_id,
        embedding_config_id
    )

    results = [
        {
            "title": context["title"],
            "url": context["url"]
        } for embedding_id in embedding_ids

        if (context := db_get_embedding_context(
            embedding_id,
            embedding_config_id
        )) is not None
    ]

    return {"results": results}
