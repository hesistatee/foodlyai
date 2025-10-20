import base64
import os
from datetime import datetime
from aiogram.types import Message
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    async def process_telegram_photo(self, message: Message) -> str | None:
        try:
            logging.info("Началась обработка фото")
            file_id = message.photo[-1].file_id if message.photo else None
            if file_id:
                file = await message.bot.get_file(file_id)
                file_path = file.file_path
                if file_path:
                    os.makedirs("temp", exist_ok=True)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    temp_file_path = f"temp/photo_{timestamp}_{message.message_id}.jpg"

                    await message.bot.download_file(file_path, temp_file_path)

                    with open(temp_file_path, "rb") as image_file:
                        base64_string = base64.b64encode(image_file.read()).decode(
                            "utf-8"
                        )

                    os.remove(temp_file_path)
                    temp_file_path = None

                    logging.info("Фото успешно обработалось")
                    return base64_string

        except Exception as e:
            logging.error(f"Ошибка обработки фото: {str(e)}")
            raise Exception(f"Ошибка обработки фото: {str(e)}")
