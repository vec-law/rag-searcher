# rag-searcher

**PL:** System RAG (Retrieval-Augmented Generation) z interfejsem REST API do przeszukiwania paginowanych stron internetowych w języku naturalnym.

---

**EN:** A RAG (Retrieval-Augmented Generation) system with a REST API for searching paginated websites using natural language.

## Architektura (Architecture)

**PL:** System składa się z dwóch niezależnych komponentów: workera indeksującego i serwera API, które komunikują się przez bazę danych PostgreSQL.

**Worker indeksujący** (`workers/indexing_worker.py`) zbiera linki z podstron paginacji, pobiera ich treść (`trafilatura`) i zapisuje ją do bazy danych wraz z embeddingami.

**Serwer API** (`api/main.py`, FastAPI) udostępnia dwa endpointy:

- `GET /search` zwraca wyniki wyszukiwania wektorowego według cosine similarity.
- `POST /chat` prowadzi konwersację i odpowiada na zapytania wynikami wyszukiwania wektorowego przefiltrowanymi przez LLM.

---

**EN:** The system consists of two independent components: an indexing worker and an API server, which communicate through a PostgreSQL database.

**Indexing worker** (`workers/indexing_worker.py`) collects links from pagination subpages, fetches their content (`trafilatura`), and saves it to the database along with embeddings.

**API server** (`api/main.py`, FastAPI) exposes two endpoints:

- `GET /search` returns vector search results ranked by cosine similarity.
- `POST /chat` handles conversation and answers queries with vector search results filtered by an LLM.

## Filtrowanie linków (Link Filtering)

**PL:** Program nie używa hardkodowanych selektorów ani słów kluczowych. Struktura strony jest dedukowana statystycznie:

- Linki wspólne dla pierwszych podstron (nawigacja, stopka) są usuwane przez część wspólną zbiorów.
- Z pozostałych linków zostają te z dominującym pierwszym segmentem ścieżki URL.
- Paginacja kończy się, gdy kolejna podstrona pokrywa się w co najmniej 80% z poprzednią lub pierwszą.

Zmiana indeksowanego serwisu wymaga tylko zmiany `PAGE_URL` w `.env`.

---

**EN:** The program uses no hardcoded selectors or keywords. The page structure is inferred statistically:

- Links shared by the first few subpages (navigation, footer) are removed via set intersection.
- Of the remaining links, only those with the dominant first URL path segment are kept.
- Pagination stops when a subpage overlaps at least 80% with the previous or the first one.

Switching to a different website only requires changing `PAGE_URL` in `.env`.

## Rozszerzalność (Extensibility)

**PL:** Fetchery i modele są konfigurowane przez `.env`. Dodanie nowego fetchera wymaga dopisania funkcji w `core/fetcher.py` i wpisu w tabeli `fetcher`, a nowego modelu embeddingów lub LLM dopisania obsługi w `core/embedder.py` lub `core/llm.py`. Reszta pipeline'u nie wymaga zmian.

---

**EN:** Fetchers and models are configured via `.env`. Adding a new fetcher requires adding a function in `core/fetcher.py` and a row in the `fetcher` table, and a new embedding model or LLM requires adding its handling in `core/embedder.py` or `core/llm.py`. The rest of the pipeline remains unchanged.

## Modele (Models)

**PL:**

Embeddingi:
- `text-embedding-3-large` (OpenAI API)
- `sdadas/mmlw-retrieval-roberta-large-v2` (lokalny)

LLM:
- `gpt-4o` (OpenAI API)
- `unsloth/gemma-4-E2B-it-GGUF`, `unsloth/gemma-4-E4B-it-GGUF`, `unsloth/gemma-4-12b-it-GGUF` (lokalne, `llama-cpp`)

---

**EN:**

Embeddings:
- `text-embedding-3-large` (OpenAI API)
- `sdadas/mmlw-retrieval-roberta-large-v2` (local)

LLM:
- `gpt-4o` (OpenAI API)
- `unsloth/gemma-4-E2B-it-GGUF`, `unsloth/gemma-4-E4B-it-GGUF`, `unsloth/gemma-4-12b-it-GGUF` (local, `llama-cpp`)

## Wymagania (Requirements)

**PL:**
- Python 3.14+
- PostgreSQL z rozszerzeniem [`pgvector`](https://github.com/pgvector/pgvector)
- Klucz API OpenAI lub token HuggingFace dla modeli lokalnych (przyspiesza pobieranie)

---

**EN:**
- Python 3.14+
- PostgreSQL with the [`pgvector`](https://github.com/pgvector/pgvector) extension
- OpenAI API key, or a HuggingFace token for local models (speeds up download)

## Instalacja (Installation)

```bash
git clone https://github.com/vec-law/rag-searcher.git
cd rag-searcher
uv sync
uv pip install -e .
```

## Konfiguracja (Configuration)

**PL:** Uzupełnij `.env`:

---

**EN:** Fill in `.env`:

| Zmienna / Variable | Opis / Description | Przykład / Example |
|---|---|---|
| `DB_NAME` | Nazwa bazy danych / Database name | `rag_searcher_db` |
| `DB_USER` | Użytkownik PostgreSQL / PostgreSQL user | `postgres` |
| `DB_PASSWORD` | Hasło / Password | `1234` |
| `DB_HOST` | Host | `localhost` |
| `DB_PORT` | Port | `5432` |
| `PAGE_URL` | URL paginacji z `{page_number}` / Pagination URL with `{page_number}` | `http://example-page.com/pn={page_number}` |
| `PAGE_TYPE` | Typ strony / Page type | `paginated` |
| `PAGE_MAX` | Limit podstron / Subpage limit | `1000` |
| `FETCHER_NAME` | Silnik pobierania / Fetcher engine | `curl` |
| `LINK_EXPIRY_DAYS` | Czas życia linków w dniach / Link expiry in days | `30` |
| `EMBEDDING_MODEL_NAME` | Model embeddingów / Embedding model | `text-embedding-3-large` |
| `EMBEDDING_VECTOR_SIZE` | Rozmiar wektora embeddingów / Embedding vector size | `3072` |
| `LLM_NAME` | Model LLM | `gpt-4o` |
| `OPENAI_API_KEY` | Klucz API OpenAI / OpenAI API key | `sk-abcd...` |
| `HF_TOKEN` | Token HuggingFace / HuggingFace token | `hf_abcd...` |

## Uruchomienie (Usage)

```bash
# Przygotowanie bazy / Database setup
psql -U postgres -c "CREATE DATABASE rag_searcher_db;"
uv run python -m rag_searcher.db.migrate

# Indeksowanie / Indexing
uv run python -m rag_searcher.workers.indexing_worker

# Serwer API / API server
uv run uvicorn rag_searcher.api.main:app
```

## Struktura projektu (Project Structure)

**PL:**
```
rag-searcher/
├── pyproject.toml
└── src/rag_searcher/
    ├── config.py              # konfiguracja (.env)
    ├── api/
    │   ├── main.py            # serwer FastAPI
    │   └── routers/
    │       ├── chat.py        # endpoint POST /chat
    │       └── search.py      # endpoint GET /search
    ├── workers/
    │   └── indexing_worker.py # worker indeksujący
    ├── core/
    │   ├── fetcher.py         # pobieranie stron
    │   ├── link_parser.py     # parsowanie linków
    │   ├── content_extractor.py # ekstrakcja treści
    │   ├── embedder.py        # modele embeddingów
    │   └── llm.py             # modele LLM
    ├── services/
    │   ├── indexing/          # pipeline indeksowania
    │   ├── embedder.py        # zwraca funkcję embed
    │   ├── llm.py             # zwraca funkcję respond
    │   └── initialization.py  # inicjalizacja przy starcie
    └── db/
        ├── pool.py            # pula połączeń
        ├── migrate.py         # migracje
        ├── migrations/        # pliki SQL
        └── queries/           # zapytania do bazy danych
```

---

**EN:**
```
rag-searcher/
├── pyproject.toml
└── src/rag_searcher/
    ├── config.py              # configuration (.env)
    ├── api/
    │   ├── main.py            # FastAPI server
    │   └── routers/
    │       ├── chat.py        # POST /chat endpoint
    │       └── search.py      # GET /search endpoint
    ├── workers/
    │   └── indexing_worker.py # indexing worker
    ├── core/
    │   ├── fetcher.py         # page fetching
    │   ├── link_parser.py     # link parsing
    │   ├── content_extractor.py # content extraction
    │   ├── embedder.py        # embedding models
    │   └── llm.py             # LLM models
    ├── services/
    │   ├── indexing/          # indexing pipeline
    │   ├── embedder.py        # returns the embed function
    │   ├── llm.py             # returns the respond function
    │   └── initialization.py  # startup initialization
    └── db/
        ├── pool.py            # connection pool
        ├── migrate.py         # migrations
        ├── migrations/        # SQL files
        └── queries/           # database queries
```

## Historia zmian (Change Log)

**PL:**
- **v0.2.0**:
  - Zreorganizowano strukturę pakietu z podziałem na warstwy `api`, `workers`, `core`, `services` i `db`
  - Zastąpiono skrypty CLI (`chat.py`, `semantic_search.py`) endpointami REST API (`POST /chat`, `GET /search`)
  - Zastąpiono lokalne modele LLM Qwen modelami Gemma (`llama-cpp`)
- **v0.1.0**: Wersja bazowa

---

**EN:**
- **v0.2.0**:
  - Reorganized the package structure into `api`, `workers`, `core`, `services`, and `db` layers
  - Replaced the CLI scripts (`chat.py`, `semantic_search.py`) with REST API endpoints (`POST /chat`, `GET /search`)
  - Replaced the local Qwen LLM models with Gemma models (`llama-cpp`)
- **v0.1.0**: Initial version

## Zastrzeżenie (Disclaimer)

**PL**: Oprogramowanie służy wyłącznie do celów edukacyjnych i badawczych. Autor nie ponosi odpowiedzialności za sposób wykorzystania narzędzia ani za zgodność jego użycia z regulaminami serwisów internetowych.

---

**EN**: This software is for educational and research purposes only. The author bears no responsibility for the use of the tool or for compliance with the terms of service of any website.

## Licencja (License)

**PL:** Ten projekt jest udostępniany na licencji **GNU General Public License v3.0**. Szczegóły znajdują się w pliku [LICENSE](LICENSE).

---

**EN:** This project is licensed under the **GNU General Public License v3.0**. See the [LICENSE](LICENSE) file for details.
