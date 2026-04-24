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
    figures_dir: str = "figures",
    prompt_variant: str = "default",
    llm_call: Optional[Callable] = None,
) -> ConversionResult:
    """Convert a PDF page directly to Markdown using pymupdf4llm (no LLM call).

    Inline images on text pages are saved to figures_dir instead of being omitted.
    """
    start = time.perf_counter()
    chunks = pymupdf4llm.to_markdown(
        pdf_path,
        pages=[page_num],
        page_chunks=True,
        write_images=True,
        image_path=figures_dir,
        image_size_limit=0,
    )
    markdown = chunks[0]["text"] if chunks else ""
    # pymupdf4llm uses a cwd-relative path in markdown image references;
    # replace it with "figures/" so links are relative to the output file
    import os as _os
    cwd_rel = _os.path.relpath(figures_dir).replace("\\", "/") + "/"
    markdown = markdown.replace(f"({cwd_rel}", "(figures/")
    # also handle absolute paths (e.g. when tmp dir is used)
    abs_prefix = _os.path.abspath(figures_dir).replace("\\", "/") + "/"
    markdown = markdown.replace(f"({abs_prefix}", "(figures/")
    elapsed_ms = (time.perf_counter() - start) * 1000
    return ConversionResult(markdown=markdown, timing_ms=elapsed_ms, token_usage=None)
