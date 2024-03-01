from functools import lru_cache

from pydantic import Extra
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Main configuration
    """
    app_name: str = "AIGC-API"
    app_secret_key: str = "secret"
    app_algorithm: str = "HS256"
    app_debug: bool = False
    """
    OpenAI configuration
    """
    openai_api_key: str = ""  # OpenAI API key
    openai_base_url: str = "https://api.openai.com/v1"  # OpenAI API base URL
    """
    Database configuration
    """
    db_host: str = "localhost"  # Database host
    db_port: int = 3306  # Database port
    db_user: str = "aigc"  # Database user
    db_password: str = "admin"  # Database password
    db_name: str = "aigc"  # Database name
    db_charset: str = "utf8mb4"  # Database charset
    db_auto_migrate: bool = False  # Database auto migration
    """
    Logger configuration
    """
    logger_dir: str = "./logs"  # Logger directory

    """
    Datasets configuration
    """
    datasets_device: str = "cpu"  # Device for datasets
    datasets_model_name: str = "uer/sbert-base-chinese-nli"  # Model name for datasets

    """
    Storage configuration
    """
    storage_dir: str = "./storage"  # Storage directory

    model_config = SettingsConfigDict(env_file=".env", extra=Extra.allow)  # Configuration dictionary


@lru_cache
def get_config():
    return Config()
