from langdetect import detect, LangDetectException


_LANGUAGE_NAMES: dict[str, str] = {
    "de": "German",
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "nl": "Dutch",
}


def detect_language(text: str) -> str:
    """Detect the primary language of the text.

    Returns an ISO 639-1 code (e.g. 'de', 'en').
    Defaults to 'en' if detection fails or text is too short.
    """
    if len(text.strip()) < 20:
        return "en"
    try:
        return detect(text)
    except LangDetectException:
        return "en"


def language_name(code: str) -> str:
    """Return a human-readable name for an ISO 639-1 language code."""
    return _LANGUAGE_NAMES.get(code, code.upper())
