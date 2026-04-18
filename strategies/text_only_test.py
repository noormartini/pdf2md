"""Tests for strategies/text_only.py — exercise message construction with a fake llm_call."""

from strategies.result import ConversionResult
from strategies.text_only import text_strategy


def test_text_strategy_returns_conversion_result_with_timing_and_tokens():
    def fake(base_url, model, messages, temp, max_tokens):
        return "# Hi", 42

    result = text_strategy(
        base_url="x",
        model_name="m",
        text="hello",
        temperature=0.0,
        max_tokens=10,
        llm_call=fake,
    )
    assert isinstance(result, ConversionResult)
    assert result.markdown == "# Hi"
    assert result.token_usage == 42
    assert result.timing_ms >= 0


def test_text_strategy_builds_system_and_user_messages():
    captured = {}

    def fake(base_url, model, messages, temp, max_tokens):
        captured["messages"] = messages
        return "out", None

    text_strategy(
        base_url="x",
        model_name="m",
        text="my page text",
        temperature=0.2,
        max_tokens=100,
        llm_call=fake,
    )
    msgs = captured["messages"]
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert msgs[1]["role"] == "user"
    assert "my page text" in msgs[1]["content"]


def test_text_strategy_passes_through_temperature_and_max_tokens():
    captured = {}

    def fake(base_url, model, messages, temp, max_tokens):
        captured["temp"] = temp
        captured["max_tokens"] = max_tokens
        return "out", None

    text_strategy(
        base_url="x",
        model_name="m",
        text="t",
        temperature=0.7,
        max_tokens=512,
        llm_call=fake,
    )
    assert captured["temp"] == 0.7
    assert captured["max_tokens"] == 512


def test_text_strategy_handles_none_token_usage():
    def fake(*args):
        return "out", None

    result = text_strategy(
        base_url="x", model_name="m", text="t",
        temperature=0.0, max_tokens=10, llm_call=fake,
    )
    assert result.token_usage is None
