from fastapi import APIRouter, HTTPException, Query, Request
from rag_searcher.db.queries.embedding import get_similar_embedding_ids as db_get_similar_embedding_ids
from rag_searcher.db.queries.embedding import get_embedding_context as db_get_embedding_context

router = APIRouter()


@router.get("/search")
def search_endpoint(
    request: Request,
    query: str = Query(pattern=r".*\S.*"),
    limit: int | None = Query(default=None, gt=0),
):
    page_id = request.app.state.page_id
    embedding_config_id = request.app.state.embedding_config_id
    embed = request.app.state.embed

    query_embedding = embed(query, text_type="query")

    if not query_embedding:
        raise HTTPException(
            status_code=500,
            detail="Nie udało się policzyć embeddingu dla zapytania"
        )
    
    embedding_ids = db_get_similar_embedding_ids(
        query_embedding,
        limit,
        page_id,
        embedding_config_id
    )

    results = [
        {
            "url": context["url"],
            "title": context["title"],
            "content": context["content"]
        } for embedding_id in embedding_ids

        if (context := db_get_embedding_context(
            embedding_id,
            embedding_config_id
        )) is not None
    ]

    return {"results": results}
