from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    app_name: str = "Project Management System API"

    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    db_pool_size : int
    db_max_overflow :int
    db_pool_timeout:int

    jwt_secret_key :str
    jwt_algorithm : str

    access_token_expire_minutes : int
    refresh_token_expire_days :int


    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )



@lru_cache
def get_settings() -> Settings:
    return Settings()
