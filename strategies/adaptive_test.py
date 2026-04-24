"""Tests for strategies/adaptive.py — analyze_page classification and routing."""

from unittest.mock import MagicMock

from strategies.adaptive import analyze_page, adaptive_strategy, PageType
from strategies.result import ConversionResult


# ---------------------------------------------------------------------------
# Fake fitz.Page helpers
# ---------------------------------------------------------------------------

def _fake_page(text="", image_count=0, drawing_count=0):
    page = MagicMock()
    page.get_text.return_value = text
    page.get_images.return_value = [object()] * image_count
    page.get_drawings.return_value = [
        {"rect": MagicMock(width=10, height=10)} for _ in range(drawing_count)
    ]
    return page


# ---------------------------------------------------------------------------
# analyze_page — classification
# ---------------------------------------------------------------------------

def test_analyze_page_classifies_text_page():
    page = _fake_page(text="A" * 200)
    result = analyze_page(page)
    assert result.page_type == PageType.TEXT
    assert result.confidence >= 0.9


def test_analyze_page_classifies_empty_page():
    page = _fake_page(text="")
    result = analyze_page(page)
    assert result.page_type == PageType.EMPTY


def test_analyze_page_classifies_image_heavy_page():
    page = _fake_page(text="A" * 200, image_count=4)
    result = analyze_page(page)
    assert result.page_type == PageType.IMAGE


def test_analyze_page_classifies_mixed_page_with_one_image():
    page = _fake_page(text="A" * 200, image_count=1)
    result = analyze_page(page)
    assert result.page_type == PageType.MIXED


def test_analyze_page_classifies_formula_page_via_math_symbol():
    page = _fake_page(text="∑ something short")
    result = analyze_page(page)
    assert result.page_type == PageType.FORMULA


def test_analyze_page_classifies_formula_page_via_vector_paths():
    page = _fake_page(text="short", drawing_count=35)
    result = analyze_page(page)
    assert result.page_type == PageType.FORMULA


def test_analyze_page_returns_correct_counts():
    page = _fake_page(text="hello world", image_count=2, drawing_count=5)
    result = analyze_page(page)
    assert result.image_count == 2
    assert result.vector_path_count == 5
    assert result.text_length == len("hello world")


# ---------------------------------------------------------------------------
# adaptive_strategy — routing
# ---------------------------------------------------------------------------

_fake_result = ConversionResult(markdown="# Out", timing_ms=10.0, token_usage=5)


def _fake_text(**kwargs):
    return _fake_result


def _fake_image(**kwargs):
    return _fake_result


def test_adaptive_empty_page_returns_skipped_without_llm_call():
    result = adaptive_strategy(
        base_url="x", model_name="m",
        pdf_path="x.pdf", page_num=0, page_image="img",
        page_type=PageType.EMPTY,
        temperature=0.0, max_tokens=10,
    )
    assert result.markdown == "*[Empty page — skipped]*"
    assert result.timing_ms == 0.0


def test_adaptive_text_page_routes_to_text_strategy():
    captured = {}

    def fake_text(**kwargs):
        captured.update(kwargs)
        return _fake_result

    result = adaptive_strategy(
        base_url="x", model_name="m",
        pdf_path="x.pdf", page_num=0, page_image="img",
        page_type=PageType.TEXT,
        temperature=0.2, max_tokens=100,
        text_call=fake_text,
        image_call=_fake_image,
    )
    assert captured["prompt_variant"] == "text"
    assert result.markdown == "# Out"


def test_adaptive_formula_page_routes_to_image_strategy_with_formula_prompt():
    captured = {}

    def fake_image(**kwargs):
        captured.update(kwargs)
        return _fake_result

    adaptive_strategy(
        base_url="x", model_name="m",
        pdf_path="x.pdf", page_num=2, page_image="img",
        page_type=PageType.FORMULA,
        temperature=0.0, max_tokens=10,
        figures_dir="out/figures", figure_offset=5,
        text_call=_fake_text,
        image_call=fake_image,
    )
    assert captured["prompt_variant"] == "formula"
    assert captured["page_num"] == 2
    assert captured["figures_dir"] == "out/figures"
    assert captured["figure_offset"] == 5


def test_adaptive_image_page_routes_to_image_strategy_with_diagram_prompt():
    captured = {}

    def fake_image(**kwargs):
        captured.update(kwargs)
        return _fake_result

    adaptive_strategy(
        base_url="x", model_name="m",
        pdf_path="x.pdf", page_num=0, page_image="img",
        page_type=PageType.IMAGE,
        temperature=0.0, max_tokens=10,
        text_call=_fake_text,
        image_call=fake_image,
    )
    assert captured["prompt_variant"] == "diagram"


def test_adaptive_mixed_page_routes_to_image_strategy_with_default_prompt():
    captured = {}

    def fake_image(**kwargs):
        captured.update(kwargs)
        return _fake_result

    adaptive_strategy(
        base_url="x", model_name="m",
        pdf_path="x.pdf", page_num=0, page_image="img",
        page_type=PageType.MIXED,
        temperature=0.0, max_tokens=10,
        text_call=_fake_text,
        image_call=fake_image,
    )
    assert captured["prompt_variant"] == "default"
