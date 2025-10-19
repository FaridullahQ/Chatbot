import os
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-3.5-turbo"


def openrouter_chat(message: str, model: str = None) -> dict:
    """Send a chat message to OpenRouter and return the assistant's reply."""
    if not OPENROUTER_API_KEY:
        return {
            "success": False,
            "message": "❌ OpenRouter API key not configured.",
            "error": "Missing API key"
        }

    model = model or DEFAULT_MODEL
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are QaderiChat — a friendly assistant."},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            return {"success": True, "message": reply, "metadata": data}
        else:
            return {"success": False, "message": "⚠️ Unexpected response format.", "error": data}

    except requests.exceptions.RequestException as e:
        logger.exception(f"❌ OpenRouter API error: {e}")
        return {"success": False, "message": f"API error: {e}", "error": str(e)}
