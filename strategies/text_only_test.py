"""Tests for strategies/text_only.py — pymupdf4llm-based conversion."""

from unittest.mock import patch

from strategies.result import ConversionResult
from strategies.text_only import text_strategy

_FAKE_CHUNKS = [{"text": "# Hello\n\nSome paragraph."}]


def test_text_strategy_returns_conversion_result():
    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=_FAKE_CHUNKS):
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
        )
    assert isinstance(result, ConversionResult)
    assert result.timing_ms >= 0
    assert result.token_usage is None


def test_text_strategy_returns_markdown_from_pymupdf4llm():
    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=_FAKE_CHUNKS):
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
        )
    assert result.markdown == "# Hello\n\nSome paragraph."


def test_text_strategy_passes_correct_page_to_pymupdf4llm():
    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=_FAKE_CHUNKS) as mock:
        text_strategy(
            base_url="x", model_name="m",
            pdf_path="my.pdf", page_num=3,
            temperature=0.0, max_tokens=10,
        )
    mock.assert_called_once_with("my.pdf", pages=[3], page_chunks=True)


def test_text_strategy_returns_empty_string_when_no_chunks():
    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=[]):
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
        )
    assert result.markdown == ""
    assert result.token_usage is None


def test_llm_call_argument_is_ignored():
    called = []

    def fake_llm(*args, **kwargs):
        called.append(True)
        return "should not appear", 99

    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=_FAKE_CHUNKS):
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
            llm_call=fake_llm,
        )
    assert not called
    assert result.token_usage is None
