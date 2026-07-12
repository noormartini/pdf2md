"""
Adaptive per-page strategy: classifies each PDF page by content type
and routes to the most appropriate extraction method.

This is the core thesis contribution — rather than applying a single fixed
strategy to the entire document, each page is analysed individually and the
best strategy is selected based on detected content type.
"""

import base64
import os
import re
from dataclasses import dataclass
from enum import Enum

import fitz

from typing import Callable

from strategies.text_only import text_strategy as _text_strategy
from strategies.image_only import image_strategy as _image_strategy
from strategies.result import ConversionResult


class PageType(Enum):
    TEXT = "text"       # Pure text    → text_strategy with "text" prompt
    IMAGE = "image"     # Image-heavy  → image_strategy with "diagram" prompt
    FORMULA = "formula" # Math-heavy   → image_strategy with "formula" prompt
    TABLE = "table"     # Table-heavy  → image_strategy with "table" prompt
    MIXED = "mixed"     # Text+visual  → image_strategy with "default" prompt
    EMPTY = "empty"     # Mostly empty → skip


@dataclass
class PageAnalysis:
    """Result of classifying a single PDF page."""
    page_type: PageType
    has_images: bool
    has_formulas: bool
    has_tables: bool
    image_count: int
    table_count: int
    text_length: int
    vector_path_count: int
    confidence: float  # 0.0–1.0


# ---------------------------------------------------------------------------
# Classification thresholds
# ---------------------------------------------------------------------------
_IMAGE_THRESHOLD = 0         # Any embedded image triggers vision mode
_VECTOR_PATH_THRESHOLD = 30  # Short vector paths → likely rendered formulas
_MIN_TEXT_CHARACTERS = 50    # Pages with less text than this → not "text" type

# Generic Markdown pipe-table separator row, e.g. "|---|---|---|" — used to
# check whether pymupdf4llm's pre-extracted text actually contains a table.
_TABLE_SEPARATOR_LINE_RE = re.compile(r"^\|[\s\-:]+(?:\|[\s\-:]+)+\|?\s*$", re.MULTILINE)


def _detect_formulas(page: fitz.Page, drawings: list) -> bool:
    """Return True if the page likely contains mathematical formulas."""
    short_paths = [
        d for d in drawings
        if d.get("rect") and (d["rect"].width < 20 or d["rect"].height < 20)
    ]
    if len(short_paths) > _VECTOR_PATH_THRESHOLD:
        return True

    text = page.get_text("text")

    if re.search(r'[∑∏∫∂∇√∞≈≠≤≥±×÷∈∉⊂⊃∪∩∧∨¬∀∃∅]', text):
        return True

    if re.search(r'\\[a-z]+|_\{[^}]+\}|\^\{[^}]+\}', text):
        return True

    return False


def analyze_page(page: fitz.Page) -> PageAnalysis:
    """
    Analyse a PDF page and return its classified type with confidence.

    Args:
        page: A PyMuPDF Page object.

    Returns:
        PageAnalysis with type, supporting metrics, and confidence score.
    """
    image_count = len(page.get_images(full=False))
    has_images = image_count > _IMAGE_THRESHOLD

    drawings = page.get_drawings()
    vector_path_count = len(drawings)

    has_formulas = _detect_formulas(page, drawings)
    text_length = len(page.get_text("text").strip())

    finder = page.find_tables()
    table_count = len(finder.tables)
    has_tables = table_count > 0

    if text_length < 10 and not has_images and vector_path_count < 5:
        page_type, confidence = PageType.EMPTY, 0.9
    elif has_formulas and text_length < _MIN_TEXT_CHARACTERS:
        page_type, confidence = PageType.FORMULA, 0.85
    elif has_images and image_count > 3:
        page_type, confidence = PageType.IMAGE, 0.9
    elif has_tables:
        page_type, confidence = PageType.TABLE, 0.85
    elif has_images or has_formulas:
        page_type, confidence = PageType.MIXED, 0.75
    elif text_length >= _MIN_TEXT_CHARACTERS:
        page_type, confidence = PageType.TEXT, 0.95
    else:
        page_type, confidence = PageType.MIXED, 0.5

    return PageAnalysis(
        page_type=page_type,
        has_images=has_images,
        has_formulas=has_formulas,
        has_tables=has_tables,
        image_count=image_count,
        table_count=table_count,
        text_length=text_length,
        vector_path_count=vector_path_count,
        confidence=confidence,
    )


_IMAGE_REF_RE = re.compile(r'!\[.*?\]\(([^)]+)\)')


def _normalize_image_paths(markdown: str, figures_dir: str) -> list[str]:
    """Extract image paths from Markdown and normalise them to `figures/<name>`.

    pymupdf4llm's own bulk extraction writes absolute paths, unlike the
    `figures/<name>` links used everywhere else in the pipeline.
    """
    cwd_rel = os.path.relpath(figures_dir).replace("\\", "/") + "/"
    abs_prefix = os.path.abspath(figures_dir).replace("\\", "/") + "/"
    refs = []
    for path in _IMAGE_REF_RE.findall(markdown):
        name = path
        if name.startswith(cwd_rel):
            name = name[len(cwd_rel):]
        elif name.startswith(abs_prefix):
            name = name[len(abs_prefix):]
        refs.append(name if name.startswith("figures/") else f"figures/{name}")
    return refs


def _drop_rendered_formula_images(refs: list[str], figures_dir: str, min_height: float = 50) -> list[str]:
    """Drop images that are pymupdf4llm's own raster render of a formula.

    When pymupdf4llm can't parse a complex equation as text, it falls back
    to cropping that region as a small image (e.g. 638x37px for a one-line
    equation) instead. Carrying that over as a figure_ref would tell the
    vision model to embed it as-is, duplicating the formula it already
    converts correctly to LaTeX from reading the page image. A real
    diagram/logo is much taller than a single equation line, so height is a
    reliable way to tell the two apart.
    """
    kept = []
    for ref in refs:
        path = os.path.join(figures_dir, os.path.basename(ref))
        try:
            height = fitz.Pixmap(path).height
        except Exception:
            kept.append(ref)
            continue
        if height >= min_height:
            kept.append(ref)
    return kept


def render_page_as_base64(page: fitz.Page, dpi: int = 150) -> str:
    """Render a PDF page to a base64-encoded PNG string."""
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pixmap = page.get_pixmap(matrix=matrix)
    return base64.b64encode(pixmap.tobytes("png")).decode("utf-8")


def adaptive_strategy(
    base_url: str,
    model_name: str,
    pdf_path: str,
    page_num: int,
    page_image: str,
    page_type: PageType,
    temperature: float,
    max_tokens: int,
    figures_dir: str = "figures",
    figure_refs: list[str] | None = None,
    language: str = "en",
    pre_extracted_markdown: str | None = None,
    text_call: Callable = _text_strategy,
    image_call: Callable = _image_strategy,
) -> ConversionResult:
    """
    Select and run the best extraction strategy for the given page type.

    Args:
        base_url:     LM Studio server URL.
        model_name:   Model name loaded in LM Studio.
        pdf_path:     Path to the source PDF file.
        page_num:     0-based page index.
        page_image:   Base64-encoded PNG of the rendered page.
        page_type:    Classified type from analyze_page().
        temperature:  LLM temperature.
        max_tokens:   Maximum response tokens.
        figures_dir:  Directory to save inline images from text pages.
        figure_refs:  Pre-extracted figure paths to include as Markdown links
                      in the LLM output for non-text pages.
        pre_extracted_markdown: Optional pre-extracted pymupdf4llm output for
                      this page (used only when page_type == TEXT).  Lets
                      callers bulk-extract once instead of paying the all-pages
                      font-histogram pass on every per-page call.
        text_call:    Injectable text strategy (default: text_strategy).
        image_call:   Injectable image strategy (default: image_strategy).

    Returns:
        ConversionResult for this page.
    """
    if page_type == PageType.EMPTY:
        return ConversionResult(markdown="*[Empty page — skipped]*", timing_ms=0.0, token_usage=0, llm_calls=0)

    if page_type == PageType.TEXT:
        # If the pre-extracted markdown contains image links, the page has
        # embedded raster formula images that page.get_images() missed.
        # Route these pages to the vision LLM so formulas become LaTeX.
        # Exception: TOC/list pages with decorative images must stay on the
        # text path so the postprocessing TOC converter can handle them.
        _is_toc_page = bool(
            pre_extracted_markdown
            and re.search(
                r"^\|\s*(?:Contents|Inhaltsverzeichnis|Seite|Kapitel|Chapter)\s*\|",
                pre_extracted_markdown,
                re.IGNORECASE | re.MULTILINE,
            )
        )
        def _text_fallback() -> ConversionResult:
            return text_call(
                base_url=base_url,
                model_name=model_name,
                pdf_path=pdf_path,
                page_num=page_num,
                temperature=temperature,
                max_tokens=max_tokens,
                figures_dir=figures_dir,
                prompt_variant="text",
                language=language,
                llm_call=None,
                pre_extracted_markdown=pre_extracted_markdown,
            )

        if pre_extracted_markdown and not _is_toc_page and re.search(r'!\[.*?\]\(', pre_extracted_markdown):
            # Carry over the image(s) pymupdf4llm already found and saved —
            # otherwise the vision LLM has no way to know they exist and the
            # image is silently dropped from the output. Excludes pymupdf4llm's
            # own rendered-formula fallback images, which would otherwise
            # duplicate the LaTeX the vision model converts them to.
            carried_over = _drop_rendered_formula_images(
                _normalize_image_paths(pre_extracted_markdown, figures_dir), figures_dir
            )
            figure_refs = list(figure_refs or []) + carried_over
            result = image_call(
                base_url=base_url,
                model_name=model_name,
                images=[page_image],
                temperature=temperature,
                max_tokens=max_tokens,
                prompt_variant="default",
                figure_refs=figure_refs,
                language=language,
            )
            # This page was already well-extracted as text — the vision
            # detour is only meant to upgrade an embedded formula image to
            # LaTeX, not replace the whole page. If the model fails outright
            # (empty/truncated response), falling back to the known-good
            # pymupdf4llm text is far safer than losing the page's content.
            if len(result.markdown.strip()) < 0.3 * len(pre_extracted_markdown.strip()):
                return _text_fallback()
            return result
        else:
            # TEXT pages have no images and no formulas (per analyze_page), so
            # pymupdf4llm's output is the answer — skip the LLM entirely to save
            # the 3–10 s round-trip per page.
            return _text_fallback()

    if page_type == PageType.FORMULA:
        return image_call(
            base_url=base_url,
            model_name=model_name,
            images=[page_image],
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_variant="formula",
            figure_refs=figure_refs,
            language=language,
        )

    if page_type == PageType.IMAGE:
        return image_call(
            base_url=base_url,
            model_name=model_name,
            images=[page_image],
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_variant="diagram",
            figure_refs=figure_refs,
            language=language,
        )

    if page_type == PageType.TABLE:
        # pymupdf4llm's own table detection is reliable for text-layer tables
        # and — unlike the vision LLM — never drops the surrounding heading
        # or paragraph text around the table. Prefer it whenever it actually
        # produced a table; fall back to the vision LLM (e.g. for scanned or
        # image-based tables the text layer can't see) when it didn't.
        if pre_extracted_markdown and _TABLE_SEPARATOR_LINE_RE.search(pre_extracted_markdown):
            return text_call(
                base_url=base_url,
                model_name=model_name,
                pdf_path=pdf_path,
                page_num=page_num,
                temperature=temperature,
                max_tokens=max_tokens,
                figures_dir=figures_dir,
                prompt_variant="table",
                language=language,
                llm_call=None,
                pre_extracted_markdown=pre_extracted_markdown,
            )
        return image_call(
            base_url=base_url,
            model_name=model_name,
            images=[page_image],
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_variant="table",
            figure_refs=figure_refs,
            language=language,
        )

    # MIXED — image with default prompt (best general coverage)
    result = image_call(
        base_url=base_url,
        model_name=model_name,
        images=[page_image],
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_variant="default",
        figure_refs=figure_refs,
        language=language,
    )
    # A vision response that's suspiciously short compared to the page's own
    # extractable text usually means the model got cut off partway through
    # (e.g. hit max_tokens) rather than the page genuinely having little
    # text. Falling back to the known-good text preserves the prose, even
    # though the figure link isn't re-embedded in this fallback path.
    if pre_extracted_markdown and len(result.markdown.strip()) < 0.3 * len(pre_extracted_markdown.strip()):
        fallback = text_call(
            base_url=base_url,
            model_name=model_name,
            pdf_path=pdf_path,
            page_num=page_num,
            temperature=temperature,
            max_tokens=max_tokens,
            figures_dir=figures_dir,
            prompt_variant="text",
            language=language,
            llm_call=None,
            pre_extracted_markdown=pre_extracted_markdown,
        )
        if figure_refs:
            refs_md = "\n".join(f"![Figure {i + 1}]({ref})" for i, ref in enumerate(figure_refs))
            fallback.markdown = fallback.markdown.rstrip() + "\n\n" + refs_md
        return fallback
    return result
