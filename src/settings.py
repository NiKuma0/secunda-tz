import pydantic as pd
import pydantic_settings as pds


class AppSettings(pds.BaseSettings):
    model_config = pds.SettingsConfigDict(env_file='.env', extra='allow')

    POSTGRES_DSN: pd.PostgresDsn


settings = AppSettings()  # pyright: ignore[reportCallIssue]
