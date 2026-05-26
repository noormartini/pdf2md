import re

# Matches numbered heading text inside any Markdown heading line.
# Groups: (hashes, optional bold markers, heading text content)
_HEADING_RE = re.compile(r"^(#{1,6})\s+(\*{0,2})(.+?)(\*{0,2})\s*$")

# Patterns for detecting heading depth from section numbers.
_SUBSECTION_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\s+\S")  # e.g. "1.1.1 Title"
_SECTION_RE    = re.compile(r"^\d{1,3}\.\d{1,3}\s+\S")           # e.g. "1.1 Title"
_CHAPTER_RE    = re.compile(r"^(?:Kapitel|Chapter|Abschnitt|Section)\s+\d+\b", re.IGNORECASE)
_TOP_NUM_RE    = re.compile(r"^\d+\.\s")           # e.g. "1. Introduction"


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

    # LLMs sometimes wrap their entire response in ```markdown ... ```.
    md = re.sub(r"```markdown\n(.*?)```", lambda m: m.group(1), md, flags=re.DOTALL)

    # Remove horizontal rules that appear immediately after a heading — these are
    # PDF decorative underlines extracted as artifacts, not intentional separators.
    md = re.sub(r"(^#{1,6} .+\n)\n*([ \t]*(-{3,}|\*{3,}|_{3,})[ \t]*\n)", r"\1\n", md, flags=re.MULTILINE)

    md = normalize_heading_levels(md)

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip()


def postprocess_markdown(md: str) -> str:
    """Final cleanup applied to the fully joined Markdown document."""
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip() + "\n"
