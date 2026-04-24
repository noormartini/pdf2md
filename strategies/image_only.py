import base64
import time
from pathlib import Path
from typing import Callable, Optional

from strategies.result import ConversionResult


def image_strategy(
    base_url: str,
    model_name: str,
    images: list[str],
    temperature: float,
    max_tokens: int,
    page_num: int = 0,
    figures_dir: str = "figures",
    figure_offset: int = 1,
    prompt_variant: str = "default",
    llm_call: Optional[Callable] = None,
) -> ConversionResult:
    """Save page images to disk and return Markdown reference placeholders."""
    Path(figures_dir).mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()
    inline_refs: list[str] = []
    ref_defs: list[str] = []

    for i, img_base64 in enumerate(images):
        n = figure_offset + i
        key = f"fig-{page_num}-{i}"
        filename = f"{key}.png"
        (Path(figures_dir) / filename).write_bytes(base64.b64decode(img_base64))
        inline_refs.append(f"![Figure {n}][{key}]")
        ref_defs.append(f'[{key}]: figures/{filename} "Figure {n}"')

    elapsed_ms = (time.perf_counter() - start) * 1000
    markdown = "\n\n".join(inline_refs)
    return ConversionResult(markdown=markdown, timing_ms=elapsed_ms, token_usage=None, image_refs=ref_defs)
