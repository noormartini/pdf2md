"""Shape tests for llm/prompts.py — every variant must be well-formed."""

import pytest

from llm.prompts import PROMPTS


def test_default_variant_exists():
    assert "default" in PROMPTS


@pytest.mark.parametrize("variant", list(PROMPTS.keys()))
def test_variant_has_system_and_user(variant):
    assert "system" in PROMPTS[variant]
    assert "user" in PROMPTS[variant]


@pytest.mark.parametrize("variant", list(PROMPTS.keys()))
def test_variant_user_has_text_placeholder(variant):
    """The user template must accept {text} so .format(text=...) works."""
    assert "{text}" in PROMPTS[variant]["user"]


@pytest.mark.parametrize("variant", list(PROMPTS.keys()))
def test_variant_user_format_substitutes(variant):
    rendered = PROMPTS[variant]["user"].format(text="SAMPLE")
    assert "SAMPLE" in rendered
    assert "{text}" not in rendered


@pytest.mark.parametrize("variant", list(PROMPTS.keys()))
def test_variant_system_is_nonempty_string(variant):
    sys_prompt = PROMPTS[variant]["system"]
    assert isinstance(sys_prompt, str)
    assert sys_prompt.strip()
