import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    BOT_TOKEN: str = os.getenv('BOT_TOKEN')
    POLZA_AI_API_KEY: str = os.getenv('POLZA_AI_API_KEY')
    POLZA_AI_BASE_URL: str = os.getenv('POLZA_AI_BASE_URL', 'https://api.polza.ai/api/v1')
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///food_analyzer.db')
    
    # GPT settings
    GPT_MODEL: str = os.getenv('GPT_MODEL', 'openai/gpt-4o')
    GPT_MAX_TOKENS: int = int(os.getenv('GPT_MAX_TOKENS', 1000))


config = Config()
