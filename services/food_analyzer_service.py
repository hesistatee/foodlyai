import logging
from typing import Any

from static.texts import (
    PROMPT_FOR_CALORIE_ANALYSIS,
    PROMPT_FOR_PRODUCT_COMPOSITION_ANALYZE,
    TEXT_FOR_CALORIE_ANALYSIS,
    TEXT_FOR_PRODUCT_COMPOSITION_ANALYZE,
)

from .openai_service import OpenAIService

logger = logging.getLogger(__name__)


class FoodAnalyzer:
    def __init__(self, openai_service: OpenAIService):
        self.openai_service: OpenAIService = openai_service

    async def analyze_product_composition(
        self, base64_image: str | None
    ) -> dict[Any, Any]:
        """
        Анализирует состав продукта по изображению (асинхронно).
        """
        return await self.openai_service.send_image_request(
            content=PROMPT_FOR_PRODUCT_COMPOSITION_ANALYZE,
            text=TEXT_FOR_PRODUCT_COMPOSITION_ANALYZE,
            base64_image=base64_image,
        )

    async def analyze_product_calories(
        self, base64_image: str | None
    ) -> dict[Any, Any]:
        """
        Анализирует калорийность продукта по изображению (асинхронно).
        """
        return await self.openai_service.send_image_request(
            content=PROMPT_FOR_CALORIE_ANALYSIS,
            text=TEXT_FOR_CALORIE_ANALYSIS,
            base64_image=base64_image,
        )
