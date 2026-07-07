import logging

logger = logging.getLogger(__name__)


class LLM:
    def __init__(self, model_name, openai_api_key=None, hf_token=None):
        self._model_name = model_name

        if self._model_name == "gpt-4o":
            from openai import OpenAI
            self._client = OpenAI(api_key=openai_api_key, max_retries=5)
            self._respond = self._respond_openai

        elif self._model_name == "Qwen/Qwen3-1.7B":
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_name, token=hf_token)
            self._model = AutoModelForCausalLM.from_pretrained(
                self._model_name,
                dtype="auto",
                device_map="auto",
                token=hf_token
            )
            self._respond = self._respond_qwen

        elif self._model_name == "microsoft/Phi-4-mini-instruct":
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self._model_name, token=hf_token)
            self._model = AutoModelForCausalLM.from_pretrained(
                self._model_name,
                dtype="auto",
                device_map="auto",
                token=hf_token
            )
            self._respond = self._respond_phi

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

    def _respond_qwen(self, messages: list[dict]) -> str:
        try:
            text = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False
            )
            model_inputs = self._tokenizer([text], return_tensors="pt").to(self._model.device)
            generated_ids = self._model.generate(
                **model_inputs,
                max_new_tokens=1024
            )
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()
            try:
                index = len(output_ids) - output_ids[::-1].index(151668)
            except ValueError:
                index = 0
            return self._tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip()
        except Exception as e:
            logger.error("Błąd modelu Qwen: %s", e)
            raise

    def _respond_phi(self, messages: list[dict]) -> str:
        try:
            text = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = self._tokenizer([text], return_tensors="pt").to(self._model.device)
            generated_ids = self._model.generate(
                **model_inputs,
                max_new_tokens=1024
            )
            output_ids = generated_ids[0][len(model_inputs.input_ids[0]):]
            return self._tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        except Exception as e:
            logger.error("Błąd modelu Phi: %s", e)
            raise
