from dataclasses import dataclass


@dataclass
class Page:
    id: int
    url: str
    page_type_id: int
    page_max: int
    fetcher_id: int
    embedding_model_name: str
    embedding_vector_size: int
