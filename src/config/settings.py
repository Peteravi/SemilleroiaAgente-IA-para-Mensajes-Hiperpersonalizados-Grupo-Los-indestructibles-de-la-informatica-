from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    llm_provider: str = "none"
    openai_api_key: str = ""


def get_settings() -> Settings:
    load_dotenv(override=False)
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "none").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
    )
