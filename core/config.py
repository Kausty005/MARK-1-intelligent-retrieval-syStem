# core/config.py 

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # The code will get the key from the environment. The fallback is just a placeholder.
    GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "THIS_IS_A_PLACEHOLDER_NOT_A_REAL_KEY")

    # The static bearer token is not a secret, it's a requirement from the hackathon.
    # It's okay for this to be in the code.
    API_BEARER_TOKEN: str = "8fbf8f7b322d483ae606bfa7df9f1ea320a16afe11608414fce857efab5d00de"

    class Config:
        case_sensitive = True

settings = Settings()