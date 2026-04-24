"""Tests for strategies/image_only.py — verify multimodal message construction."""

from strategies.image_only import image_strategy
from strategies.result import ConversionResult


def test_image_strategy_returns_conversion_result():
    def fake(*args, **kwargs):
        return "# Hi", 7

    result = image_strategy(
        base_url="x", model_name="m", images=["b64data"],
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    assert isinstance(result, ConversionResult)
    assert result.markdown == "# Hi"
    assert result.token_usage == 7


def test_image_strategy_wraps_each_image_as_image_url():
    captured = {}

    def fake(base_url, model, messages, temp, max_tokens):
        captured["messages"] = messages
        return "out", None

    image_strategy(
        base_url="x", model_name="m",
        images=["IMG_A", "IMG_B"],
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    user_content = captured["messages"][1]["content"]
    assert len(user_content) == 2
    assert user_content[0]["type"] == "image_url"
    assert "IMG_A" in user_content[0]["image_url"]["url"]
    assert user_content[0]["image_url"]["url"].startswith("data:image/png;base64,")
    assert "IMG_B" in user_content[1]["image_url"]["url"]


def test_image_strategy_no_text_block_in_user_content():
    """image-only must not include a text content block — that's hybrid's job."""
    captured = {}

    def fake(base_url, model, messages, temp, max_tokens):
        captured["messages"] = messages
        return "out", None

    image_strategy(
        base_url="x", model_name="m", images=["IMG"],
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    user_content = captured["messages"][1]["content"]
    assert all(block["type"] == "image_url" for block in user_content)


def test_image_strategy_handles_none_token_usage():
    def fake(*args, **kwargs):
        return "out", None

    result = image_strategy(
        base_url="x", model_name="m", images=["IMG"],
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    assert result.token_usage is None
