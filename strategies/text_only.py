import time
from typing import Callable

from llm.prompts import PROMPTS
from llm.client import call_llm
from strategies.result import ConversionResult


def text_strategy(
    base_url: str,
    model_name: str,
    text: str,
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
    llm_call: Callable = call_llm,
) -> ConversionResult:
    """Convert PDF-extracted text to Markdown via an LLM (text-only input).

    `llm_call` is injectable so tests can swap in a fake without touching
    the network.
    """
    messages = [
        {"role": "system", "content": PROMPTS[prompt_variant]["system"]},
        {"role": "user", "content": PROMPTS[prompt_variant]["user"].format(text=text)},
    ]

    start = time.perf_counter()
    content, token_usage = llm_call(base_url, model_name, messages, temperature, max_tokens)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return ConversionResult(
        markdown=content,
        timing_ms=elapsed_ms,
        token_usage=token_usage,
    )
