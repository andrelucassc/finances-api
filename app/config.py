from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    db_client_lib: str
    db_dsn: str
    db_user: str = "dbuser"
    db_password: str = "dbpassword"
    db_wallet: str

    default_payment_user: str

    pbi_api: Optional[str] = None

    class Config:
        env_file = "env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    """Get settigns for the DB"""
    return Settings()
