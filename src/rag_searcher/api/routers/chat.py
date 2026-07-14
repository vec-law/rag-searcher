import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from rag_searcher.db.queries.embedding import get_similar_embedding_ids as db_get_similar_embedding_ids
from rag_searcher.db.queries.embedding import get_embedding_context as db_get_embedding_context

logger = logging.getLogger(__name__)

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    history: list[Message]
    message: str
    sources_limit: int = Field(default=20, ge=1, le=50)


def is_search_request(respond, domain, history, message):
    history_text = "\n".join(f"{m.role}: {m.content}" for m in history)
    try:
        reply = respond([
            {"role": "system", "content": (
                f"Jesteś routerem wyszukiwarki w dziedzinie: {domain}. "
                "Zdecyduj, czy ostatnią wiadomość użytkownika należy potraktować jako zapytanie do wyszukiwarki.\n"
                "TAK — wiadomość opisuje, czego użytkownik szuka: pełne zdanie LUB sama fraza kluczowa "
                "(np. nazwa, kategoria, opis z tej dziedziny).\n"
                "NIE — powitanie, podziękowanie, pytanie o działanie asystenta lub temat spoza dziedziny.\n"
                "W razie wątpliwości: TAK.\n"
                "Odpowiedz jednym słowem: TAK albo NIE."
            )},
            {"role": "user", "content": f"Historia:\n{history_text}\n\nOstatnia wiadomość: {message}"}
        ])
    except Exception as e:
        logger.error("Błąd podczas klasyfikacji intencji: %s", e)
        return False

    return reply.strip().upper().startswith("TAK")


def evaluate_source(respond, domain, query, source):
    try:
        classification = respond([
            {"role": "system", "content": (
                f"Oceniasz trafność wyniku wyszukiwania w dziedzinie: {domain}.\n"
                "TAK — treść wyniku odpowiada na zapytanie.\n"
                "NIE — wynik dotyczy innego tematu lub łączy go z zapytaniem tylko wspólne słowo.\n"
                "W razie wątpliwości: NIE.\n"
                "Odpowiedz jednym słowem: TAK albo NIE."
            )},
            {"role": "user", "content": f"Zapytanie: {query}\n\nWynik:\n{source['title']}\n{source['content']}"}
        ])
    except Exception as e:
        logger.error("Błąd podczas klasyfikacji source'a: %s: %s", source.get("title"), e)
        return None

    if not classification.strip().upper().startswith("TAK"):
        return None

    return {"title": source["title"], "url": source["url"]}


def handle_conversation(respond, domain, history, message):
    system_prompt = (
        f"Jesteś asystentem wyszukiwania w dziedzinie: {domain}. Pomagasz tylko w niej — "
        "pytania spoza dziedziny grzecznie odrzucaj. Rozmawiaj naturalnie i zwięźle. "
        "Nie wymyślaj wyników ani źródeł — wyszukuje osobny mechanizm."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": message})

    return respond(messages)


def handle_search(respond, embed, domain, page_id, embedding_config_id, sources_limit, message):
    try:
        query_embedding = embed(message, text_type="query")
    except Exception as e:
        logger.error("Błąd podczas liczenia embeddingu: %s", e)
        raise HTTPException(status_code=500, detail="Nie udało się policzyć embeddingu dla zapytania")

    if not query_embedding:
        raise HTTPException(status_code=500, detail="Nie udało się policzyć embeddingu dla zapytania")

    embedding_ids = db_get_similar_embedding_ids(
        query_embedding,
        sources_limit,
        page_id,
        embedding_config_id
    )

    sources = [
        {
            "title": context["title"],
            "url": context["url"],
            "content": context["content"]
        } for embedding_id in embedding_ids

        if (context := db_get_embedding_context(
            embedding_id,
            embedding_config_id
        )) is not None
    ]

    matches = [
        match for source in sources
        if (match := evaluate_source(respond, domain, message, source)) is not None
    ]

    if not matches:
        return "\n\nNie znalazłem żadnych pasujących wyników.\n"

    lines = [
        f"[{i}] {m['title']}\n{m['url']}"
        for i, m in enumerate(matches, start=1)
    ]

    answer = "\n\nZnalazłem następujące wyniki:\n\n" + "\n\n".join(lines) + "\n"

    return answer


@router.post("/chat")
def chat_endpoint(request: Request, body: ChatRequest):
    page_id = request.app.state.page_id
    embedding_config_id = request.app.state.embedding_config_id
    embed = request.app.state.embed
    respond = request.app.state.respond
    domain = request.app.state.domain

    if is_search_request(respond, domain, body.history, body.message):
        answer = handle_search(
            respond, embed, domain, page_id, embedding_config_id,
            body.sources_limit, body.message
        )
    else:
        answer = handle_conversation(respond, domain, body.history, body.message)

    logger.info(answer)

    return {"answer": answer}
