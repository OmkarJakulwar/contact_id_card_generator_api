# app/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Default theme for cards if not specified in the request.  This can be overridden by setting the ``theme`` field in the request body to a valid theme name.

    default_theme: str = "default"

    class Config:
        env_prefix = ""
        # Case insensitive environment variables allow variables like
        # ``DEFAULT_THEME`` to map to the attribute ``default_theme``【116483188812688†L369-L372】.
        case_sensitive = False


# Instantiate a global settings object.  This reads environment variables from this config class and makes them available throughout the application via import.  
settings = Settings()
