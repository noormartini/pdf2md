"""Tests for strategies/hybrid.py — verify text + image multimodal construction."""

from strategies.hybrid import hybrid_strategy
from strategies.result import ConversionResult


def test_hybrid_strategy_returns_conversion_result():
    def fake(*args):
        return "# Hi", 13

    result = hybrid_strategy(
        base_url="x", model_name="m",
        text="page text", images=["b64"],
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    assert isinstance(result, ConversionResult)
    assert result.token_usage == 13


def test_hybrid_strategy_user_content_starts_with_text_block():
    captured = {}

    def fake(base_url, model, messages, temp, max_tokens):
        captured["messages"] = messages
        return "out", None

    hybrid_strategy(
        base_url="x", model_name="m",
        text="extracted page", images=["IMG_A", "IMG_B"],
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    user_content = captured["messages"][1]["content"]
    assert user_content[0]["type"] == "text"
    assert "extracted page" in user_content[0]["text"]


def test_hybrid_strategy_appends_all_images_after_text():
    captured = {}

    def fake(base_url, model, messages, temp, max_tokens):
        captured["messages"] = messages
        return "out", None

    hybrid_strategy(
        base_url="x", model_name="m",
        text="t", images=["IMG_A", "IMG_B"],
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    user_content = captured["messages"][1]["content"]
    assert len(user_content) == 3  # 1 text + 2 images
    assert [b["type"] for b in user_content] == ["text", "image_url", "image_url"]
    assert "IMG_A" in user_content[1]["image_url"]["url"]
    assert "IMG_B" in user_content[2]["image_url"]["url"]
