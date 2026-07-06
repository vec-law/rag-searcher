CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS page_type (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS fetcher (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS page (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    page_type_id INTEGER REFERENCES page_type(id),
    page_max INTEGER NOT NULL,
    fetcher_id INTEGER REFERENCES fetcher(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (url, page_type_id, page_max, fetcher_id)
);

CREATE TABLE IF NOT EXISTS embedding_config (
    id SERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    vector_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (model_name, vector_size)
);

CREATE TABLE IF NOT EXISTS page_embedding_config (
    page_id INTEGER REFERENCES page(id) ON DELETE CASCADE,
    embedding_config_id INTEGER REFERENCES embedding_config(id) ON DELETE CASCADE,
    PRIMARY KEY (page_id, embedding_config_id)
);

CREATE TABLE IF NOT EXISTS link (
    id SERIAL PRIMARY KEY,
    page_id INTEGER REFERENCES page(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (page_id, url)
);

CREATE TABLE IF NOT EXISTS content (
    id SERIAL PRIMARY KEY,
    link_id INTEGER REFERENCES link(id) ON DELETE CASCADE UNIQUE,
    content TEXT,
    status_id INTEGER REFERENCES status(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_link_page_id ON link(page_id);
CREATE INDEX IF NOT EXISTS idx_content_link_id ON content(link_id);
CREATE INDEX IF NOT EXISTS idx_content_status_id ON content(status_id);
