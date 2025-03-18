from pathlib import Path

import dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DEBUG: bool = False
    DOWNLOADING_ROOT_PATH: Path

    class Config:
        env_file = Path(BASE_DIR, 'settings', 'env')
        dotenv.load_dotenv(env_file)


settings = Settings()
