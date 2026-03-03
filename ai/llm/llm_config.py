# ai/llm/llm_config.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_model_config(tier="cheap"):
    """
    Tier-based configuration:
    - 'smart': For Architecture and Auditing (OpenAI GPT-4o)
    - 'cheap': For massive Code Generation (DeepSeek)
    """
    if tier == "smart":
        return {
            "model": os.getenv("AI_SMART_MODEL", "gpt-4o"), # Usamos gpt-4o para el Auditor
            "max_tokens": 4096,
            "temperature": 0.2,
            "provider": "openai"
        }
    else:
        return {
            "model": os.getenv("AI_CHEAP_MODEL", "deepseek-chat"), # DeepSeek para el grueso del código
            "max_tokens": 4096,
            "temperature": 0.1,
            "provider": "deepseek"
        }

def build_llm_client(provider="deepseek"):
    """Returns the correct client based on the provider."""
    if provider == "openai":
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    else:
        return OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("AI_BASE_URL", "https://api.deepseek.com/v1")
        )