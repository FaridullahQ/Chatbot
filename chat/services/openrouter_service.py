# chat/services/openrouter_service.py
import os
import json
import time
import logging
import requests
from typing import Generator, Optional, Dict, Any
from dotenv import load_dotenv

# ============================================
# 🔐 Load environment variables (shell & server)
# ============================================
load_dotenv()

logger = logging.getLogger(__name__)

# ============================================
# 🔧 Config (env-overridable)
# ============================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model & generation controls (tuned for speed)
DEFAULT_MODEL = os.getenv("AI_MODEL", "openai/gpt-3.5-turbo-0125")
AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.4"))
AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "400"))
AI_TOP_P = float(os.getenv("AI_TOP_P", "1.0"))

# Optional project metadata (helps OpenRouter dashboard)
PROJECT_REFERER = os.getenv("PROJECT_REFERER", "http://localhost:8000")
PROJECT_TITLE = os.getenv("PROJECT_TITLE", "QaderiChat")

# Networking
DEFAULT_TIMEOUT = int(os.getenv("HTTP_TIMEOUT_SECONDS", "45"))
RETRY_COUNT = int(os.getenv("HTTP_RETRY_COUNT", "2"))
RETRY_BACKOFF = float(os.getenv("HTTP_RETRY_BACKOFF", "0.75"))  # seconds


def _build_headers() -> Dict[str, str]:
    """
    Build request headers, including optional project metadata.
    Some gateways expect either 'Referer' or 'HTTP-Referer', so we include both safely.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Title": PROJECT_TITLE,
        # Both variants (harmless to include together)
        "Referer": PROJECT_REFERER,
        "HTTP-Referer": PROJECT_REFERER,
    }
    return headers


def _request_with_retries(method: str, url: str, **kwargs) -> requests.Response:
    """
    Minimal retry wrapper for transient network errors / 429s.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(RETRY_COUNT + 1):
        try:
            resp = requests.request(method, url, timeout=DEFAULT_TIMEOUT, **kwargs)
            # If rate limited, back off and retry (simple strategy)
            if resp.status_code == 429 and attempt < RETRY_COUNT:
                logger.warning("⏳ Rate limit (429). Backing off and retrying...")
                time.sleep(RETRY_BACKOFF * (attempt + 1))
                continue
            return resp
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            if attempt < RETRY_COUNT:
                logger.warning(f"🌐 Transient network error ({e}). Retrying...")
                time.sleep(RETRY_BACKOFF * (attempt + 1))
            else:
                raise
    # Should not reach here; raise last exception if present
    if last_exc:
        raise last_exc
    raise RuntimeError("Unknown networking error while contacting OpenRouter")


def openrouter_chat(message: str, model: Optional[str] = None) -> Dict[str, Any]:
    """
    🧠 Send a single-turn chat message to OpenRouter and return a normalized dict.

    Returns:
        {
          "success": bool,
          "message": str,         # assistant content (if success)
          "metadata": {...},      # raw response (optional)
          "error": "..."          # error string (if failed)
        }
    """
    if not OPENROUTER_API_KEY:
        return {
            "success": False,
            "message": "⚠️ OpenRouter API key is missing. Set OPENROUTER_API_KEY in your .env.",
            "error": "Missing API key",
        }

    model = model or DEFAULT_MODEL

    headers = _build_headers()
    payload = {
        "model": model,
        "temperature": AI_TEMPERATURE,
        "max_tokens": AI_MAX_TOKENS,
        "top_p": AI_TOP_P,
        "messages": [
            {"role": "system", "content": "You are QaderiChat — a friendly assistant."},
            {"role": "user", "content": message},
        ],
    }

    try:
        resp = _request_with_retries("POST", OPENROUTER_URL, headers=headers, json=payload)

        # Common error surfaces
        if resp.status_code == 401:
            logger.error(f"🚨 Unauthorized (401): {resp.text}")
            return {
                "success": False,
                "message": "⚠️ Invalid or expired OpenRouter API key. Please verify your .env.",
                "error": "Unauthorized (401)",
            }

        if resp.status_code == 429:
            logger.warning(f"⏳ Rate limit (429): {resp.text}")
            return {
                "success": False,
                "message": "⏳ Rate limit reached. Please wait and try again.",
                "error": "Rate limit (429)",
            }

        if resp.status_code != 200:
            logger.error(f"⚠️ API returned {resp.status_code}: {resp.text}")
            return {
                "success": False,
                "message": f"⚠️ OpenRouter error ({resp.status_code}).",
                "error": resp.text,
            }

        data = resp.json()

        # Expected shape: { choices: [ { message: { content: "..." } } ] }
        if "choices" in data and data["choices"]:
            msg = data["choices"][0].get("message", {})
            content = msg.get("content", "")
            return {"success": True, "message": content, "metadata": data}

        logger.warning(f"⚠️ Unexpected response format: {data}")
        return {
            "success": False,
            "message": "⚠️ Unexpected response format from OpenRouter.",
            "error": data,
        }

    except requests.exceptions.Timeout:
        logger.exception("⏳ OpenRouter request timed out.")
        return {"success": False, "message": "⏳ Request timed out. Try again.", "error": "Timeout"}
    except requests.exceptions.RequestException as e:
        logger.exception(f"❌ OpenRouter API error: {e}")
        return {
            "success": False,
            "message": "⚠️ Failed to connect to OpenRouter.",
            "error": str(e),
        }
    except Exception as e:
        logger.exception(f"❌ Unexpected error: {e}")
        return {"success": False, "message": "⚠️ Unexpected error.", "error": str(e)}


# ===============================================================
# 🔴 Optional: Streaming (for live “typing” UX)
#    You can wire this to a Django StreamingHttpResponse endpoint.
# ===============================================================
def openrouter_stream(message: str, model: Optional[str] = None) -> Generator[str, None, None]:
    """
    Stream assistant output as it’s generated. Yields delta text chunks.

    Usage in a view:
        def stream_message(request):
            def gen():
                for chunk in openrouter_stream("Hello"):
                    yield chunk
            return StreamingHttpResponse(gen(), content_type="text/plain")
    """
    if not OPENROUTER_API_KEY:
        yield "[STREAM ERROR] OpenRouter API key is missing."
        return

    model = model or DEFAULT_MODEL
    headers = _build_headers()
    headers["Accept"] = "text/event-stream"  # SSE stream

    payload = {
        "model": model,
        "temperature": AI_TEMPERATURE,
        "max_tokens": AI_MAX_TOKENS,
        "top_p": AI_TOP_P,
        "stream": True,  # 🔑 enable streaming
        "messages": [
            {"role": "system", "content": "You are QaderiChat — a friendly assistant."},
            {"role": "user", "content": message},
        ],
    }

    try:
        with requests.post(
            OPENROUTER_URL, headers=headers, json=payload, stream=True, timeout=DEFAULT_TIMEOUT
        ) as r:
            # Raise early for auth or 4xx/5xx
            if r.status_code != 200:
                # Read one chunk of error body (avoid consuming whole stream)
                try:
                    err_preview = next(r.iter_lines(decode_unicode=True))
                except StopIteration:
                    err_preview = ""
                yield f"[STREAM ERROR] HTTP {r.status_code} {err_preview}"
                return

            for raw in r.iter_lines(decode_unicode=True):
                if not raw:
                    continue
                if raw.startswith("data: "):
                    body = raw[6:].strip()
                    if body == "[DONE]":
                        break
                    try:
                        obj = json.loads(body)
                        # choices[0].delta.content pattern
                        delta = (
                            obj.get("choices", [{}])[0]
                              .get("delta", {})
                              .get("content", "")
                        )
                        if delta:
                            yield delta
                    except Exception:
                        # If parsing fails, skip silently (or yield "")
                        continue
    except Exception as e:
        yield f"[STREAM ERROR] {e}"
