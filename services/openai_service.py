from typing import Any
from typing_extensions import Dict
from config import settings
import json
import logging
from openai import AsyncOpenAI


logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        """Инициализация асинхронного клиента OpenAI с конфигурацией из config."""
        self.client: AsyncOpenAI = AsyncOpenAI(
            base_url=settings.POLZA_AI_BASE_URL,
            api_key=settings.POLZA_AI_API_KEY,
        )
        self.model: str = settings.GPT_MODEL
        self.max_tokens: int = settings.GPT_MAX_TOKENS

    async def _send_image_request(
        self, content: str, text: str, base64_image: str | None
    ) -> dict[Any, Any]:
        try:
            logging.info("Отправлен асинхронный запрос на разбор фото")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": content},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                },
                            },
                        ],
                    },
                ],
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"},
            )

            logging.info("Фото разобрано")
            description = response.choices[0].message.content
            if not description:
                raise ValueError("Пустой ответ от API")

            decoded_description = json.loads(description)
            if not isinstance(decoded_description, dict):
                raise ValueError(f"Ожидался dict, получен {type(decoded_description)}")

            return decoded_description

        except json.JSONDecodeError as e:
            logging.error(f"Не удалось распарсить ответ от API: {str(e)}")
            raise ValueError("Не удалось распарсить ответ от API") from e
        except Exception as e:
            logging.error(f"Ошибка: {str(e)}")
            raise RuntimeError(f"Ошибка: {e}") from e
