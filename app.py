import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

import fitz
import pymupdf4llm

from config import Config
from llm.client import call_llm

from extraction.text import extract_pages_from_pdf, extract_monospace_lines
from extraction.image import extract_page_figures
from extraction.language import detect_language, language_name
from postprocess import clean_page, postprocess_markdown
from strategies.text_only import text_strategy
from strategies.image_only import image_strategy
from strategies.hybrid import hybrid_strategy
from strategies.adaptive import analyze_page, adaptive_strategy, render_page_as_base64, PageType


_TOC_HEADER_RE = re.compile(
    # pipe-row format: | Inhaltsverzeichnis | or | Kapitel | …
    r"^\|\s*(?:Contents|Inhaltsverzeichnis|Seite|Kapitel|Chapter|Abschnitt)\s*\|"
    # heading / plain-text format: ## **Inhaltsverzeichnis** or bare "Inhaltsverzeichnis"
    r"|^(?:#{1,3}\s+)?(?:\*{1,2})?(?:Contents|Inhaltsverzeichnis)(?:\*{1,2})?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _build_toc_markdown(doc: fitz.Document) -> str:
    """Format doc.get_toc() as a nested Markdown list with display page labels."""
    toc = doc.get_toc()
    if not toc:
        return ""
    lines = ["## Contents", ""]
    for level, title, page_num in toc:
        label = ""
        if 0 < page_num <= len(doc):
            label = doc[page_num - 1].get_label() or str(page_num)
        else:
            label = str(page_num)
        if level == 1:
            lines.append(f"- **{title}** {label}")
        elif level == 2:
            lines.append(f"  - {title} {label}")
        else:
            lines.append(f"    - {title} {label}")
    return "\n".join(lines)


def _find_toc_page_indices(page_markdowns: list[str]) -> set[int]:
    """Return 0-based indices of TOC pages (first page + any continuation page)."""
    indices: set[int] = set()
    for i, md in enumerate(page_markdowns):
        if md and _TOC_HEADER_RE.search(md):
            indices.add(i)
            # Continuation: next page starts with the TOC title word and has pipe rows
            if i + 1 < len(page_markdowns):
                nxt = page_markdowns[i + 1]
                if (
                    nxt
                    and re.search(r"^(?:Inhaltsverzeichnis|Contents)\b", nxt, re.IGNORECASE | re.MULTILINE)
                    and "|" in nxt
                ):
                    indices.add(i + 1)
    return indices


_FIGURE_CAPTION_RE = re.compile(r"(?:Abbildung|Abb\.|Figure|Fig\.)\s+\d+(?:\.\d+)+", re.IGNORECASE)


def _inject_missing_figure(markdown: str, figure_refs: list[str]) -> str:
    """Insert a figure link before its caption when pymupdf4llm captured the
    caption text but not the image itself.

    This happens for vector-drawn diagrams (see extraction.image, which falls
    back to cropping the page's vector-drawing bounding box) — pymupdf4llm's
    own text extraction has no equivalent, so the caption ends up in the
    Markdown with no image above it. Decorative images with no caption at
    all (e.g. a title-page logo) have no anchor line to insert before, so
    they're placed at the top of the page instead.
    """
    missing = [ref for ref in figure_refs if ref not in markdown]
    if not missing:
        return markdown
    lines = markdown.split("\n")
    for idx, line in enumerate(lines):
        if _FIGURE_CAPTION_RE.search(line):
            lines.insert(idx, f"![Figure 1]({missing[0]})\n")
            return "\n".join(lines)
    lines.insert(0, f"![Figure 1]({missing[0]})\n")
    return "\n".join(lines)


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


def _run_in_pool(indices: list[int], concurrency: int, worker) -> list:
    """Run `worker(i)` for each i in `indices` concurrently and return results
    in input order.

    `pool.map` preserves input order, so the final document join stays correct
    without any indexing dance.  Concurrency is capped at len(indices) to avoid
    spinning up idle threads on small documents.
    """
    workers = max(1, min(concurrency, len(indices)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(worker, indices))


def run(config: Config):
    start_time = time.perf_counter()
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

    page_indices = list(range(num_pages))
    total_tokens = 0
    total_llm_calls = 0

    match (config.strategy):
        case "text":
            # One bulk extraction instead of N per-page calls (each of which
            # would re-scan the whole document for header font sizes).
            page_markdown = _bulk_extract_markdown(config.input, num_pages, figures_dir)

            def _convert(i: int) -> tuple:
                label = page_labels[i]
                raw_text = ""
                with fitz.open(config.input) as worker_doc:
                    raw_text = worker_doc[i].get_text("text")
                    code_lines = extract_monospace_lines(worker_doc[i])
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
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result.markdown, raw_page_text=raw_text, code_lines=code_lines)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert)
            cleaned_pages = [r[0] for r in raw_results]
            total_tokens = sum(r[1] or 0 for r in raw_results)
            total_llm_calls = sum(r[2] for r in raw_results)

        case "image":
            def _convert(i: int) -> tuple:
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
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert)
            cleaned_pages = [r[0] for r in raw_results]
            total_tokens = sum(r[1] or 0 for r in raw_results)
            total_llm_calls = sum(r[2] for r in raw_results)

        case "hybrid":
            pages = extract_pages_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")

            def _convert(i: int) -> tuple:
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
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert)
            cleaned_pages = [r[0] for r in raw_results]
            total_tokens = sum(r[1] or 0 for r in raw_results)
            total_llm_calls = sum(r[2] for r in raw_results)

        case "adaptive":
            # Bulk-extract once for any page that ends up classified as TEXT.
            # Done unconditionally because pymupdf4llm scans the whole doc for
            # header font sizes anyway, so per-page calls are no cheaper than
            # one bulk call.
            page_markdown = _bulk_extract_markdown(config.input, num_pages, figures_dir)

            with fitz.open(config.input) as _toc_doc:
                toc_markdown = _build_toc_markdown(_toc_doc)

            toc_page_indices = _find_toc_page_indices(page_markdown) if toc_markdown else set()
            first_toc_page = min(toc_page_indices) if toc_page_indices else None

            def _convert(i: int) -> tuple:
                label = page_labels[i]

                # TOC pages: use the PDF bookmark outline directly, no LLM.
                # First TOC page gets the full nested list; continuation pages
                # are left empty (the list is complete on the first page).
                if toc_markdown and i in toc_page_indices:
                    content = toc_markdown if i == first_toc_page else ""
                    return f"<!-- Page {label} -->\n\n{content}", 0, 0

                raw_text = ""
                with fitz.open(config.input) as worker_doc:
                    page = worker_doc[i]
                    raw_text = page.get_text("text")
                    analysis = analyze_page(page)
                    strategy_label = (
                        "text" if analysis.page_type == PageType.TEXT
                        else "skip" if analysis.page_type == PageType.EMPTY
                        else "image"
                    )
                    print(f"Page {i+1}/{num_pages} (page {label}) → {strategy_label}...")
                    page_image = render_page_as_base64(page)
                    is_text_page = analysis.page_type == PageType.TEXT
                    # TEXT pages skip the vision LLM, so a figure caption with
                    # no matching raster image (a vector-drawn diagram) would
                    # otherwise be silently dropped — check for that cheaply
                    # instead of always paying for figure extraction. Also
                    # rescue vector-drawn decorative images with no caption at
                    # all (e.g. a title-page logo) when pymupdf4llm's own
                    # extraction found no image on the page.
                    page_pre_markdown = page_markdown[i] if i < len(page_markdown) else ""
                    has_pre_extracted_image = "![" in page_pre_markdown
                    needs_figure_check = is_text_page and (
                        bool(_FIGURE_CAPTION_RE.search(raw_text))
                        or (not has_pre_extracted_image and analysis.vector_path_count >= 10)
                    )
                    figure_refs = (
                        extract_page_figures(page, worker_doc, i, figures_dir)
                        if (not is_text_page or needs_figure_check)
                        else None
                    )
                    code_lines = extract_monospace_lines(page) if is_text_page else None
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
                result_markdown = result.markdown
                if is_text_page and figure_refs:
                    result_markdown = _inject_missing_figure(result_markdown, figure_refs)
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result_markdown, raw_page_text=raw_text, code_lines=code_lines)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert)
            cleaned_pages = [r[0] for r in raw_results]
            total_tokens = sum(r[1] or 0 for r in raw_results)
            total_llm_calls = sum(r[2] for r in raw_results)

        case _:
            raise ValueError(f"Unknown strategy: {config.strategy}")

    markdown = "\n\n---\n\n".join(cleaned_pages)
    markdown = postprocess_markdown(markdown)

    print("Saving Markdown output...")
    os.makedirs(os.path.dirname(os.path.abspath(config.output)), exist_ok=True)
    with open(config.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    elapsed_s = time.perf_counter() - start_time
    avg_per_page = elapsed_s / num_pages if num_pages > 0 else 0

    print(f"Done! Output saved as '{config.output}'.")
    print(f"Conversion time: {elapsed_s:.1f}s total — {num_pages} pages — {avg_per_page:.1f}s/page avg")
    if total_llm_calls > 0:
        avg = total_tokens // total_llm_calls
        print(f"Token usage: {total_tokens:,} tokens ({total_llm_calls} LLM calls, avg {avg:,}/call)")
    else:
        print("Token usage: 0 (no LLM calls — text strategy)")
