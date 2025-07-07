from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or a .env file."""

    sqlite_file: str = 'database.db'

    redis_host: str
    redis_port: int
    redis_password: str

    backend_cors_origins: str

    jwt_secret_key: str
    jwt_expire_minutes: int
    jwt_algorithm: str

    gpt_api_key: str

    host: str
    port: int

    @property
    def database_url(self) -> str:
        """Construct the full database URL for SQLAlchemy connection with aiosqlite driver."""
        return f'sqlite+aiosqlite:///./{self.sqlite_file}'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()  # type: ignore
