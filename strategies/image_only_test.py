"""Tests for strategies/image_only.py — image saving and reference generation."""

import base64
from pathlib import Path

import pytest

from strategies.image_only import image_strategy
from strategies.result import ConversionResult

# Minimal 1x1 white PNG (valid PNG bytes)
_PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00"
    b"\x00\x11\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)
_B64_PNG = base64.b64encode(_PNG_1X1).decode()


def test_image_strategy_returns_conversion_result(tmp_path):
    result = image_strategy(
        base_url="x", model_name="m", images=[_B64_PNG],
        temperature=0.0, max_tokens=10,
        page_num=0, figures_dir=str(tmp_path / "figures"),
    )
    assert isinstance(result, ConversionResult)
    assert result.token_usage is None
    assert result.timing_ms >= 0


def test_image_strategy_saves_image_file(tmp_path):
    figures = tmp_path / "figures"
    image_strategy(
        base_url="x", model_name="m", images=[_B64_PNG],
        temperature=0.0, max_tokens=10,
        page_num=2, figures_dir=str(figures),
    )
    assert (figures / "fig-2-0.png").exists()


def test_image_strategy_inline_markdown(tmp_path):
    result = image_strategy(
        base_url="x", model_name="m", images=[_B64_PNG],
        temperature=0.0, max_tokens=10,
        page_num=1, figures_dir=str(tmp_path / "figures"), figure_offset=3,
    )
    assert result.markdown == "![Figure 3][fig-1-0]"


def test_image_strategy_ref_definition(tmp_path):
    result = image_strategy(
        base_url="x", model_name="m", images=[_B64_PNG],
        temperature=0.0, max_tokens=10,
        page_num=1, figures_dir=str(tmp_path / "figures"), figure_offset=3,
    )
    assert result.image_refs == ['[fig-1-0]: figures/fig-1-0.png "Figure 3"']


def test_image_strategy_multiple_images(tmp_path):
    figures = tmp_path / "figures"
    result = image_strategy(
        base_url="x", model_name="m", images=[_B64_PNG, _B64_PNG],
        temperature=0.0, max_tokens=10,
        page_num=0, figures_dir=str(figures), figure_offset=1,
    )
    assert "![Figure 1][fig-0-0]" in result.markdown
    assert "![Figure 2][fig-0-1]" in result.markdown
    assert len(result.image_refs) == 2
    assert (figures / "fig-0-0.png").exists()
    assert (figures / "fig-0-1.png").exists()


def test_image_strategy_creates_figures_dir(tmp_path):
    figures = tmp_path / "new" / "figures"
    assert not figures.exists()
    image_strategy(
        base_url="x", model_name="m", images=[_B64_PNG],
        temperature=0.0, max_tokens=10,
        page_num=0, figures_dir=str(figures),
    )
    assert figures.exists()


def test_llm_call_is_ignored(tmp_path):
    called = []
    def fake(*a, **kw): called.append(True)

    image_strategy(
        base_url="x", model_name="m", images=[_B64_PNG],
        temperature=0.0, max_tokens=10,
        page_num=0, figures_dir=str(tmp_path / "figures"),
        llm_call=fake,
    )
    assert not called
