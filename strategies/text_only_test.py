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
    mock.assert_called_once_with(
        "my.pdf", pages=[3], page_chunks=True,
        write_images=True, image_path="figures", image_size_limit=0,
    )


def test_text_strategy_returns_empty_string_when_no_chunks():
    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=[]):
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
        )
    assert result.markdown == ""
    assert result.token_usage is None


def test_llm_call_is_used_when_provided():
    """When llm_call is provided, the raw pymupdf4llm output is passed through
    the LLM so that math symbols are converted to LaTeX."""
    fake_token_usage = {"prompt_tokens": 10, "completion_tokens": 20}

    def fake_llm(*args, **kwargs):
        return "# Hello\n\n$E = mc^2$", fake_token_usage

    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=_FAKE_CHUNKS):
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
            llm_call=fake_llm,
        )
    assert result.markdown == "# Hello\n\n$E = mc^2$"
    assert result.token_usage == fake_token_usage


def test_no_llm_call_returns_raw_pymupdf4llm_output():
    """Without llm_call, the raw pymupdf4llm output is returned directly."""
    with patch("strategies.text_only.pymupdf4llm.to_markdown", return_value=_FAKE_CHUNKS):
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
        )
    assert result.markdown == "# Hello\n\nSome paragraph."
    assert result.token_usage is None


def test_pre_extracted_markdown_skips_pymupdf4llm_call():
    """When pre_extracted_markdown is provided, no per-page pymupdf4llm
    call should fire — callers can bulk-extract once and feed chunks in."""
    with patch("strategies.text_only.pymupdf4llm.to_markdown") as mock:
        result = text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
            pre_extracted_markdown="# Pre-extracted\n\nbody",
        )
    mock.assert_not_called()
    assert result.markdown == "# Pre-extracted\n\nbody"
    assert result.token_usage is None


def test_pre_extracted_markdown_still_runs_llm_when_provided():
    """pre_extracted_markdown bypasses extraction but is still passed
    through the LLM when llm_call is given (e.g. for math cleanup)."""
    captured_user_content = {}

    def fake_llm(base_url, model_name, messages, temperature, max_tokens):
        captured_user_content["text"] = messages[-1]["content"]
        return "# Cleaned\n\n$x = 1$", None

    with patch("strategies.text_only.pymupdf4llm.to_markdown") as mock:
        text_strategy(
            base_url="x", model_name="m",
            pdf_path="doc.pdf", page_num=0,
            temperature=0.0, max_tokens=10,
            pre_extracted_markdown="# Raw\n\nx = 1",
            llm_call=fake_llm,
        )
    mock.assert_not_called()
    assert "# Raw" in captured_user_content["text"]
