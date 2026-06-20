from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int
    db_name: str
    embedding_model_name: str
    embedding_vector_size: int
    openai_api_key: SecretStr | None = None
    hf_token: SecretStr | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
