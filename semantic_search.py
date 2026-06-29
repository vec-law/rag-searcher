import os
from dotenv import load_dotenv
from embedder import Embedder
from db.queries.search import search_links as db_search_links
from db.queries.link import get_links as db_get_links

load_dotenv()

embedder = Embedder()

while True:
    query = input("\nZapytanie: ").strip()
    if not query:
        continue
    if query.lower() == "exit":
        break

    embedding = embedder.get_embedding(query, type="query")
    if embedding is None:
        print("\nBłąd: nie udało się przetworzyć zapytania, spróbuj ponownie.\n")
        continue
    limit = int(os.getenv("SEMANTIC_SEARCH_LIMIT", 50))
    link_ids = db_search_links(embedding, limit)
    results = db_get_links(link_ids)

    if not results:
        continue

    for i, r in enumerate(results, start=1):
        print(f"\n{i}: {r['title']}\n{r['url']}")
