import logging

logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, model_name, openai_api_key=None, hf_token=None):
        self._model_name = model_name

        if self._model_name == "gpt-4o":
            from openai import OpenAI
            self._client = OpenAI(api_key=openai_api_key, max_retries=5)
            self._respond = self._respond_openai

        elif self._model_name in ("unsloth/gemma-4-E2B-it-GGUF", "unsloth/gemma-4-E4B-it-GGUF", "unsloth/gemma-4-12b-it-GGUF"):
            logger.info("Rozpoczęto ładowanie modelu: %s", self._model_name)

            import contextlib
            import io
            import warnings
            warnings.filterwarnings("ignore", module="huggingface_hub")

            from llama_cpp import Llama
            import llama_cpp

            def _null_log_callback(level, text, user_data):
                pass
            self._log_cb = llama_cpp.ggml_log_callback(_null_log_callback)
            llama_cpp.llama_log_set(self._log_cb, None)

            with contextlib.redirect_stderr(io.StringIO()):
                self._model = Llama.from_pretrained(
                    repo_id=self._model_name,
                    filename="*Q4_K_M*.gguf",
                    verbose=False,
                    token=hf_token,
                    n_ctx=8192
                )
            self._respond = self._respond_gemma_llamacpp

            logger.info("Zakończono ładowanie modelu: %s", self._model_name)

        else:
            raise NotImplementedError(f"Brak implementacji dla modelu: {self._model_name}. Dodaj implementację do llm.py.")

    def respond(self, messages: list[dict]) -> str:
        return self._respond(messages)

    def _respond_openai(self, messages: list[dict]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Błąd API: %s", e)
            raise

    def _respond_gemma_llamacpp(self, messages: list[dict]) -> str:
        try:
            response = self._model.create_chat_completion(
                messages=messages
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error("Błąd modelu Gemma (llama.cpp): %s", e)
            raise
