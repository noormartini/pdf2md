import time
from typing import Callable, Optional

import pymupdf4llm

from strategies.result import ConversionResult


def text_strategy(
    base_url: str,
    model_name: str,
    pdf_path: str,
    page_num: int,
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
    llm_call: Optional[Callable] = None,
) -> ConversionResult:
    """Convert a PDF page directly to Markdown using pymupdf4llm (no LLM call)."""
    start = time.perf_counter()
    chunks = pymupdf4llm.to_markdown(pdf_path, pages=[page_num], page_chunks=True)
    markdown = chunks[0]["text"] if chunks else ""
    elapsed_ms = (time.perf_counter() - start) * 1000
    return ConversionResult(markdown=markdown, timing_ms=elapsed_ms, token_usage=None)
