import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import fitz
import pymupdf4llm

from config import Config
from llm.client import call_llm

from extraction.text import extract_pages_from_pdf
from extraction.image import extract_page_figures
from extraction.language import detect_language, language_name
from postprocess import clean_page, postprocess_markdown
from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy
from strategies.adaptive import analyze_page, adaptive_strategy, render_page_as_base64, PageType


def _page_label(doc: fitz.Document, index: int) -> str:
    """Return the printed page label (e.g. 'v', '3') for a 0-based page index."""
    label = doc[index].get_label()
    return label if label else str(index + 1)


def _bulk_extract_markdown(pdf_path: str, num_pages: int, figures_dir: str) -> list[str]:
    """Run pymupdf4llm.to_markdown once for the whole page range.

    `pymupdf4llm.to_markdown` runs an all-pages font-histogram pass
    (`IdentifyHeaders`) on every call regardless of the `pages=` filter, so
    calling it once per page is O(N²) text extraction.  We do it once here
    and the per-page workers index by page number.
    """
    chunks = pymupdf4llm.to_markdown(
        pdf_path,
        pages=list(range(num_pages)),
        page_chunks=True,
        write_images=True,
        image_path=figures_dir,
        image_size_limit=0,
    )
    # `to_markdown` returns chunks in the same order as `pages=`.
    return [chunk.get("text", "") for chunk in chunks]


def _run_in_pool(num_pages: int, concurrency: int, worker) -> list[str]:
    """Run `worker(i)` for i in [0, num_pages) concurrently and return results
    in input order.

    `pool.map` preserves input order, so the final document join stays correct
    without any indexing dance.  Concurrency is capped at `num_pages` to avoid
    spinning up idle threads on small documents.
    """
    workers = max(1, min(concurrency, num_pages))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(worker, range(num_pages)))


def run(config: Config):
    figures_dir = os.path.join(os.path.dirname(os.path.abspath(config.output)), "figures")
    llm_call = partial(call_llm, timeout=config.llm_timeout)

    # Detect document language from the first page's text
    with fitz.open(config.input) as _doc:
        sample_text = _doc[0].get_text("text") if len(_doc) > 0 else ""
    language = detect_language(sample_text)
    print(f"Detected language: {language_name(language)} ({language})")

    # Use a temporary doc just to get the page count and labels; per-page
    # workers open their own fitz.Document because Document objects are not
    # thread-safe.
    with fitz.open(config.input) as doc:
        num_pages = min(len(doc), config.max_pages)
        if num_pages == 0:
            raise ValueError("No pages could be read from the PDF.")
        page_labels = [_page_label(doc, i) for i in range(num_pages)]

    match (config.strategy):
        case "text":
            # One bulk extraction instead of N per-page calls (each of which
            # would re-scan the whole document for header font sizes).
            page_markdown = _bulk_extract_markdown(config.input, num_pages, figures_dir)

            def _convert(i: int) -> str:
                label = page_labels[i]
                print(f"Converting page {i+1}/{num_pages} (page {label}) to Markdown...")
                result = text_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    pdf_path=config.input,
                    page_num=i,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    figures_dir=figures_dir,
                    pre_extracted_markdown=page_markdown[i] if i < len(page_markdown) else "",
                )
                return f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"

            cleaned_pages = _run_in_pool(num_pages, config.concurrency, _convert)

        case "image":
            def _convert(i: int) -> str:
                label = page_labels[i]
                with fitz.open(config.input) as worker_doc:
                    page = worker_doc[i]
                    page_image = render_page_as_base64(page)
                    figure_refs = extract_page_figures(page, worker_doc, i, figures_dir)
                print(f"Sending page {i+1}/{num_pages} (page {label}) to LM Studio...")
                result = image_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                    figure_refs=figure_refs or None,
                    language=language,
                    llm_call=llm_call,
                )
                return f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"

            cleaned_pages = _run_in_pool(num_pages, config.concurrency, _convert)

        case "hybrid":
            pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")

            def _convert(i: int) -> str:
                label = page_labels[i]
                with fitz.open(config.input) as worker_doc:
                    page = worker_doc[i]
                    page_image = render_page_as_base64(page)
                    figure_refs = extract_page_figures(page, worker_doc, i, figures_dir)
                page_text = pages[i] if i < len(pages) else ""
                print(f"Sending page {i+1}/{num_pages} (page {label}) to LM Studio...")
                result = hybrid_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    text=page_text,
                    images=[page_image],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    prompt_variant="default",
                    figure_refs=figure_refs or None,
                    language=language,
                    llm_call=llm_call,
                )
                return f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"

            cleaned_pages = _run_in_pool(num_pages, config.concurrency, _convert)

        case "adaptive":
            # Bulk-extract once for any page that ends up classified as TEXT.
            # Done unconditionally because pymupdf4llm scans the whole doc for
            # header font sizes anyway, so per-page calls are no cheaper than
            # one bulk call.
            page_markdown = _bulk_extract_markdown(config.input, num_pages, figures_dir)

            def _convert(i: int) -> str:
                label = page_labels[i]
                with fitz.open(config.input) as worker_doc:
                    page = worker_doc[i]
                    analysis = analyze_page(page)
                    print(
                        f"Page {i+1}/{num_pages} (page {label}) → "
                        f"{analysis.page_type.value} "
                        f"(conf={analysis.confidence:.2f})..."
                    )
                    page_image = render_page_as_base64(page)
                    figure_refs = (
                        extract_page_figures(page, worker_doc, i, figures_dir)
                        if analysis.page_type != PageType.TEXT
                        else None
                    )
                result = adaptive_strategy(
                    base_url=config.base_url,
                    model_name=config.model,
                    pdf_path=config.input,
                    page_num=i,
                    page_image=page_image,
                    page_type=analysis.page_type,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    figures_dir=figures_dir,
                    figure_refs=figure_refs,
                    language=language,
                    pre_extracted_markdown=page_markdown[i] if i < len(page_markdown) else None,
                    image_call=partial(image_strategy, llm_call=llm_call),
                )
                return f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"

            cleaned_pages = _run_in_pool(num_pages, config.concurrency, _convert)

        case _:
            raise ValueError(f"Unknown strategy: {config.strategy}")

    markdown = "\n\n---\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    os.makedirs(os.path.dirname(os.path.abspath(config.output)), exist_ok=True)
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Done! Output saved as '{config.output}'.")
