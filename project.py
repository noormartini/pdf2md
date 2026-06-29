"""
PDF2MD — single-file version of the complete project.

Usage:
    python3 project.py -i input.pdf -o output.md -s adaptive

This file is a self-contained consolidation of every module in the project.
It is functionally identical to running `python3 main.py` with the same
arguments.  The multi-file layout is preserved for the main codebase;
this file exists so the whole system can be read and run as a single unit.

Dependencies (install via pip):
    pymupdf pymupdf4llm requests langdetect
"""

# ===========================================================================
# Standard-library imports
# ===========================================================================

import argparse
import base64
import os
import re
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Callable, Optional

# ===========================================================================
# Third-party imports
# ===========================================================================

import fitz               # PyMuPDF
import pymupdf4llm
import requests
from langdetect import detect, LangDetectException


# ===========================================================================
# Configuration  (config.py)
# ===========================================================================

ADAPTIVE_IMAGE_THRESHOLD: int = 0
ADAPTIVE_VECTOR_PATH_THRESHOLD: int = 30
ADAPTIVE_MIN_TEXT_CHARACTERS: int = 50
ADAPTIVE_RENDER_DPI: int = 150

DEFAULT_MODEL: str = "qwen2.5-vl-7b-instruct-abliterated"
DEFAULT_BASE_URL: str = "http://127.0.0.1:1234/v1"
DEFAULT_LLM_TIMEOUT: int = 300
DEFAULT_CONCURRENCY: int = 4


@dataclass
class Config:
    input: str
    output: str
    base_url: str
    model: str
    max_pages: int
    strategy: str = "text"
    temperature: float = 0.2
    max_tokens: int = 4096
    llm_timeout: int = DEFAULT_LLM_TIMEOUT
    concurrency: int = DEFAULT_CONCURRENCY


# ===========================================================================
# Conversion result  (strategies/result.py)
# ===========================================================================

@dataclass
class ConversionResult:
    """Result of converting one PDF page via a conversion strategy."""
    markdown: str
    timing_ms: float
    token_usage: Optional[int]  # None means LM Studio did not report usage
    llm_calls: int = 0          # 0 when the LLM was skipped entirely


# ===========================================================================
# Language detection  (extraction/language.py)
# ===========================================================================

_LANGUAGE_NAMES: dict[str, str] = {
    "de": "German",
    "en": "English",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "nl": "Dutch",
}


def detect_language(text: str) -> str:
    """Detect the primary language of the text.

    Returns an ISO 639-1 code (e.g. 'de', 'en').
    Defaults to 'en' if detection fails or text is too short.
    """
    if len(text.strip()) < 20:
        return "en"
    try:
        return detect(text)
    except LangDetectException:
        return "en"


def language_name(code: str) -> str:
    """Return a human-readable name for an ISO 639-1 language code."""
    return _LANGUAGE_NAMES.get(code, code.upper())


# ===========================================================================
# LLM client  (llm/client.py)
# ===========================================================================

def call_llm(
    base_url: str,
    model_name: str,
    messages: list[dict],
    temperature: float,
    max_tokens: int,
    timeout: int = 300,
) -> tuple[str, Optional[int]]:
    """Send messages to the LLM and return (content, total_token_usage).

    `total_token_usage` is `usage.total_tokens` from the response if the
    server returns it (LM Studio / OpenAI-compatible APIs do), else None.
    """
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    response = requests.post(f"{base_url}/chat/completions", json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    token_usage = data.get("usage", {}).get("total_tokens")
    return content, token_usage


# ===========================================================================
# LLM prompts  (llm/prompts.py)
# ===========================================================================

def with_language_hint(system_prompt: str, language: str) -> str:
    """Append a language-preservation note to a system prompt for non-English docs."""
    if language.startswith("en"):
        return system_prompt
    lang = _LANGUAGE_NAMES.get(language, language.upper())
    note = (
        f"\n\n**Language:** This document is written in {lang}. "
        "Preserve all text in the original language — do not translate."
    )
    return system_prompt + note


PROMPTS = {
    # ------------------------------------------------------------------
    # default — general-purpose prompt used by text, image, and hybrid
    # strategies when no specific variant is specified.
    # ------------------------------------------------------------------
    "default": {
        "system": """\
You are a PDF-to-Markdown conversion specialist. Convert the following PDF-extracted text into clean, well-structured Markdown.

## Rules

**Content Integrity:**
- Preserve the original meaning exactly - do not add, remove, or invent content.
- Do not include any commentary, explanations, or meta-text in your output.

**Structure & Formatting:**
- Fix broken line breaks within paragraphs (common PDF artifact).
- Preserve meaningful paragraph breaks.
- Detect headings and format as Markdown headings (# for title, ## for sections, ### for subsections).
- If a heading includes a section number (e.g. "1.1 Motivation" or "2.3.4 Title"), preserve the number exactly as it appears — do not drop it.
- Only use Markdown headings for text that marks a structural section — do NOT convert bold or italic text to a heading.
- Format lists (bulleted or numbered) as proper Markdown lists.
- Wrap source code in fenced code blocks with language identifier if detectable.

**Figures & Captions:**
- When you include an image link, look for a visible caption label near the figure in the page (e.g. "Figure 1.1: ...", "Abb. 1.1: ...", "Fig. 1: ...").
- Include the caption as italic text on a new line immediately below the image link: `*Figure 1.1: caption text*`
- Do not skip captions — they are part of the content.

**Special Content:**
- Convert inline mathematical formulas and symbols to LaTeX: $E = mc^2$
- Convert display/block formulas to LaTeX: $$\\int_0^\\infty f(x)\\,dx$$
- Preserve tables in Markdown table format if structure is clear.
- Keep footnotes and references intact.
- Preserve page numbers exactly as they appear (e.g. a standalone "7" at the top or bottom of a page should be kept as plain text).

**Output:**
- Return ONLY the final Markdown - no preamble, no explanations.""",
        "user": "{text}",
    },

    # ------------------------------------------------------------------
    # text — used by the adaptive strategy for TEXT-classified pages.
    # ------------------------------------------------------------------
    "text": {
        "system": """\
You are a PDF-to-Markdown conversion specialist. You will receive raw text extracted from a PDF page. Convert it into clean, well-structured Markdown.

## Rules

**Content Integrity:**
- Preserve the original meaning exactly — do not add, remove, or invent content.
- Do not include commentary, explanations, or meta-text in your output.

**Structure & Formatting:**
- Fix broken line breaks caused by PDF extraction (re-join hyphenated words, merge split sentences).
- Assign heading levels strictly by numbering depth:
  - Chapter / top-level title (e.g. "Kapitel 1", "Chapter 1", "1. Title") → #
  - Section (e.g. "1.1 Title", "2.3 Title") → ##
  - Subsection (e.g. "1.1.1 Title", "2.3.4 Title") → ###
  - Deeper levels → ####
- Only use Markdown headings for structural section titles — do NOT convert bold or italic text to a heading.
- Format bullet and numbered lists correctly.
- Detect and wrap source code in fenced code blocks with a language tag if identifiable.

**Tables & Special Content:**
- Reconstruct tables in Markdown table syntax when the structure is recoverable.
- Convert any inline mathematical formulas or symbols to LaTeX: $E = mc^2$
- Convert any display/block formulas to LaTeX: $$\\int_0^\\infty f(x)\\,dx$$
- Keep footnotes, citations, and references intact.
- Preserve page numbers exactly as they appear (e.g. a standalone "7" in a header or footer should be kept as plain text).

**Output:**
- Return ONLY the Markdown — no preamble, no closing remarks.""",
        "user": "{text}",
    },

    # ------------------------------------------------------------------
    # formula — used by the adaptive strategy for FORMULA-classified pages.
    # ------------------------------------------------------------------
    "formula": {
        "system": """\
You are a mathematical document converter. You will receive an image of a PDF page that contains mathematical formulas. Extract all content and convert it to structured Markdown with LaTeX math notation.

## Rules

**Math Formatting:**
- Convert all inline formulas to LaTeX: $E = mc^2$
- Convert all display/block formulas to LaTeX: $$\\int_0^\\infty f(x)\\,dx$$
- Preserve subscripts, superscripts, Greek letters, and operators accurately.
- Do not approximate or simplify formulas — transcribe them exactly.

**Surrounding Text:**
- Preserve explanatory text, theorem labels, and proof steps in Markdown.
- Maintain the logical flow of derivations.
- Preserve page numbers exactly as they appear in the document.

**Output:**
- Return ONLY the Markdown+LaTeX — no commentary, no preamble.""",
        "user": "{text}",
    },

    # ------------------------------------------------------------------
    # table — used by the adaptive strategy for TABLE-classified pages.
    # ------------------------------------------------------------------
    "table": {
        "system": """\
You are a document table extraction specialist. You will receive an image of a PDF page containing one or more tables. Extract all table content and produce valid Markdown.

## Rules

**Table Formatting:**
- Reconstruct every table using Markdown table syntax: | col | col | with a |---|---| separator after the header row.
- Preserve all cell values exactly — do not paraphrase or summarise.
- If a cell spans multiple columns, approximate it in flat Markdown and note the span if needed.
- Align columns consistently.

**Surrounding Text:**
- Extract any text outside the tables (headings, captions, footnotes) and place it before or after the relevant table.
- Preserve page numbers exactly as they appear.

**Formulas:**
- If a cell contains a formula or symbol, convert it to LaTeX: $formula$ inline, $$formula$$ for display.

**Output:**
- Return ONLY the Markdown — no preamble, no explanations.""",
        "user": "{text}",
    },

    # ------------------------------------------------------------------
    # diagram — used by the adaptive strategy for IMAGE-classified pages.
    # ------------------------------------------------------------------
    "diagram": {
        "system": """\
You are a document analysis specialist. You will receive an image of a PDF page that is dominated by figures, charts, or diagrams. Extract all content and produce structured Markdown.

## Rules

**Text Extraction:**
- Extract all visible text: titles, axis labels, legends, annotations, captions.
- If a heading includes a section number (e.g. "1.1 Motivation" or "2.3.4 Title"), preserve the number exactly — do not drop it.

**Diagram Description:**
- Identify the type of diagram (flowchart, bar chart, scatter plot, architecture diagram, etc.).
- Summarise the key information or trend the diagram conveys in 1–3 sentences.
- Use a Markdown blockquote or italics for the description.

**Tables:**
- If the image contains a table, reconstruct it in Markdown table syntax.

**Formulas:**
- If the image contains mathematical formulas or symbols, convert them to LaTeX: $formula$ for inline, $$formula$$ for display/block.

**Page Numbers:**
- Preserve any page numbers visible in headers or footers as plain text.

**Output:**
- Return ONLY the Markdown — no meta-commentary, no preamble.""",
        "user": "{text}",
    },
}


# ===========================================================================
# PDF text extraction  (extraction/text.py)
# ===========================================================================

def _font_size_to_heading_level(size: float, body_size: float) -> int:
    """Return heading level 1–3 based on ratio to body size, or 0 for body text."""
    if body_size <= 0:
        return 0
    ratio = size / body_size
    if ratio >= 1.8:
        return 1
    if ratio >= 1.4:
        return 2
    if ratio >= 1.15:
        return 3
    return 0


def _page_to_markdown(page: fitz.Page) -> str:
    """Convert a page to markdown text, mapping larger font spans to headings."""
    blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]

    size_tally: Counter = Counter()
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if text:
                    size_tally[round(span["size"])] += len(text)

    body_size: float = size_tally.most_common(1)[0][0] if size_tally else 12

    md_lines: list[str] = []
    for block in blocks:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            dominant_size = body_size
            max_chars = 0
            line_text = ""
            for span in line.get("spans", []):
                line_text += span["text"]
                n = len(span["text"].strip())
                if n > max_chars:
                    max_chars = n
                    dominant_size = span["size"]

            stripped = line_text.strip()
            if not stripped:
                continue

            level = _font_size_to_heading_level(dominant_size, body_size)
            if level:
                md_lines.append("#" * level + " " + stripped)
            else:
                md_lines.append(stripped)

    return "\n".join(md_lines)


def extract_text_pages_from_pdf(pdf_path: str, max_pages: int = 3) -> list[str]:
    """Extract text page by page, using font sizes to detect headings."""
    doc = fitz.open(pdf_path)
    pages = []
    try:
        for i, page in enumerate(doc):  # type: ignore[arg-type]
            if i >= max_pages:
                break
            text = _page_to_markdown(page)
            if text.strip():
                pages.append(text)
    finally:
        doc.close()
    return pages


# ===========================================================================
# PDF image/figure extraction  (extraction/image.py)
# ===========================================================================

def extract_page_figures(
    page: fitz.Page,
    doc: fitz.Document,
    page_num: int,
    figures_dir: str,
) -> list[str]:
    """Extract embedded images from a PDF page and save them as files.

    Returns relative paths (`figures/<filename>`) suitable for Markdown image links.
    """
    os.makedirs(figures_dir, exist_ok=True)
    refs: list[str] = []

    for fig_idx, img_info in enumerate(page.get_images(full=True), start=1):
        xref = img_info[0]
        try:
            img_dict = doc.extract_image(xref)
        except Exception:
            continue

        ext = img_dict.get("ext", "png")
        img_bytes = img_dict["image"]
        filename = f"page_{page_num + 1:03d}_fig_{fig_idx:03d}.{ext}"
        filepath = os.path.join(figures_dir, filename)

        with open(filepath, "wb") as f:
            f.write(img_bytes)

        refs.append(f"figures/{filename}")

    return refs


def extract_image_pages_from_pdf(pdf_path: str, max_pages: int = 3) -> list[str]:
    """Extract images page by page from the PDF as base64-encoded strings."""
    doc = fitz.open(pdf_path)
    images = []
    try:
        for i, page in enumerate(doc):  # type: ignore[arg-type]
            if i >= max_pages:
                break
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("png")
            img_base64 = base64.b64encode(img_data).decode("utf-8")
            if img_base64:
                images.append(img_base64)
    finally:
        doc.close()
    return images


# ===========================================================================
# Page classifier and adaptive routing  (strategies/adaptive.py)
# ===========================================================================

class PageType(Enum):
    TEXT    = "text"     # Pure text    → text_strategy, no LLM
    IMAGE   = "image"    # Image-heavy  → image_strategy with "diagram" prompt
    FORMULA = "formula"  # Math-heavy   → image_strategy with "formula" prompt
    TABLE   = "table"    # Table-heavy  → image_strategy with "table" prompt
    MIXED   = "mixed"    # Text+visual  → image_strategy with "default" prompt
    EMPTY   = "empty"    # Mostly empty → skip


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


_IMAGE_THRESHOLD = 0
_VECTOR_PATH_THRESHOLD = 30
_MIN_TEXT_CHARACTERS = 50


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
    """Analyse a PDF page and return its classified type with confidence."""
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


def render_page_as_base64(page: fitz.Page, dpi: int = 150) -> str:
    """Render a PDF page to a base64-encoded PNG string."""
    matrix = fitz.Matrix(dpi / 72, dpi / 72)
    pixmap = page.get_pixmap(matrix=matrix)
    return base64.b64encode(pixmap.tobytes("png")).decode("utf-8")


# ===========================================================================
# Conversion strategies  (strategies/text_only.py, image_only.py, hybrid.py)
# ===========================================================================

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
    """Convert a PDF page to Markdown using pymupdf4llm, optionally refining with an LLM.

    When `llm_call` is provided the raw pymupdf4llm output is passed through
    the LLM using `prompt_variant` (required for LaTeX math conversion).
    Without `llm_call` the raw Markdown is returned as-is (fast path).

    When `pre_extracted_markdown` is provided, the per-page pymupdf4llm call
    is skipped — callers should bulk-extract once and feed each page chunk in.
    """
    start = time.perf_counter()
    if pre_extracted_markdown is not None:
        raw_markdown = pre_extracted_markdown
    else:
        chunks: list[dict] = pymupdf4llm.to_markdown(
            pdf_path,
            pages=[page_num],
            page_chunks=True,
            write_images=True,
            image_path=figures_dir,
            image_size_limit=0,
        )
        raw_markdown = chunks[0]["text"] if chunks else ""

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


def image_strategy(
    base_url: str,
    model_name: str,
    images: list[str],
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
    figure_refs: list[str] | None = None,
    language: str = "en",
    llm_call: Callable = call_llm,
) -> ConversionResult:
    """Convert page images to Markdown via a vision LLM (image-only input).

    `llm_call` is injectable so tests can swap in a fake without touching
    the network.
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
            "image_url": {"url": f"data:image/png;base64,{img_base64}"},
        })

    messages = [
        {"role": "system", "content": with_language_hint(PROMPTS[prompt_variant]["system"], language)},
        {"role": "user", "content": content},
    ]

    start = time.perf_counter()
    response, token_usage = llm_call(base_url, model_name, messages, temperature, max_tokens)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return ConversionResult(markdown=response, timing_ms=elapsed_ms, token_usage=token_usage, llm_calls=1)


def hybrid_strategy(
    base_url: str,
    model_name: str,
    text: str,
    images: list[str],
    temperature: float,
    max_tokens: int,
    prompt_variant: str = "default",
    figure_refs: list[str] | None = None,
    language: str = "en",
    llm_call: Callable = call_llm,
) -> ConversionResult:
    """Convert a PDF page to Markdown via a vision LLM using both text and image.

    `llm_call` is injectable so tests can swap in a fake without touching
    the network.
    """
    content: list[dict[str, object]] = [
        {"type": "text", "text": PROMPTS[prompt_variant]["user"].format(text=text)}
    ]

    if figure_refs:
        ref_list = "\n".join(
            f"- ![Figure {i + 1}]({ref})" for i, ref in enumerate(figure_refs)
        )
        content.append({
            "type": "text",
            "text": "Extracted figures for this page:\n" + ref_list,
        })

    for img_base64 in images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img_base64}"},
        })

    messages = [
        {"role": "system", "content": with_language_hint(PROMPTS[prompt_variant]["system"], language)},
        {"role": "user", "content": content},
    ]

    start = time.perf_counter()
    response, token_usage = llm_call(base_url, model_name, messages, temperature, max_tokens)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return ConversionResult(markdown=response, timing_ms=elapsed_ms, token_usage=token_usage, llm_calls=1)


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
    text_call: Callable = None,   # type: ignore[assignment]  — set below
    image_call: Callable = None,  # type: ignore[assignment]  — set below
) -> ConversionResult:
    """Select and run the best extraction strategy for the given page type.

    TEXT pages bypass the LLM entirely (pymupdf4llm output is used as-is).
    All other page types send a rendered PNG to the vision LLM with a
    type-appropriate prompt.
    """
    # Late binding avoids a forward-reference problem in default arguments.
    if text_call is None:
        text_call = text_strategy
    if image_call is None:
        image_call = image_strategy

    if page_type == PageType.EMPTY:
        return ConversionResult(markdown="*[Empty page — skipped]*", timing_ms=0.0, token_usage=0, llm_calls=0)

    if page_type == PageType.TEXT:
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

    variant_map = {
        PageType.FORMULA: "formula",
        PageType.IMAGE:   "diagram",
        PageType.TABLE:   "table",
        PageType.MIXED:   "default",
    }
    return image_call(
        base_url=base_url,
        model_name=model_name,
        images=[page_image],
        temperature=temperature,
        max_tokens=max_tokens,
        prompt_variant=variant_map.get(page_type, "default"),
        figure_refs=figure_refs,
        language=language,
    )


# ===========================================================================
# Postprocessing pipeline  (postprocess.py)
# ===========================================================================

_HEADING_RE = re.compile(r"^(#{1,6})\s+(\*{0,2})(.+?)(\*{0,2})\s*$")

_CAPTION_RE = re.compile(
    r"^\*\*((?:Figure|Fig\.|Abb\.|Abbildung|Table|Tabelle)\s+[\d.]+):?\*{0,2}\s*(.*)$",
    re.IGNORECASE,
)

_EMPTY_ITALIC_CAPTION_RE = re.compile(
    r"^\*((?:Figure|Fig\.|Abb\.|Abbildung|Table|Tabelle)\s+[\d.]+):?\*$",
    re.IGNORECASE,
)

_CAPTION_BEFORE_IMAGE_RE = re.compile(
    r"^(\*(?:Figure|Fig\.|Abb\.|Abbildung|Table|Tabelle)[^\n]+\*)"
    r"(\s*\n)+"
    r"(!\[[^\]]*\]\([^\)]+\))",
    re.MULTILINE | re.IGNORECASE,
)

_SYMBOL_ITALIC_RE = re.compile(r"\*{1,2}([^\w\s*_])\*{1,2}|_{1,2}([^\w\s*_])_{1,2}")

_GREEK_TO_LATEX: dict[str, str] = {
    "α": r"\alpha",    "β": r"\beta",      "γ": r"\gamma",   "δ": r"\delta",
    "ε": r"\varepsilon","ζ": r"\zeta",     "η": r"\eta",     "θ": r"\theta",
    "ι": r"\iota",     "κ": r"\kappa",     "λ": r"\lambda",  "μ": r"\mu",
    "ν": r"\nu",       "ξ": r"\xi",        "π": r"\pi",      "ρ": r"\rho",
    "σ": r"\sigma",    "τ": r"\tau",       "υ": r"\upsilon", "φ": r"\varphi",
    "χ": r"\chi",      "ψ": r"\psi",       "ω": r"\omega",
    "Γ": r"\Gamma",    "Δ": r"\Delta",     "Θ": r"\Theta",   "Λ": r"\Lambda",
    "Ξ": r"\Xi",       "Π": r"\Pi",        "Σ": r"\Sigma",   "Υ": r"\Upsilon",
    "Φ": r"\Phi",      "Ψ": r"\Psi",       "Ω": r"\Omega",
}
_GREEK_CHARS: frozenset[str] = frozenset(_GREEK_TO_LATEX)
_GREEK_ITALIC_RE = re.compile(r"_([A-Za-zΑ-ω\d]+)_")

_SUPERSCRIPT_DIGITS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_OCR_SUPERSCRIPT_RE = re.compile(r"_([A-Z]{2,})_\[([1-9])\]")

_FIGURE_INSTRUCTION_RE = re.compile(
    r"The following figures have been extracted\b[^\n]+\n"
    r"(?:- !\[[^\]]*\]\([^\)]+\)\n*)+",
    re.MULTILINE,
)

_SUBSECTION_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\s+\S")
_SECTION_RE    = re.compile(r"^\d{1,3}\.\d{1,3}\s+\S")
_CHAPTER_RE    = re.compile(r"^(?:Kapitel|Chapter|Abschnitt|Section)\s+\d+(?!\s*[-–])\b", re.IGNORECASE)
_TOP_NUM_RE    = re.compile(r"^\d+\.\s")

_OUTLINE_CHAPTER_REF_RE = re.compile(
    r"^(#{1,6})\s+((?:Chapter|Kapitel|Section|Abschnitt)\s+\d+\s*[-–]\s*.+)$",
    re.IGNORECASE | re.MULTILINE,
)

_BARE_NUM_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){1,2}$")

_STRUCTURAL_KEYWORDS: frozenset[str] = frozenset({
    "introduction", "abstract", "conclusion", "summary", "references",
    "bibliography", "appendix", "acknowledgements", "acknowledgments",
    "contents", "overview", "background", "motivation", "evaluation",
    "results", "discussion", "methodology", "outlook", "preface",
    "contributions", "foreword", "erklärung", "surrounding",
    "foundations", "implementation", "requirements", "architecture",
    "design", "approach", "experiments", "analysis", "related",
    "einleitung", "zusammenfassung", "schluss", "literatur", "anhang",
    "vorwort", "danksagung", "inhaltsverzeichnis", "hintergrund",
    "bewertung", "ergebnis", "ausblick", "fazit", "abstrakt",
    "grundlagen", "implementierung", "anforderungen", "entwurf",
})

_DOT_LEADER_RE = re.compile(r"\s*\.(?:\s*\.)+\s*(\d+)\s*$")

_TOC_CONTENTS_HEADER_RE = re.compile(
    r"^\|\s*(Contents|Inhaltsverzeichnis)\s*\|(\s*\|)?\s*$", re.IGNORECASE
)

_TOC_CHAPTER_HEADER_RE = re.compile(
    r"^\|\s*(?:Kapitel|Chapter)\s*\|\s*(?:Abschnitt|Section)\s*\|\s*(?:Seite|Page)\s*\|\s*$",
    re.IGNORECASE,
)

_TABLE_SEPARATOR_RE = re.compile(r"^\|[\s\-:]+(?:\|[\s\-:]+)+\|$")

_LISTING_PAGE_HEADER_RE = re.compile(
    r"^\|\s*(List of Figures|List of Tables|Listings)\s*\|(?:\s*\|)?\s*$", re.IGNORECASE
)

_FIG_NUM_RE = re.compile(r"^(\d+\.\d+)\s*(.*)", re.DOTALL)
_PAGE_NUM_ONLY_RE = re.compile(r"^\d+$")
_DOT_LEADER_LINE_RE = re.compile(r"^[\s.]+$")

_TABLE_LIST_HEADER_2COL_RE = re.compile(
    r"^\|\s*(?:Table|Tabelle)\s*\|\s*(?:Description|Beschreibung)\s*\|\s*$",
    re.IGNORECASE,
)

_DOTS_CELL_RE = re.compile(r"^\.+$")

_ABBR_INLINE_RE = re.compile(
    r"\*\*([A-Z][A-Z0-9]{1,})\*\*\s+([^*]+?)(?=\s+\*\*[A-Z]|\s*$)"
)

_RUNNING_HEADER_RE = re.compile(
    r"^(?:(?:\d{1,3}(?:\.\d{1,3}){0,2})\s+[A-ZÄÖÜ][\w\s\-–—äöüÄÖÜß,()]+|"
    r"(?:Chapter|Kapitel|Section|Abschnitt)\s+\d+\b.*)$"
)


def _heading_depth(text: str) -> int | None:
    plain = re.sub(r"\*+", "", text).strip()
    if _SUBSECTION_RE.match(plain):
        return 3
    if _SECTION_RE.match(plain):
        return 2
    if _CHAPTER_RE.match(plain) or _TOP_NUM_RE.match(plain):
        return 1
    return None


def _reorder_captions_after_images(md: str) -> str:
    return _CAPTION_BEFORE_IMAGE_RE.sub(r"\3\n\1", md)


def _clean_toc_dot_leaders(md: str) -> str:
    lines = md.split("\n")
    result = []
    for line in lines:
        if not line.startswith("|"):
            result.append(line)
            continue
        cells = line.split("|")
        if len(cells) < 3:
            result.append(line)
            continue
        inner = cells[1:-1]
        changed = False
        for j, cell in enumerate(inner):
            dm = _DOT_LEADER_RE.search(cell)
            if dm:
                page_num = dm.group(1)
                cleaned = _DOT_LEADER_RE.sub("", cell).strip()
                inner[j] = f" {cleaned} "
                if j + 1 < len(inner) and not inner[j + 1].strip():
                    inner[j + 1] = f" {page_num} "
                changed = True
        if changed:
            line = "|" + "|".join(inner) + "|"
        result.append(line)
    return "\n".join(result)


def _toc_2col_entry(entry: str, page: str) -> str:
    if re.match(r"^\d+\.\d+\.\d+\s", entry):
        return f"    - {entry} {page}"
    if re.match(r"^\d+\.\d+\s", entry):
        return f"  - {entry} {page}"
    return f"- **{entry}** {page}"


def _toc_3col_entry(col1_raw: str, col2: str, col3: str) -> str:
    col1 = col1_raw.strip()
    if col1:
        if col1[0].isdigit():
            return f"- **{col1} {col2}** {col3}"
        title = f"{col1} {col2}".strip() if col2 else col1
        return f"- **{title}** {col3}"
    n = len(col1_raw) - len(col1_raw.lstrip())
    if n >= 5:
        return f"    - {col2} {col3}"
    return f"  - {col2} {col3}"


def _convert_toc_table(md: str) -> str:
    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if _TOC_CONTENTS_HEADER_RE.match(stripped):
            items: list[str] = []
            i += 1
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    continue
                if not lines[i].strip().startswith("|"):
                    break
                row = lines[i].strip()
                if _TABLE_SEPARATOR_RE.match(row):
                    i += 1
                    continue
                cells = row.split("|")
                if len(cells) >= 4:
                    entry = cells[1].strip()
                    page = cells[2].strip()
                    if entry:
                        items.append(_toc_2col_entry(entry, page))
                i += 1
            result.append("## Contents")
            result.append("")
            result.extend(items)
            continue

        if _TOC_CHAPTER_HEADER_RE.match(stripped):
            items = []
            i += 1
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    continue
                if not lines[i].strip().startswith("|"):
                    break
                row = lines[i]
                if _TABLE_SEPARATOR_RE.match(row.strip()):
                    i += 1
                    continue
                cells = row.split("|")
                if len(cells) >= 5:
                    col1_raw = cells[1]
                    col2 = cells[2].strip()
                    col3 = cells[3].strip()
                    if col2 or col1_raw.strip():
                        items.append(_toc_3col_entry(col1_raw, col2, col3))
                i += 1
            result.extend(items)
            continue

        result.append(lines[i])
        i += 1

    return "\n".join(result)


def _convert_abbreviations(md: str) -> str:
    lines = md.split("\n")
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("**") and "**" in stripped[2:]:
            pairs = _ABBR_INLINE_RE.findall(stripped)
            if len(pairs) >= 3:
                result.append("| Abbreviation | Definition |")
                result.append("|---|---|")
                for abbr, defn in pairs:
                    result.append(f"| {abbr} | {defn.strip()} |")
                continue
        result.append(line)
    return "\n".join(result)


def _split_num_desc(entry: str) -> tuple[str, str]:
    m = re.match(r"^(\d+\.\d+(?:\.\d+)?)\s+(.+)$", entry)
    if m:
        return m.group(1), m.group(2)
    return "", entry


def _parse_lof_entries(raw_text: str) -> list[tuple[str, str, str]]:
    lines = [ln.strip() for ln in raw_text.split("\n")]

    start = None
    for idx, ln in enumerate(lines):
        if re.match(r"^list of figures$", ln, re.IGNORECASE):
            start = idx + 1
            break
    if start is None:
        return []

    entries: list[tuple[str, str, str]] = []
    i = start
    while i < len(lines):
        ln = lines[i]
        if not ln or re.match(r"^[ivxlc]+$", ln, re.IGNORECASE):
            i += 1
            continue

        m = _FIG_NUM_RE.match(ln)
        if not m:
            break

        num = m.group(1)
        rest = m.group(2).strip()

        if rest:
            desc = re.sub(r"\s*\.+\s*", " ", rest).strip().rstrip(".")
            j = i + 1
            while j < len(lines) and not lines[j]:
                j += 1
            page = ""
            if j < len(lines):
                if _PAGE_NUM_ONLY_RE.match(lines[j]):
                    page = lines[j]
                    i = j + 1
                elif _DOT_LEADER_LINE_RE.match(lines[j]):
                    k = j + 1
                    while k < len(lines) and not lines[k]:
                        k += 1
                    if k < len(lines) and _PAGE_NUM_ONLY_RE.match(lines[k]):
                        page = lines[k]
                        i = k + 1
                    else:
                        i = k
                else:
                    i = j
            else:
                i = j
        else:
            j = i + 1
            while j < len(lines) and not lines[j]:
                j += 1
            if j >= len(lines):
                break
            desc_raw = lines[j]
            desc = re.sub(r"\s*\.+\s*", " ", desc_raw).strip().rstrip(".")
            k = j + 1
            while k < len(lines) and not lines[k]:
                k += 1
            page = ""
            if k < len(lines):
                if _PAGE_NUM_ONLY_RE.match(lines[k]):
                    page = lines[k]
                    i = k + 1
                elif _DOT_LEADER_LINE_RE.match(lines[k]):
                    m2 = k + 1
                    while m2 < len(lines) and not lines[m2]:
                        m2 += 1
                    if m2 < len(lines) and _PAGE_NUM_ONLY_RE.match(lines[m2]):
                        page = lines[m2]
                        i = m2 + 1
                    else:
                        i = m2
                else:
                    i = k
            else:
                i = k

        entries.append((num, desc, page))

    return entries


def _fix_lof_numbers(md: str, raw_page_text: str = "") -> str:
    if not raw_page_text or "List of Figures" not in raw_page_text:
        return md

    entries = _parse_lof_entries(raw_page_text)
    if not entries:
        return md

    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        is_lof = re.match(r"^\|\s*List of Figures\s*\|", stripped, re.IGNORECASE) or re.match(
            r"^#{1,3}\s*List of Figures\s*$", stripped, re.IGNORECASE
        )
        if is_lof:
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    if j < len(lines) and lines[j].strip().startswith("|"):
                        i = j
                        continue
                    break
                if s.startswith("|"):
                    i += 1
                    continue
                break

            result.append("## List of Figures")
            result.append("")
            result.append("| Figure | Description | Page |")
            result.append("|---|---|---|")
            for fig_num, desc, page in entries:
                result.append(f"| {fig_num} | {desc} | {page} |")
            continue

        result.append(lines[i])
        i += 1

    return "\n".join(result)


def _fix_listing_table(md: str) -> str:
    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        m = _LISTING_PAGE_HEADER_RE.match(lines[i].strip())
        if m:
            section = m.group(1)
            num_col = "Figure" if "Figure" in section else ("Table" if "Table" in section else "Listing")
            rows: list[str] = []
            i += 1
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    continue
                if not lines[i].strip().startswith("|"):
                    break
                row = lines[i].strip()
                if _TABLE_SEPARATOR_RE.match(row):
                    i += 1
                    continue
                cells = row.split("|")
                inner = [c.strip() for c in cells[1:-1]]
                non_dot = [c for c in inner if c and not _DOTS_CELL_RE.match(c)]
                if not non_dot:
                    i += 1
                    continue
                entry = non_dot[0]
                page = ""
                if len(non_dot) > 1:
                    last = non_dot[-1]
                    if re.match(r"^[a-zA-Z0-9]+$", last) and last != entry:
                        page = last
                num, desc = _split_num_desc(entry)
                rows.append(f"| {num} | {desc} | {page} |")
                i += 1
            result.append(f"## {section}")
            result.append("")
            result.append(f"| {num_col} | Description | Page |")
            result.append("|---|---|---|")
            result.extend(rows)
            continue
        result.append(lines[i])
        i += 1
    return "\n".join(result)


def _fix_table_list_header(md: str) -> str:
    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        if _TABLE_LIST_HEADER_2COL_RE.match(lines[i].strip()):
            last_content = next(
                (result[j] for j in range(len(result) - 1, -1, -1) if result[j].strip()),
                "",
            )
            if not last_content.startswith("##"):
                result.append("## List of Tables")
                result.append("")
            result.append("| Table | Description | Page |")
            i += 1
            if i < len(lines) and _TABLE_SEPARATOR_RE.match(lines[i].strip()):
                result.append("|---|---|---|")
                i += 1
            else:
                result.append("|---|---|---|")
            continue
        result.append(lines[i])
        i += 1
    return "\n".join(result)


def _demote_unlabeled_single_word_headings(md: str) -> str:
    def _replace(m: re.Match) -> str:
        hashes, content = m.group(1), m.group(2).strip()
        if re.match(r"^\d", content):
            return m.group(0)
        words = content.split()
        if len(words) == 1 and content.lower() not in _STRUCTURAL_KEYWORDS:
            return f"**{content}**"
        if content.endswith(" :"):
            return f"**{content}**"
        if len(content) > 80 and hashes != "#":
            return f"**{content}**"
        return m.group(0)

    return re.sub(r"^(#{1,6})\s+(.+)$", _replace, md, flags=re.MULTILINE)


def _demote_outline_chapter_refs(md: str) -> str:
    return _OUTLINE_CHAPTER_REF_RE.sub(r"**\2**", md)


def _strip_running_headers(md: str) -> str:
    lines = md.split("\n")
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return md
    first = lines[i].strip()
    if first and first[0] not in ("#", "-", "*", ">", "!", "[", "|", "`"):
        if _RUNNING_HEADER_RE.match(first):
            del lines[i]
            while i < len(lines) and not lines[i].strip():
                del lines[i]
    return "\n".join(lines)


def _fix_bold_space_before_colon(md: str) -> str:
    return re.sub(r"\*\*([^*]+?)\s+:\*\*", r"**\1:**", md)


def _fix_bold_listing_headings(md: str) -> str:
    return re.sub(
        r"^\*\*(List of Figures|List of Tables|Listings)\*\*\s*$",
        lambda m: f"## {m.group(1)}",
        md,
        flags=re.IGNORECASE | re.MULTILINE,
    )


_DECLARATION_LINE_RE = re.compile(
    r"^(Erklärung(?:\s*/\s*Declaration)?|Declaration)\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _promote_declaration_heading(md: str) -> str:
    return _DECLARATION_LINE_RE.sub(lambda m: f"## {m.group(1)}", md)


def _unwrap_symbol_italics(md: str) -> str:
    return _SYMBOL_ITALIC_RE.sub(lambda m: m.group(1) or m.group(2), md)


def _convert_greek_italic_math(md: str) -> str:
    def _to_latex(m: re.Match) -> str:
        content = m.group(1)
        if not any(c in _GREEK_CHARS for c in content):
            return m.group(0)

        greek_part = ""
        subscript = ""
        entered_subscript = False
        for c in content:
            if c in _GREEK_CHARS and not entered_subscript:
                greek_part += _GREEK_TO_LATEX[c]
            else:
                entered_subscript = True
                subscript += c

        if not subscript:
            return f"${greek_part}$"
        if len(subscript) == 1:
            return f"${greek_part}_{subscript}$"
        return f"${greek_part}_{{{subscript}}}$"

    lines = md.split("\n")
    result: list[str] = []
    in_code = False
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
        if in_code:
            result.append(line)
        else:
            result.append(_GREEK_ITALIC_RE.sub(_to_latex, line))
    return "\n".join(result)


def _fix_ocr_superscripts(md: str) -> str:
    return _OCR_SUPERSCRIPT_RE.sub(
        lambda m: m.group(1) + m.group(2).translate(_SUPERSCRIPT_DIGITS),
        md,
    )


def _format_figure_captions(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _EMPTY_ITALIC_CAPTION_RE.match(line):
            i += 1
            continue

        cm = _CAPTION_RE.match(line)
        if cm:
            label = cm.group(1).rstrip(":")
            text = cm.group(2).strip()
            if not text:
                i += 1
                continue
            caption_line = f"*{label}: {text}*"
            last_content = next(
                (out[j] for j in range(len(out) - 1, -1, -1) if out[j].strip()),
                "",
            )
            if last_content.startswith("!["):
                while out and out[-1].strip() == "":
                    out.pop()
            out.append(caption_line)
        else:
            out.append(line)
        i += 1
    return "\n".join(out)


def _recover_bare_number_headings(md: str, raw_text: str) -> str:
    if not raw_text:
        return md

    fitz_titles: dict[str, str] = {}
    fitz_numbers: dict[str, str] = {}
    for raw_line in raw_text.splitlines():
        raw_line = raw_line.strip()
        m = re.match(r"^(\d{1,3}(?:\.\d{1,3}){1,2})\s+(.+)$", raw_line)
        if m:
            num, title = m.group(1), m.group(2).strip()
            title = title.replace("ﬂ", "fl").replace("ﬁ", "fi")
            fitz_titles[num] = title
            fitz_numbers[title.lower()] = num

    if not fitz_titles:
        return md

    def _patch_bare_number(m: re.Match) -> str:
        hashes, num = m.group(1), m.group(2).strip()
        title = fitz_titles.get(num)
        if title:
            return f"{hashes} {num} {title}"
        return m.group(0)

    md = re.sub(r"^(#{1,6})\s+(\d[\d.]+)[ \t]*$", _patch_bare_number, md, flags=re.MULTILINE)

    def _patch_missing_number(m: re.Match) -> str:
        hashes, content = m.group(1), m.group(2).strip()
        if re.match(r"^\d", content):
            return m.group(0)
        if content.lower() in _STRUCTURAL_KEYWORDS:
            return m.group(0)
        num = fitz_numbers.get(content.lower())
        if num:
            return f"{hashes} {num} {content}"
        return m.group(0)

    return re.sub(r"^(#{2,6})\s+(\S[^\n]*)$", _patch_missing_number, md, flags=re.MULTILINE)


def _merge_split_headings(md: str) -> str:
    lines = md.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m and _BARE_NUM_RE.match(m.group(2).strip()):
            hashes, num = m.group(1), m.group(2).strip()
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines):
                next_m = re.match(r"^(#{1,6})\s+(.+)$", lines[j])
                if next_m and next_m.group(1) == hashes:
                    out.append(f"{hashes} {num} {next_m.group(2).strip()}")
                    i = j + 1
                    continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _strip_bold_from_headings(md: str) -> str:
    def _strip_markers(m: re.Match) -> str:
        hashes = m.group(1)
        content = m.group(2)
        content = re.sub(r"\*\*\*(.+?)\*\*\*", r"_\1_", content)
        content = re.sub(r"\*\*(.+?)\*\*", r"\1", content)
        content = re.sub(r"__(.+?)__", r"\1", content)
        return f"{hashes} {content.strip()}"

    return re.sub(r"^(#{1,6}) (.+)$", _strip_markers, md, flags=re.MULTILINE)


def normalize_heading_levels(md: str) -> str:
    """Re-assign Markdown heading levels based on section-number patterns."""
    lines = md.split("\n")
    out = []
    for line in lines:
        m = _HEADING_RE.match(line)
        if m:
            hashes, open_bold, content, close_bold = m.groups()
            depth = _heading_depth(content)
            if depth is not None:
                line = "#" * depth + " " + open_bold + content + close_bold
        out.append(line)
    return "\n".join(out)


def clean_page(md: str, raw_page_text: str = "") -> str:
    """Clean a single page's Markdown before pages are joined."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    md = _FIGURE_INSTRUCTION_RE.sub("", md)
    md = re.sub(r"```markdown\n(.*?)```", lambda m: m.group(1), md, flags=re.DOTALL)
    md = re.sub(r"(^#{1,6} .+\n)\n*([ \t]*(-{3,}|\*{3,}|_{3,})[ \t]*\n)", r"\1\n", md, flags=re.MULTILINE)

    md = _fix_bold_space_before_colon(md)
    md = _fix_bold_listing_headings(md)
    md = _promote_declaration_heading(md)
    md = _strip_running_headers(md)
    md = _clean_toc_dot_leaders(md)
    md = _convert_toc_table(md)
    md = _fix_lof_numbers(md, raw_page_text)
    md = _fix_listing_table(md)
    md = _fix_table_list_header(md)
    md = _convert_abbreviations(md)
    md = _unwrap_symbol_italics(md)
    md = _convert_greek_italic_math(md)
    md = _fix_ocr_superscripts(md)
    md = _format_figure_captions(md)
    md = _reorder_captions_after_images(md)
    md = _strip_bold_from_headings(md)
    md = _merge_split_headings(md)
    md = _recover_bare_number_headings(md, raw_page_text)
    md = normalize_heading_levels(md)
    md = _demote_outline_chapter_refs(md)
    md = _demote_unlabeled_single_word_headings(md)

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip()


_FRONT_MATTER_SECTIONS: frozenset[str] = frozenset({
    "erklärung", "declaration",
    "abstrakt", "abstract",
    "inhaltsverzeichnis", "table of contents", "contents",
    "vorwort", "preface",
    "zusammenfassung", "summary",
    "danksagung", "acknowledgements", "acknowledgments",
})

_KAPITEL_RE = re.compile(r"^##\s+((?:Kapitel|Chapter))\s+(\d+)\s*$", re.IGNORECASE)
_CHAPTER_H1_RE = re.compile(r"^#\s+((?:Kapitel|Chapter))\s+(\d+)\s*$", re.IGNORECASE)

_FULLY_ITALIC_HEADING_RE = re.compile(r"^#{1,6}\s+(_[^_\n]+_)\s*$", re.MULTILINE)
_CODE_LISTING_HEADING_RE = re.compile(r"^#{1,6}\s+(\d+\s+`[^`\n]+`)\s*$", re.MULTILINE)

_PICTURE_TEXT_BLOCK_RE = re.compile(
    r"\*\*----- Start of picture text -----\*\*<br>\n(.*?)"
    r"\*\*----- End of picture text -----\*\*<br>",
    re.DOTALL,
)


def _demote_italic_headings(md: str) -> str:
    return _FULLY_ITALIC_HEADING_RE.sub(r"\1", md)


def _demote_code_listing_headings(md: str) -> str:
    return _CODE_LISTING_HEADING_RE.sub(r"- \1", md)


def _clean_picture_text_blocks(md: str) -> str:
    return _PICTURE_TEXT_BLOCK_RE.sub("", md)


def _demote_title_page_headings(md: str) -> str:
    lines = md.split("\n")
    title_page_end = len(lines)
    for i, line in enumerate(lines):
        m = re.match(r"^#{1,6}\s+(.+)$", line)
        if m:
            title = m.group(1).strip().lower()
            if title in _FRONT_MATTER_SECTIONS:
                title_page_end = i
                break

    if title_page_end == len(lines):
        return md

    result = []
    found_h1 = False
    for i, line in enumerate(lines):
        if i >= title_page_end:
            result.append(line)
            continue
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            level = len(m.group(1))
            if level == 1 and not found_h1:
                found_h1 = True
                result.append(line)
            elif level >= 2:
                content = m.group(2).strip().rstrip(": ")
                result.append(content)
            else:
                result.append(line)
        else:
            result.append(line)
    return "\n".join(result)


def _merge_kapitel_headings(md: str) -> str:
    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        m1 = _CHAPTER_H1_RE.match(lines[i])
        if m1:
            chapter_word, chapter_num = m1.group(1), m1.group(2)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                m2 = re.match(r"^##\s+(.+)$", lines[j])
                if m2:
                    title = re.sub(r"\*+$", "", m2.group(1)).strip()
                    result.append(f"# {chapter_word} {chapter_num}: {title}")
                    i = j + 1
                    continue
            result.append(lines[i])
            i += 1
            continue
        m2 = _KAPITEL_RE.match(lines[i])
        if m2:
            chapter_word, chapter_num = m2.group(1), m2.group(2)
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines):
                m3 = re.match(r"^#{1,6}\s+(.+)$", lines[j])
                if m3:
                    title = re.sub(r"\*+$", "", m3.group(1)).strip()
                    result.append(f"# {chapter_word} {chapter_num}: {title}")
                    i = j + 1
                    continue
            i += 1
            continue
        result.append(lines[i])
        i += 1
    return "\n".join(result)


def _strip_duplicate_section_headers(md: str) -> str:
    lines = md.split("\n")
    seen_titled_headings: set[str] = set()
    seen_all_headings: set[str] = set()
    seen_exact_numbered: set[str] = set()
    result: list[str] = []

    for line in lines:
        m_numbered = re.match(r"^##\s+(\d[\d.]*\s+.+)$", line)
        if m_numbered:
            full = m_numbered.group(1).strip()
            key = full.lower()
            if key in seen_exact_numbered:
                continue
            seen_exact_numbered.add(key)
            title_part = re.sub(r"^\d[\d.]*\s+", "", full).strip().lower()
            seen_titled_headings.add(title_part)
            seen_all_headings.add(title_part)
            result.append(line)
            continue

        m_unnumbered = re.match(r"^##\s+(\S[^\n]*)$", line)
        if m_unnumbered:
            title = m_unnumbered.group(1).strip().lower()
            if title in seen_titled_headings:
                continue
            seen_all_headings.add(title)
            result.append(line)
            continue

        m_kapitel = re.match(
            r"^#\s+(?:Kapitel|Chapter)\s+\d+\s+(.+)$", line, re.IGNORECASE
        )
        if m_kapitel:
            title = m_kapitel.group(1).strip().lower()
            if title in seen_all_headings:
                continue
            seen_all_headings.add(title)
            result.append(line)
            continue

        result.append(line)

    return "\n".join(result)


def _strip_bibliography_dash(md: str) -> str:
    md = re.sub(
        r"(^\*\*[^\n]+\*\*\s*\n\n)([–—])\s+",
        r"\1",
        md,
        flags=re.MULTILINE,
    )
    md = re.sub(r"\.\s*[–—][ \t]*$", ".", md, flags=re.MULTILINE)
    return md


def _strip_mid_doc_page_numbers(md: str) -> str:
    md = re.sub(r"\n\n\d{1,3} ?\n\n", "\n\n", md)
    md = re.sub(r"\n\n[ivxIVX]{1,8} ?\n\n", "\n\n", md)
    return md


def _strip_mid_doc_running_headers(md: str) -> str:
    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if (
            stripped
            and stripped[0] not in ("#", "-", "*", ">", "!", "[", "|", "`", "_")
            and not stripped.startswith("**")
            and (
                _RUNNING_HEADER_RE.match(stripped)
                or stripped.lower() in _FRONT_MATTER_SECTIONS
            )
        ):
            prev_blank = i == 0 or not lines[i - 1].strip()
            next_blank = i == len(lines) - 1 or not lines[i + 1].strip()
            if prev_blank and next_blank:
                i += 1
                continue
        result.append(lines[i])
        i += 1
    return "\n".join(result)


def _normalise_latex_delimiters(md: str) -> str:
    md = re.sub(r"\\\[\s*(.*?)\s*\\\]", r"$$\1$$", md, flags=re.DOTALL)
    md = re.sub(r"\\\(\s*(.*?)\s*\\\)", r"$\1$", md, flags=re.DOTALL)
    return md


def postprocess_markdown(md: str) -> str:
    """Final cleanup applied to the fully joined Markdown document."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")
    md = _strip_bold_from_headings(md)
    md = _demote_italic_headings(md)
    md = _demote_code_listing_headings(md)
    md = _clean_picture_text_blocks(md)
    md = _demote_title_page_headings(md)
    md = _merge_kapitel_headings(md)
    md = _strip_duplicate_section_headers(md)
    md = _strip_bibliography_dash(md)
    md = _normalise_latex_delimiters(md)
    md = _strip_mid_doc_page_numbers(md)
    md = _strip_mid_doc_running_headers(md)

    md = re.sub(r"\n\n(\d{1,3})\n\n---", "\n\n---", md)
    md = re.sub(r"\n\n(\d{1,3})\s*$", "", md)

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip() + "\n"


# ===========================================================================
# Main pipeline  (app.py)
# ===========================================================================

def _page_label(doc: fitz.Document, index: int) -> str:
    """Return the printed page label (e.g. 'v', '3') for a 0-based page index."""
    label = doc[index].get_label()
    return label if label else str(index + 1)


def _bulk_extract_markdown(pdf_path: str, num_pages: int, figures_dir: str) -> list[str]:
    """Run pymupdf4llm.to_markdown once for the whole page range."""
    chunks: list[dict] = pymupdf4llm.to_markdown(
        pdf_path,
        pages=list(range(num_pages)),
        page_chunks=True,
        write_images=True,
        image_path=figures_dir,
        image_size_limit=0,
    )
    return [chunk.get("text", "") for chunk in chunks]


def _run_in_pool(indices: list[int], concurrency: int, worker) -> list:
    """Run `worker(i)` for each i in `indices` concurrently and return results in input order."""
    workers = max(1, min(concurrency, len(indices)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(worker, indices))


def run(config: Config) -> None:
    figures_dir = os.path.join(os.path.dirname(os.path.abspath(config.output)), "figures")
    llm = partial(call_llm, timeout=config.llm_timeout)

    sample_text = ""
    with fitz.open(config.input) as _doc:
        sample_text = _doc[0].get_text("text") if len(_doc) > 0 else ""
    language = detect_language(sample_text)
    print(f"Detected language: {language_name(language)} ({language})")

    with fitz.open(config.input) as doc:
        num_pages = min(len(doc), config.max_pages)
        if num_pages == 0:
            raise ValueError("No pages could be read from the PDF.")
        page_labels = [_page_label(doc, i) for i in range(num_pages)]

    page_indices = list(range(num_pages))
    total_tokens = 0
    total_llm_calls = 0

    match config.strategy:
        case "text":
            page_markdown = _bulk_extract_markdown(config.input, num_pages, figures_dir)

            def _convert_text(i: int) -> tuple:
                label = page_labels[i]
                raw_text = ""
                with fitz.open(config.input) as worker_doc:
                    raw_text = worker_doc[i].get_text("text")
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
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result.markdown, raw_page_text=raw_text)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert_text)
            cleaned_pages = [r[0] for r in raw_results]
            total_tokens = sum(r[1] or 0 for r in raw_results)
            total_llm_calls = sum(r[2] for r in raw_results)

        case "image":
            def _convert_image(i: int) -> tuple:
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
                    llm_call=llm,
                )
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert_image)
            cleaned_pages = [r[0] for r in raw_results]
            total_tokens = sum(r[1] or 0 for r in raw_results)
            total_llm_calls = sum(r[2] for r in raw_results)

        case "hybrid":
            pages = extract_text_pages_from_pdf(config.input, max_pages=config.max_pages)
            if not pages:
                raise ValueError("No text could be extracted from the PDF.")

            def _convert_hybrid(i: int) -> tuple:
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
                    llm_call=llm,
                )
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result.markdown)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert_hybrid)
            cleaned_pages = [r[0] for r in raw_results]
            total_tokens = sum(r[1] or 0 for r in raw_results)
            total_llm_calls = sum(r[2] for r in raw_results)

        case "adaptive":
            page_markdown = _bulk_extract_markdown(config.input, num_pages, figures_dir)

            def _convert_adaptive(i: int) -> tuple:
                label = page_labels[i]
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
                    image_call=partial(image_strategy, llm_call=llm),
                )
                page_md = f"<!-- Page {label} -->\n\n{clean_page(result.markdown, raw_page_text=raw_text)}"
                return page_md, result.token_usage, result.llm_calls

            raw_results = _run_in_pool(page_indices, config.concurrency, _convert_adaptive)
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

    print(f"Done! Output saved as '{config.output}'.")
    if total_llm_calls > 0:
        avg = total_tokens // total_llm_calls
        print(f"Token usage: {total_tokens:,} tokens ({total_llm_calls} LLM calls, avg {avg:,}/call)")
    else:
        print("Token usage: 0 (no LLM calls — text strategy)")


# ===========================================================================
# CLI argument parsing  (cli.py)
# ===========================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF to Markdown using an adaptive LLM-based pipeline."
    )
    parser.add_argument(
        "-i", "--input",
        default="pdf_source/test_pdf_source.pdf",
        help="Input PDF file",
    )
    parser.add_argument(
        "-o", "--output",
        default="output/test_pdf_output.md",
        help="Output Markdown file",
    )
    parser.add_argument(
        "-b", "--base-url",
        default=DEFAULT_BASE_URL,
        help="LM Studio base URL",
    )
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL, help="Model name")
    parser.add_argument(
        "-n", "--max-pages",
        type=int,
        default=20,
        help="Maximum number of pages to convert",
    )
    parser.add_argument(
        "-s", "--strategy",
        default="text",
        choices=["text", "image", "hybrid", "adaptive"],
        help="Conversion strategy",
    )
    parser.add_argument(
        "-t", "--temperature",
        type=float,
        default=0.2,
        help="LLM temperature (0.0 = deterministic, 1.0 = creative)",
    )
    parser.add_argument(
        "-T", "--max-tokens",
        type=int,
        default=4096,
        help="Maximum response tokens from LLM",
    )
    parser.add_argument(
        "-c", "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help="Number of pages converted in parallel",
    )
    return parser.parse_args()


# ===========================================================================
# Entry point  (main.py)
# ===========================================================================

def main() -> None:
    args = parse_args()
    config = Config(
        input=args.input,
        output=args.output,
        base_url=args.base_url,
        model=args.model,
        max_pages=args.max_pages,
        strategy=args.strategy,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        concurrency=args.concurrency,
    )
    run(config)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
