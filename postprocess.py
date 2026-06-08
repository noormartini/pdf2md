import re

# Matches numbered heading text inside any Markdown heading line.
# Groups: (hashes, optional bold markers, heading text content)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(\*{0,2})(.+?)(\*{0,2})\s*$")

# Matches figure caption lines that pymupdf4llm emits as bold text, e.g.:
#   **Figure 1.1:** What is this Thesis about?
#   **Abb. 2.3:** Description
# Requires exactly ** at the start so already-italic lines (*...) are skipped.
# Group 1 = label (e.g. "Figure 1.1"), group 2 = caption text
_CAPTION_RE = re.compile(
    r"^\*\*((?:Figure|Fig\.|Abb\.|Abbildung|Table|Tabelle)\s+[\d.]+):?\*{0,2}\s*(.*)$",
    re.IGNORECASE,
)

# Detects an italic figure caption that sits BEFORE an image link so the two
# can be swapped.  By the time this regex runs, _format_figure_captions has
# already converted all bold captions to italic, so only the italic form needs
# to be matched here.
# Group 1 = full caption line, group 3 = full image link line.
_CAPTION_BEFORE_IMAGE_RE = re.compile(
    r"^(\*(?:Figure|Fig\.|Abb\.|Abbildung|Table|Tabelle)[^\n]+\*)"
    r"(\s*\n)+"
    r"(!\[[^\]]*\]\([^\)]+\))",
    re.MULTILINE | re.IGNORECASE,
)

# Matches italic/bold wrappers around a single non-word Unicode symbol, e.g.:
#   _⇒_  →  ⇒
#   **→**  →  →
# pymupdf4llm emits these when a symbol span happens to use an italic/bold font.
# The underscore form is the most common; the ** form also appears occasionally.
_SYMBOL_ITALIC_RE = re.compile(r"\*{1,2}([^\w\s*_])\*{1,2}|_{1,2}([^\w\s*_])_{1,2}")

# Matches OCR superscript artifacts where an all-caps abbreviation followed by a
# superscript digit was extracted as italic text + bracket citation, e.g.:
#   _EMC_[2]  →  EMC²
# The pattern only fires when the bracketed value is a single digit (1–9), which
# distinguishes it from real multi-digit citation references like [12] or [2016].
_SUPERSCRIPT_DIGITS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_OCR_SUPERSCRIPT_RE = re.compile(r"_([A-Z]{2,})_\[([1-9])\]")

# Matches the figure-ref instruction block that leaks from the LLM prompt into
# its output — e.g. "The following figures have been extracted from this page
# and saved as files. Include them as Markdown image links..."
# We strip the preamble sentence + the duplicated image list; the figures
# themselves appear correctly later in the same output.
_FIGURE_INSTRUCTION_RE = re.compile(
    r"The following figures have been extracted\b[^\n]+\n"
    r"(?:- !\[[^\]]*\]\([^\)]+\)\n*)+",
    re.MULTILINE,
)

# Patterns for detecting heading depth from section numbers.
_SUBSECTION_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\s+\S")  # e.g. "1.1.1 Title"
_SECTION_RE    = re.compile(r"^\d{1,3}\.\d{1,3}\s+\S")           # e.g. "1.1 Title"
# Only match bare "Chapter N" or "Chapter N Title" — NOT "Chapter N - Title" which
# is an outline back-reference (e.g. in "Outline of this document") not a real heading.
_CHAPTER_RE    = re.compile(r"^(?:Kapitel|Chapter|Abschnitt|Section)\s+\d+(?!\s*[-–])\b", re.IGNORECASE)
_TOP_NUM_RE    = re.compile(r"^\d+\.\s")           # e.g. "1. Introduction"

# Matches heading lines that are outline back-references to chapters, e.g.:
#   ## Chapter 1 - Introduction
#   ## Kapitel 2 – Ausführungsplan
# These should be rendered as bold text, not structural headings.
_OUTLINE_CHAPTER_REF_RE = re.compile(
    r"^(#{1,6})\s+((?:Chapter|Kapitel|Section|Abschnitt)\s+\d+\s*[-–]\s*.+)$",
    re.IGNORECASE | re.MULTILINE,
)

# Matches a heading that is ONLY a section number with no title, e.g. "1.1" or "2.3.4".
_BARE_NUM_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){1,2}$")

# Single-word headings that ARE legitimate structural section titles (keep as headings).
# All lowercase for case-insensitive matching.
_STRUCTURAL_KEYWORDS: frozenset[str] = frozenset({
    # English
    "introduction", "abstract", "conclusion", "summary", "references",
    "bibliography", "appendix", "acknowledgements", "acknowledgments",
    "contents", "overview", "background", "motivation", "evaluation",
    "results", "discussion", "methodology", "outlook", "preface",
    "contributions", "foreword", "erklärung", "surrounding",
    # German
    "einleitung", "zusammenfassung", "schluss", "literatur", "anhang",
    "vorwort", "danksagung", "inhaltsverzeichnis", "hintergrund",
    "bewertung", "ergebnis", "ausblick", "fazit",
})

# Matches a PDF running header (Kopfzeile) line — a plain-text repetition of the
# chapter/section title that appears at the top of every PDF page.
# Pattern: optional section number (e.g. "2" or "2.1"), a space, then a title
# consisting of word characters.  The line must NOT start with a Markdown marker
# (#, -, *, >) and must NOT end in punctuation (actual prose starts with a capital
# but usually has sentence punctuation).  Also matches "Chapter N" style headers.
_RUNNING_HEADER_RE = re.compile(
    r"^(?:(?:\d{1,3}(?:\.\d{1,3}){0,2})\s+[A-ZÄÖÜ][\w\s\-–—äöüÄÖÜß,()]+|"
    r"(?:Chapter|Kapitel|Section|Abschnitt)\s+\d+\b.*)$"
)


def _heading_depth(text: str) -> int | None:
    """Return the correct heading level (1–3) from numbering patterns, or None."""
    plain = re.sub(r"\*+", "", text).strip()
    if _SUBSECTION_RE.match(plain):
        return 3
    if _SECTION_RE.match(plain):
        return 2
    if _CHAPTER_RE.match(plain) or _TOP_NUM_RE.match(plain):
        return 1
    return None


def _reorder_captions_after_images(md: str) -> str:
    """Move figure captions that appear before their image to after the image.

    LLMs sometimes output the caption label first, then the image link:
        *Figure 1.1: What is this Thesis about?*

        ![Figure 1](figures/page_009_fig_001.png)

    This swaps them so the image always precedes its caption:
        ![Figure 1](figures/page_009_fig_001.png)
        *Figure 1.1: What is this Thesis about?*
    """
    return _CAPTION_BEFORE_IMAGE_RE.sub(r"\3\n\1", md)


def _demote_unlabeled_single_word_headings(md: str) -> str:
    """Convert single-word unnumbered headings to bold text.

    pymupdf4llm's layout parser promotes bold body-size labels like "Company"
    or "Department" to ## headings because they appear visually like section
    titles.  A heading is likely a mis-promoted label when it:
      - consists of exactly one word (no spaces or digits)
      - has no section number at the start
      - is not a recognised structural section title keyword

    Those are converted to **bold** text.  Multi-word headings and known
    keywords (Introduction, Abstract, Conclusion, etc.) are left untouched.
    """
    def _replace(m: re.Match) -> str:
        hashes, content = m.group(1), m.group(2).strip()
        words = content.split()
        if len(words) != 1:
            return m.group(0)
        if re.match(r"^\d", content):  # starts with section number → keep
            return m.group(0)
        if content.lower() in _STRUCTURAL_KEYWORDS:
            return m.group(0)
        return f"**{content}**"

    return re.sub(r"^(#{1,6})\s+(.+)$", _replace, md, flags=re.MULTILINE)


def _demote_outline_chapter_refs(md: str) -> str:
    """Convert outline back-references from headings to bold text.

    In the "Outline of this document" section, chapter descriptions like
    "Chapter 1 - Introduction" are formatted in the same bold font as section
    headings, so pymupdf4llm emits them as ## headings.  They are NOT real
    structural headings — they are just bold labels.  This pass converts them
    back to bold text:
        ## Chapter 1 - Introduction  →  **Chapter 1 - Introduction**
    The dash is the key distinguisher: real chapter headings ("Chapter 1",
    "Chapter 2") have no dash; outline references always do.
    """
    return _OUTLINE_CHAPTER_REF_RE.sub(r"**\2**", md)


def _strip_running_headers(md: str) -> str:
    """Remove PDF running headers (Kopfzeilen) from the top of each page chunk.

    Running headers are the chapter/section title repeated in the page header
    area of the PDF (e.g. "2 Execution plan", "2.2 Dataset research").
    pymupdf4llm extracts them as plain-text lines at the very start of each
    page chunk — they are NOT Markdown headings (no # prefix) and carry no
    new information since the actual heading already appeared on the section's
    first page.

    Only the first non-empty line is considered; if it matches the running
    header pattern it is removed together with any blank lines that immediately
    follow it (so the page content starts cleanly).
    """
    lines = md.split("\n")
    i = 0
    # Skip leading blank lines to find the first content line.
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return md
    first = lines[i].strip()
    # Must not start with any Markdown marker.
    if first and first[0] not in ("#", "-", "*", ">", "!", "[", "|", "`"):
        if _RUNNING_HEADER_RE.match(first):
            # Remove this line and any immediately following blank lines.
            del lines[i]
            while i < len(lines) and not lines[i].strip():
                del lines[i]
    return "\n".join(lines)


def _unwrap_symbol_italics(md: str) -> str:
    """Strip italic/bold markers wrapping a single non-word Unicode symbol.

    pymupdf4llm wraps arrow characters in underscore italic because the glyph
    uses an italic font variant in the PDF, e.g. ``_⇒_``.  Most Markdown
    renderers do not apply italic styling to non-alphabetic characters and
    leave the underscores as literal text, which looks wrong.  This pass
    removes those markers so ``_⇒_`` becomes ``⇒``.
    """
    return _SYMBOL_ITALIC_RE.sub(lambda m: m.group(1) or m.group(2), md)


def _fix_ocr_superscripts(md: str) -> str:
    """Fix OCR artefacts where superscript digits were extracted as bracketed refs.

    Tesseract OCR renders e.g. EMC² as _EMC_[2] — it marks the word as italic
    and converts the superscript to a bracketed citation.  This pass detects the
    pattern and replaces it with the Unicode superscript character:
        _EMC_[2]  →  EMC²
    Only fires for single-digit brackets (1–9) to avoid touching real multi-digit
    citation references like [12] or [2016].
    """
    return _OCR_SUPERSCRIPT_RE.sub(
        lambda m: m.group(1) + m.group(2).translate(_SUPERSCRIPT_DIGITS),
        md,
    )


def _format_figure_captions(md: str) -> str:
    """Convert bold-formatted figure caption lines to italic captions below images.

    pymupdf4llm emits figure captions as bold text, e.g.:
        **Figure 1.1:** What is this Thesis about?

    This converts them to italic caption lines:
        *Figure 1.1: What is this Thesis about?*

    When the caption already follows an image link it stays in place; when it
    is separated from the preceding image by blank lines, those blank lines
    are collapsed so the caption sits directly below its image.
    """
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        cm = _CAPTION_RE.match(line)
        if cm:
            label = cm.group(1).rstrip(":")
            text = cm.group(2).strip()
            caption_line = f"*{label}: {text}*" if text else f"*{label}*"
            # If the last non-blank line already ended with an image link, keep
            # the caption immediately after it without an extra blank line.
            last_content = next(
                (out[j] for j in range(len(out) - 1, -1, -1) if out[j].strip()),
                "",
            )
            if last_content.startswith("!["):
                # Remove any trailing blank lines between image and caption
                while out and out[-1].strip() == "":
                    out.pop()
            out.append(caption_line)
        else:
            out.append(line)
        i += 1
    return "\n".join(out)


def _merge_split_headings(md: str) -> str:
    """Merge section-number headings split across two consecutive heading lines.

    pymupdf4llm outputs the section number and its title as separate spans
    at the same font size, producing two heading lines at the same level:
        ### 1.1
        ### Motivation - Is it just a wish?
    This merges them into one:
        ### 1.1 Motivation - Is it just a wish?
    Only merges when the first heading contains nothing but a bare section
    number (e.g. "2.3" or "1.1.1") and the next heading is at the same level.
    """
    lines = md.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m and _BARE_NUM_RE.match(m.group(2).strip()):
            hashes, num = m.group(1), m.group(2).strip()
            # Look ahead past blank lines for the next heading at the same level.
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
    """Remove bold/italic markers from inside heading lines.

    pymupdf4llm emits lines like '## **Section Title**' when the heading text
    is also bold in the PDF.  Markdown headings are already visually distinct
    (larger, heavier) so the bold wrapper is redundant and looks wrong in
    rendered output.  This pass converts '## **text**' → '## text'.
    """
    def _strip_markers(m: re.Match) -> str:
        hashes = m.group(1)
        content = m.group(2)
        content = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", content)
        content = re.sub(r"_{1,2}(.+?)_{1,2}", r"\1", content)
        return f"{hashes} {content.strip()}"

    return re.sub(r"^(#{1,6}) (.+)$", _strip_markers, md, flags=re.MULTILINE)


def normalize_heading_levels(md: str) -> str:
    """Re-assign Markdown heading levels based on section-number patterns.

    pymupdf4llm often collapses all headings to the same level (##).
    This pass detects numbered patterns such as "1.1 Title" or "1.1.1 Title"
    and promotes/demotes the heading markers accordingly.
    Only headings whose text matches a recognised numbering pattern are changed;
    unnumbered headings are left untouched.
    """
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


def clean_page(md: str) -> str:
    """Clean a single page's Markdown before pages are joined.

    Removes PDF visual artifacts (decorative horizontal rules, code-fence
    wrappers) and normalises heading levels.  Called per-page so that the
    page-break separators added afterwards are not affected.
    """
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    # Strip figure-ref instruction text that some models copy verbatim from the prompt.
    md = _FIGURE_INSTRUCTION_RE.sub("", md)

    # LLMs sometimes wrap their entire response in ```markdown ... ```.
    md = re.sub(r"```markdown\n(.*?)```", lambda m: m.group(1), md, flags=re.DOTALL)

    # Remove horizontal rules that appear immediately after a heading — these are
    # PDF decorative underlines extracted as artifacts, not intentional separators.
    md = re.sub(r"(^#{1,6} .+\n)\n*([ \t]*(-{3,}|\*{3,}|_{3,})[ \t]*\n)", r"\1\n", md, flags=re.MULTILINE)

    md = _strip_running_headers(md)
    md = _unwrap_symbol_italics(md)
    md = _fix_ocr_superscripts(md)
    md = _format_figure_captions(md)
    md = _reorder_captions_after_images(md)
    md = _merge_split_headings(md)
    md = _strip_bold_from_headings(md)
    md = normalize_heading_levels(md)
    md = _demote_outline_chapter_refs(md)
    md = _demote_unlabeled_single_word_headings(md)

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip()


def postprocess_markdown(md: str) -> str:
    """Final cleanup applied to the fully joined Markdown document."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip() + "\n"
