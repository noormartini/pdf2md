"""
Adaptive per-page strategy: classifies each PDF page by content type
and routes to the most appropriate extraction method.

This is the core thesis contribution — rather than applying a single fixed
strategy to the entire document, each page is analysed individually and the
best strategy is selected based on detected content type.
"""

import base64
import re
from dataclasses import dataclass
from enum import Enum

import fitz

from typing import Callable

from strategies.text_only import text_strategy as _text_strategy
from strategies.image_only import image_strategy as _image_strategy
from strategies.result import ConversionResult


class PageType(Enum):
    TEXT = "text"       # Pure text   → text_strategy with "text" prompt
    IMAGE = "image"     # Image-heavy → image_strategy with "diagram" prompt
    FORMULA = "formula" # Math-heavy  → image_strategy with "formula" prompt
    MIXED = "mixed"     # Text+visual → image_strategy with "default" prompt
    EMPTY = "empty"     # Mostly empty → skip


@dataclass
class PageAnalysis:
    """Result of classifying a single PDF page."""
    page_type: PageType
    has_images: bool
    has_formulas: bool
    image_count: int
    text_length: int
    vector_path_count: int
    confidence: float  # 0.0–1.0


# ---------------------------------------------------------------------------
# Classification thresholds
# ---------------------------------------------------------------------------
_IMAGE_THRESHOLD = 0         # Any embedded image triggers vision mode
_VECTOR_PATH_THRESHOLD = 30  # Short vector paths → likely rendered formulas
_MIN_TEXT_CHARACTERS = 50    # Pages with less text than this → not "text" type


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

    if text_length < 10 and not has_images and vector_path_count < 5:
        page_type, confidence = PageType.EMPTY, 0.9
    elif has_formulas and text_length < _MIN_TEXT_CHARACTERS:
        page_type, confidence = PageType.FORMULA, 0.85
    elif has_images and image_count > 3:
        page_type, confidence = PageType.IMAGE, 0.9
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
        image_count=image_count,
        text_length=text_length,
        vector_path_count=vector_path_count,
        confidence=confidence,
    )


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
    text_call: Callable = _text_strategy,
    image_call: Callable = _image_strategy,
) -> ConversionResult:
    """
    Select and run the best extraction strategy for the given page type.

    Args:
        base_url:    LM Studio server URL.
        model_name:  Model name loaded in LM Studio.
        pdf_path:    Path to the source PDF file.
        page_num:    0-based page index.
        page_image:  Base64-encoded PNG of the rendered page.
        page_type:   Classified type from analyze_page().
        temperature: LLM temperature.
        max_tokens:  Maximum response tokens.
        text_call:   Injectable text strategy (default: text_strategy).
        image_call:  Injectable image strategy (default: image_strategy).

    Returns:
        ConversionResult for this page.
    """
    if page_type == PageType.EMPTY:
        return ConversionResult(markdown="*[Empty page — skipped]*", timing_ms=0.0, token_usage=None)

    if page_type == PageType.TEXT:
        return text_call(
            base_url=base_url,
            model_name=model_name,
            pdf_path=pdf_path,
            page_num=page_num,
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_variant="text",
        )

    if page_type == PageType.FORMULA:
        return image_call(
            base_url=base_url,
            model_name=model_name,
            images=[page_image],
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_variant="formula",
        )

    if page_type == PageType.IMAGE:
        return image_call(
            base_url=base_url,
            model_name=model_name,
            images=[page_image],
            temperature=temperature,
            max_tokens=max_tokens,
            prompt_variant="diagram",
        )

    # MIXED — image with default prompt (best general coverage)
    return image_call(
        base_url=base_url,
        model_name=model_name,
        images=[page_image],
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_variant="default",
    )
