from config import config
import json
import logging
from openai import AsyncOpenAI


logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        """Инициализация асинхронного клиента OpenAI с конфигурацией из config."""
        self.client = AsyncOpenAI(
            base_url=config.POLZA_AI_BASE_URL,
            api_key=config.POLZA_AI_API_KEY,
        )
        self.model = config.GPT_MODEL
        self.max_tokens = config.GPT_MAX_TOKENS
        
    async def _send_image_request(self, content: str, text: str, base64_image: str):
        try:
            logging.info('Отправлен асинхронный запрос на разбор фото')
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": content
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": text
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            logging.info('Фото разобрано')
            description = response.choices[0].message.content
            return json.loads(description)
            
        except json.JSONDecodeError as e:
            logging.error(f"Не удалось распарсить ответ от API: {str(e)}")
            raise ValueError("Не удалось распарсить ответ от API") from e
        except Exception as e:
            logging.error(f'Ошибка: {str(e)}')
            raise RuntimeError(f"Ошибка: {e}") from e