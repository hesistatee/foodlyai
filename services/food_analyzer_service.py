from config import config
import json
import logging
from static.texts import PROMPT_FOR_PRODUCT_COMPOSITION_ANALYZE, TEXT_FOR_PRODUCT_COMPOSITION_ANALYZE, PROMPT_FOR_CALORIE_ANALYSIS, TEXT_FOR_CALORIE_ANALYSIS
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class FoodAnalyzer:
    """Анализатор состава продуктов питания с использованием POLZA_AI API."""
    
    def __init__(self):
        """Инициализация асинхронного клиента OpenAI с конфигурацией из config."""
        self.client = AsyncOpenAI(
            base_url=config.POLZA_AI_BASE_URL,
            api_key=config.POLZA_AI_API_KEY,
        )
        self.model = config.GPT_MODEL
        self.max_tokens = config.GPT_MAX_TOKENS
        
    async def analyze_product_composition(self, base64_image: str) -> dict:
        """
        Анализирует состав продукта по изображению (асинхронно).
        """
        try:
            logging.info('Отправлен асинхронный запрос на разбор фото')
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": PROMPT_FOR_PRODUCT_COMPOSITION_ANALYZE
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": TEXT_FOR_PRODUCT_COMPOSITION_ANALYZE
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
            
            logging.info('Фото разобрано асинхронно')
            description = response.choices[0].message.content
            return json.loads(description)
            
        except json.JSONDecodeError as e:
            logging.error(f"Не удалось распарсить ответ от API: {str(e)}")
            raise ValueError("Не удалось распарсить ответ от API") from e
        except Exception as e:
            logging.error(f'Ошибка при анализе продукта: {str(e)}')
            raise RuntimeError(f"Ошибка при анализе продукта: {e}") from e
        
    async def analyze_product_calories(self, base64_image: str) -> dict:
        """
        Анализирует калорийность продукта по изображению (асинхронно).
        """
        try:
            logging.info('Отправлен асинхронный запрос на разбор фото для анализа калорий')
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": PROMPT_FOR_CALORIE_ANALYSIS
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": TEXT_FOR_CALORIE_ANALYSIS
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
            
            logging.info('Фото разобрано для анализа калорий')
            description = response.choices[0].message.content
            return json.loads(description)
            
        except json.JSONDecodeError as e:
            logging.error(f"Не удалось распарсить ответ от API: {str(e)}")
            raise ValueError("Не удалось распарсить ответ от API") from e
        except Exception as e:
            logging.error(f'Ошибка при анализе калорий продукта: {str(e)}')
            raise RuntimeError(f"Ошибка при анализе калорий продукта: {e}") from e