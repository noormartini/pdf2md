import os
import time
from typing import Callable, Optional

import pymupdf4llm

from llm.prompts import PROMPTS, with_language_hint
from strategies.result import ConversionResult


def text_strategy(
    base_url: str,
    model_name: str,
    pdf_path: str,
    page_num: int,
    temperature: float,
    max_tokens: int,
    figures_dir: str = "figures",
    prompt_variant: str = "default",
    language: str = "en",
    llm_call: Optional[Callable] = None,
    pre_extracted_markdown: Optional[str] = None,
) -> ConversionResult:
    """Convert a PDF page to Markdown using pymupdf4llm, then optionally clean
    up the output with an LLM (required for LaTeX math conversion).

    When `llm_call` is provided the raw pymupdf4llm output is passed through
    the LLM using `prompt_variant` so that any mathematical symbols or formulas
    are converted to LaTeX notation.  Without `llm_call` the raw Markdown is
    returned as-is (fast path, no math conversion).

    When `pre_extracted_markdown` is provided, the per-page `pymupdf4llm`
    call is skipped and the supplied Markdown is used directly.  Callers
    that convert many pages from the same document should bulk-extract once
    (`pymupdf4llm.to_markdown(..., pages=range(N))`) and pass each page's
    chunk in here — this avoids the all-pages font-histogram pass that
    `pymupdf4llm` runs on every call.
    """
    start = time.perf_counter()
    if pre_extracted_markdown is not None:
        raw_markdown = pre_extracted_markdown
    else:
        chunks = pymupdf4llm.to_markdown(
            pdf_path,
            pages=[page_num],
            page_chunks=True,
            write_images=True,
            image_path=figures_dir,
            image_size_limit=0,
        )
        raw_markdown = chunks[0]["text"] if chunks else ""

    # Fix image paths to be relative to the output file, not cwd.
    cwd_rel = os.path.relpath(figures_dir).replace("\\", "/") + "/"
    raw_markdown = raw_markdown.replace(f"({cwd_rel}", "(figures/")
    abs_prefix = os.path.abspath(figures_dir).replace("\\", "/") + "/"
    raw_markdown = raw_markdown.replace(f"({abs_prefix}", "(figures/")

    if llm_call is None:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return ConversionResult(markdown=raw_markdown, timing_ms=elapsed_ms, token_usage=0, llm_calls=0)

    prompt = PROMPTS.get(prompt_variant, PROMPTS["text"])
    messages = [
        {"role": "system", "content": with_language_hint(prompt["system"], language)},
        {"role": "user", "content": raw_markdown},
    ]
    response, token_usage = llm_call(base_url, model_name, messages, temperature, max_tokens)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return ConversionResult(markdown=response, timing_ms=elapsed_ms, token_usage=token_usage, llm_calls=1)
