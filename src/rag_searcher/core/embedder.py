import logging

logger = logging.getLogger(__name__)


class Embedder:
    def __init__(self, model_name, openai_api_key=None):
        self._model_name = model_name

        if self._model_name == "text-embedding-3-large":
            from openai import OpenAI
            self._client = OpenAI(api_key=openai_api_key, max_retries=5)
            self._get_embedding = self._get_embedding_openai

        elif self._model_name == "sdadas/mmlw-retrieval-roberta-large-v2":
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name)
            self._get_embedding = self._get_embedding_roberta

        else:
            raise NotImplementedError(f"Brak implementacji dla modelu: {self._model_name}. Dodaj implementację do embedder.py.")

    def get_embedding(self, text, type=None):
        return self._get_embedding(text, type)

    def _get_embedding_openai(self, text, type=None):
        from openai import APIError
        try:
            response = self._client.embeddings.create(
                input=text,
                model=self._model_name
            )
            return response.data[0].embedding
        except APIError as e:
            logger.error(f"Błąd API: {e}")
            raise

    def _get_embedding_roberta(self, text, type=None):
        try:
            if type == "query":
                text = f"[query]: {text}"
            return self._model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Błąd embeddera: {e}")
            raise
