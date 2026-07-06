import logging

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name, openai_api_key=None, hf_token=None):
        self._model_name = model_name

        if self._model_name == "text-embedding-3-large":
            from openai import OpenAI
            
            self._client = OpenAI(api_key=openai_api_key, max_retries=5)
            self._embed = self._embed_openai

        elif self._model_name == "sdadas/mmlw-retrieval-roberta-large-v2":
            from huggingface_hub.utils import disable_progress_bars
            disable_progress_bars()

            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name, token=hf_token)
            self._embed = self._embed_roberta

        else:
            raise NotImplementedError(f"Brak implementacji dla modelu: {self._model_name}. Dodaj implementację do embedder.py.")

    def embed(self, text, text_type=None):
        return self._embed(text, text_type)

    def _embed_openai(self, text, text_type=None):
        try:
            response = self._client.embeddings.create(
                input=text,
                model=self._model_name
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error("Błąd API: %s", e)
            raise

    def _embed_roberta(self, text, text_type=None):
        try:
            if text_type == "query":
                text = f"[query]: {text}"
            return self._model.encode(text, show_progress_bar=False).tolist()
        except Exception as e:
            logger.error("Błąd embeddera: %s", e)
            raise

