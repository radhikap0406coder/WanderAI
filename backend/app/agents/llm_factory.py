
from typing import Optional, Any
from app.config import settings


def get_llm(
    api_key_override: Optional[str] = None,
    provider_override: Optional[str] = None
) -> Optional[Any]:
    """
    Returns a configured Google Gemini LangChain chat model.
    Returns None when Gemini is unavailable, allowing agents
    to use their built-in fallback logic.
    """
    provider = (provider_override or "auto").lower()

    # Support only Gemini and automatic provider selection.
    if provider not in ("gemini", "auto"):
        print(f"[LLM Factory Warning] Unsupported provider: {provider}")
        return None

    # Prefer a user-supplied key when Gemini is explicitly selected.
    gemini_key = (
        api_key_override if provider == "gemini" and api_key_override
        else settings.GEMINI_API_KEY
        or (
            api_key_override
            if provider == "auto"
            and api_key_override
            and api_key_override.startswith("AIza")
            else ""
        )
    )

    if not gemini_key:
        return None

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key,
            temperature=0.4,
        )

    except Exception as e:
        print(
            f"[LLM Factory Warning] Could not initialize Gemini ({e}). "
            "Using built-in fallback where available."
        )
        return None
