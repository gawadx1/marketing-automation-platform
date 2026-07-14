from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, SecretStr
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Marketing Automation Platform"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="production", validate_default=True)
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: SecretStr = Field(default=SecretStr("change-me-in-production"))

    POSTGRES_USER: str = "marketing_user"
    POSTGRES_PASSWORD: SecretStr = Field(default=SecretStr("marketing_pass"))
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "marketing_platform"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False
    DATABASE_SSL_MODE: str = "prefer"

    @property
    def DATABASE_URL(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        password = self.POSTGRES_PASSWORD.get_secret_value()
        return (
            f"postgresql://{self.POSTGRES_USER}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL

    JWT_SECRET_KEY: SecretStr = Field(default=SecretStr("super-secret-key-change-in-production"))
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_ISSUER: str = "marketing-platform"

    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    CACHE_TTL_SECONDS: int = 300
    CACHE_PREFIX: str = "mkt:"

    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    SIMULATED_API_DELAY_MIN: float = 0.05
    SIMULATED_API_DELAY_MAX: float = 0.2
    MOCK_DATA_SEED: int = 42

    # Google Ads API
    GOOGLE_ADS_CLIENT_ID: Optional[str] = None
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = None
    GOOGLE_ADS_REFRESH_TOKEN: Optional[str] = None
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = None
    GOOGLE_ADS_LOGIN_CUSTOMER_ID: Optional[str] = None

    # Meta Ads API
    META_ADS_ACCESS_TOKEN: Optional[str] = None
    META_ADS_AD_ACCOUNT_ID: Optional[str] = None
    META_ADS_APP_ID: Optional[str] = None
    META_ADS_APP_SECRET: Optional[str] = None

    # HubSpot CRM API
    HUBSPOT_ACCESS_TOKEN: Optional[str] = None

    # Mailchimp API
    MAILCHIMP_API_KEY: Optional[str] = None
    MAILCHIMP_SERVER_PREFIX: Optional[str] = None

    # Google Analytics Data API
    GOOGLE_ANALYTICS_CREDENTIALS_JSON: Optional[str] = None
    GOOGLE_ANALYTICS_PROPERTY_ID: Optional[str] = None

    LOG_LEVEL: str = Field(default="INFO", validate_default=True)
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<7} | {name}:{function}:{line} | {message}"
    LOG_JSON_FORMAT: bool = False
    LOG_FILE_MAX_BYTES: int = 50 * 1024 * 1024
    LOG_FILE_BACKUP_COUNT: int = 10

    PROMETHEUS_ENABLED: bool = True
    SENTRY_DSN: Optional[str] = None

    CELERY_TASK_ALWAYS_EAGER: bool = False
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: list[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 1800
    CELERY_TASK_SOFT_TIME_LIMIT: int = 1500
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 200
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 1
    CELERY_TASK_ACKS_LATE: bool = True

    @field_validator("APP_ENV")
    @classmethod
    def validate_env(cls, v: str) -> str:
        allowed = {"development", "staging", "production", "testing"}
        if v.lower() not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}")
        return v.lower()

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    @property
    def IS_PRODUCTION(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def IS_DEVELOPMENT(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def IS_TESTING(self) -> bool:
        return self.APP_ENV == "testing"

    def get_jwt_secret(self) -> str:
        return self.JWT_SECRET_KEY.get_secret_value()

    def get_secret_key(self) -> str:
        return self.SECRET_KEY.get_secret_value()


@lru_cache()
def get_settings() -> Settings:
    return Settings()
