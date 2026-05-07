import time
from typing import Callable

from llm.prompts import PROMPTS
from llm.client import call_llm
from strategies.result import ConversionResult


def image_strategy(
    base_url: str,
    model_name: str,
    images: list[str],
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
    figure_refs: list[str] | None = None,
    llm_call: Callable = call_llm,
) -> ConversionResult:
    """Convert page images to Markdown via a vision LLM (image-only input).

    `llm_call` is injectable so tests can swap in a fake without touching
    the network.
    `figure_refs`: optional list of already-saved figure paths (e.g.
    ``["figures/page_001_fig_001.png"]``); when present, a text block is
    prepended instructing the LLM to include those links in its output.
    """
    content: list[dict[str, object]] = []

    if figure_refs:
        ref_list = "\n".join(
            f"- ![Figure {i + 1}]({ref})" for i, ref in enumerate(figure_refs)
        )
        content.append({
            "type": "text",
            "text": (
                "The following figures have been extracted from this page and saved as files. "
                "Include them as Markdown image links at the appropriate locations in your output:\n"
                + ref_list
            ),
        })

    for img_base64 in images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{img_base64}",
            },
        })

    messages = [
        {"role": "system", "content": PROMPTS[prompt_variant]["system"]},
        {"role": "user", "content": content},
    ]

    start = time.perf_counter()
    response, token_usage = llm_call(base_url, model_name, messages, temperature, max_tokens)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return ConversionResult(
        markdown=response,
        timing_ms=elapsed_ms,
        token_usage=token_usage,
    )
