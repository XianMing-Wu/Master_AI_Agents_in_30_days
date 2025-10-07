"""Utilities shared across tasks."""

import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import set_default_openai_client, set_tracing_disabled


def configure_closeai_client(base_url: str = "https://api.openai-proxy.org/v1") -> AsyncOpenAI:
    """Configure the default AsyncOpenAI client to use CloseAI as a proxy."""

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    client = AsyncOpenAI(base_url=base_url, api_key=api_key)
    set_default_openai_client(client)
    set_tracing_disabled(True)
    return client
