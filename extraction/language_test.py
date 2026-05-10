"""Tests for extraction/language.py."""

from extraction.language import detect_language, language_name


def test_detect_language_english():
    text = "This is a sample English text for language detection testing purposes."
    assert detect_language(text) == "en"


def test_detect_language_german():
    text = "Dies ist ein Beispieltext auf Deutsch für die Spracherkennung. Neuronale Netze werden häufig eingesetzt."
    assert detect_language(text) == "de"


def test_detect_language_short_text_defaults_to_english():
    assert detect_language("hi") == "en"


def test_detect_language_empty_defaults_to_english():
    assert detect_language("") == "en"


def test_language_name_known_codes():
    assert language_name("de") == "German"
    assert language_name("en") == "English"
    assert language_name("fr") == "French"


def test_language_name_unknown_code_returns_uppercase():
    assert language_name("xx") == "XX"
