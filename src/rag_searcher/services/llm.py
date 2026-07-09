from rag_searcher.core.llm import LLM
from rag_searcher.config import settings

def get_respond():
    llm = LLM(
        model_name=settings.llm_name,
        openai_api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None,
        hf_token=settings.hf_token.get_secret_value() if settings.hf_token else None,
    )
    return llm.respond
