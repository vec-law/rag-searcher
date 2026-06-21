from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int

    page_url: str
    page_type: str
    page_max: int
    fetcher_name: str

    link_expiry_days: int

    embedding_model_name: str
    embedding_vector_size: int

    semantic_search_limit: int

    llm_name: str
    rag_limit: int

    hf_token: SecretStr | None = None
    openai_api_key: SecretStr | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
