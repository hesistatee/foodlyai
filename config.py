import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    POLZA_AI_API_KEY: str = os.getenv("POLZA_AI_API_KEY", "")
    POLZA_AI_BASE_URL: str = os.getenv("POLZA_AI_BASE_URL", "")

    # GPT settings
    GPT_MODEL: str = os.getenv("GPT_MODEL", "")
    GPT_MAX_TOKENS: int = int(os.getenv("GPT_MAX_TOKENS", 1000))

    # Subscription
    TRIAL_DAYS: int = int(os.getenv("TRIAL_DAYS", 0))
    MAIN_SUBSCRIPTION_DAYS: int = int(os.getenv("MAIN_SUBSCRIPTION_DAYS", 30))

    # Payment
    YOOKASSA_PAYMENT_TOKEN: str = os.getenv("YOOKASSA_PAYMENT_TOKEN", "")

    # Database
    DB: str = os.getenv("DB", "")
    DB_DRIVER: str = os.getenv("DB_DRIVER", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: int = int(os.getenv("DB_PORT", ""))
    DB_NAME: str = os.getenv("DB_NAME", "")

    @property
    def DATABASE_URL(self):
        return f"{self.DB}+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
