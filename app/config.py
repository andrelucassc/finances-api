from functools import lru_cache
from typing import Union

from pydantic import BaseSettings


class Settings(BaseSettings):
    db_client_lib: str
    db_dsn: str
    db_user: str = "dbuser"
    db_password: str = "dbpassword"
    db_wallet: str

    default_payment_user: str


@lru_cache(maxsize=None)
def get_settings() -> Settings:
    """Get settigns for the DB"""
    return Settings()
