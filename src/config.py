from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class all settings."""

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
        """Get database url."""
        return f'sqlite+aiosqlite:///./{self.sqlite_file}'

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()  # type: ignore
