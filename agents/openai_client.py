# agents/openai_client.py

import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
load_dotenv(ENV_PATH)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        f"OPENAI_API_KEY not found. Make sure .env file exists at: {ENV_PATH}"
    )

client = OpenAI(api_key=api_key)

def get_client():
    return client
