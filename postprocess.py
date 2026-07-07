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

# Matches a label-only italic caption with no descriptive text, e.g. "*Figure 1:*"
# or "*Abb. 2:*". These carry no information and should be removed.
_EMPTY_ITALIC_CAPTION_RE = re.compile(
    r"^\*((?:Figure|Fig\.|Abb\.|Abbildung|Table|Tabelle)\s+[\d.]+):?\*$",
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

# Greek letter → LaTeX command mapping.
# pymupdf4llm renders math variables that use a Greek font as italic Markdown
# spans (e.g. `_φ_`, `_φj_`).  Greek letters are never intentionally italic
# in academic prose, so these can be converted safely to inline LaTeX.
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

# Matches a Markdown italic span containing only letters and digits.
# Only fired when the span contains at least one Greek character (checked inside
# the replacement function).  Skipped inside fenced code blocks.
_GREEK_ITALIC_RE = re.compile(r"_([A-Za-zΑ-ω\d]+)_")

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
    "foundations", "implementation", "requirements", "architecture",
    "design", "approach", "experiments", "analysis", "related",
    # German
    "einleitung", "zusammenfassung", "schluss", "literatur", "anhang",
    "vorwort", "danksagung", "inhaltsverzeichnis", "hintergrund",
    "bewertung", "ergebnis", "ausblick", "fazit", "abstrakt",
    "grundlagen", "implementierung", "anforderungen", "entwurf",
})

# Matches dot-leader patterns in TOC table cells, e.g. " . . . . . . . . 32 "
# at the end of a cell.  Group 1 = the page number.
_DOT_LEADER_RE = re.compile(r"\s*\.(?:\s*\.)+\s*(\d+)\s*$")

# ── Front-matter table detection ─────────────────────────────────────────────

# Table whose header cell is "Contents" or "Inhaltsverzeichnis" — either a
# single-cell row (| Contents |) or with one empty trailing cell (| Inhaltsverzeichnis |  |).
_TOC_CONTENTS_HEADER_RE = re.compile(
    r"^\|\s*(Contents|Inhaltsverzeichnis)\s*\|(\s*\|)?\s*$", re.IGNORECASE
)

# TOC table whose header cell is "Seite" (page number first, title second).
_TOC_SEITE_HEADER_RE = re.compile(
    r"^\|\s*Seite\s*\|(\s*\|)?\s*$", re.IGNORECASE
)

# TOC continuation table with Chapter/Section/Page column headers.
_TOC_CHAPTER_HEADER_RE = re.compile(
    r"^\|\s*(?:Kapitel|Chapter)\s*\|\s*(?:Abschnitt|Section)\s*\|\s*(?:Seite|Page)\s*\|\s*$",
    re.IGNORECASE,
)

# Generic Markdown pipe-table separator row (only dashes, colons, spaces, pipes).
_TABLE_SEPARATOR_RE = re.compile(r"^\|[\s\-:]+(?:\|[\s\-:]+)+\|$")

# Single-header listing/figure tables that begin a front-matter list page.
# Matches both the 1-column form "| List of Figures |" and the 2-column VLM
# form "| List of Figures |  |".
_LISTING_PAGE_HEADER_RE = re.compile(
    r"^\|\s*(List of Figures|Abbildungsverzeichnis|List of Tables|Tabellenverzeichnis|Listings|Quellcodeverzeichnis)\s*\|(?:\s*\|)?\s*$", re.IGNORECASE
)

# Matches a figure-number token like "1.1" or "4.10".
_FIG_NUM_RE = re.compile(r"^(\d+\.\d+)\s*(.*)", re.DOTALL)
# Matches a plain integer page number.
_PAGE_NUM_ONLY_RE = re.compile(r"^\d+$")
# Matches a line that is entirely dots/spaces (dot-leader continuation line).
_DOT_LEADER_LINE_RE = re.compile(r"^[\s.]+$")

# Two-column "Table | Description" list-of-tables header (missing Page column).
_TABLE_LIST_HEADER_2COL_RE = re.compile(
    r"^\|\s*(?:Table|Tabelle)\s*\|\s*(?:Description|Beschreibung)\s*\|\s*$",
    re.IGNORECASE,
)

# A pipe-table cell that consists entirely of dots — dot-leader debris from
# the Listings page where each dot became a separate column.
_DOTS_CELL_RE = re.compile(r"^\.+$")

# Abbreviation inline pattern: one **ABBR** definition pair within a longer line.
# Captures (abbreviation, definition) — definition ends before the next **ABBR**
# or at end of string.
_ABBR_INLINE_RE = re.compile(
    r"\*\*([A-Z][A-Z0-9]{1,})\*\*\s+([^*]+?)(?=\s+\*\*[A-Z]|\s*$)"
)

# Bold label with a space before the colon, e.g. **Schmitt, Steven :** → **Schmitt, Steven:**
_BOLD_SPACE_COLON_RE = re.compile(r"\*\*([^*]+?)\s+:\*\*")

# Standalone declaration heading line — the VLM sometimes outputs this as plain text.
_DECLARATION_LINE_RE = re.compile(
    r"^(Erklärung(?:\s*/\s*Declaration)?|Declaration)\s*$",
    re.MULTILINE | re.IGNORECASE,
)

# Bold front-matter section title that should be a heading, e.g. **Listings** or
# **List of Figures** when it appears as a standalone line (the VLM sometimes outputs
# these as bold text rather than pipe-table headers).
_BOLD_LISTING_TITLE_RE = re.compile(
    r"^\*\*(List of Figures|Abbildungsverzeichnis|List of Tables|Tabellenverzeichnis|Listings|Quellcodeverzeichnis)\*\*\s*$", re.IGNORECASE | re.MULTILINE
)

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


def _clean_toc_dot_leaders(md: str) -> str:
    """Strip dot leaders from TOC table cells and recover embedded page numbers.

    TOC tables from pymupdf4llm often embed dot leaders inside cells:
        | 1.1 Motivation . . . . . . . . . . . . . . . . 1 | 1 |
        | 6.4 Results . . . . . . . . . . . . . . . . . 32 |   |

    This strips the ". . . ." pattern and, when the page number was absorbed
    into the title cell leaving the second cell empty, moves it there:
        | 1.1 Motivation | 1 |
        | 6.4 Results | 32 |
    """
    lines = md.split("\n")
    result = []
    for line in lines:
        if not line.startswith("|"):
            result.append(line)
            continue
        cells = line.split("|")
        # cells[0] = '' before first |, cells[-1] = '' after last |
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
                # If the adjacent page-number cell is empty, fill it in.
                if j + 1 < len(inner) and not inner[j + 1].strip():
                    inner[j + 1] = f" {page_num} "
                changed = True
        if changed:
            line = "|" + "|".join(inner) + "|"
        result.append(line)
    return "\n".join(result)


def _toc_2col_entry(entry: str, page: str) -> str:
    """Format a single 2-col TOC row as a nested list item."""
    if re.match(r"^\d+\.\d+\.\d+\s", entry):
        return f"    - {entry} {page}"
    if re.match(r"^\d+\.\d+\s", entry):
        return f"  - {entry} {page}"
    return f"- **{entry}** {page}"


def _toc_3col_entry(col1_raw: str, col2: str, col3: str) -> str:
    """Format a single 3-col Chapter/Section/Page row as a nested list item."""
    col1 = col1_raw.strip()
    if col1:
        if col1[0].isdigit():
            return f"- **{col1} {col2}** {col3}"
        # Front matter or appendix (e.g. "Bibliography", "Appendix A").
        title = f"{col1} {col2}".strip() if col2 else col1
        return f"- **{title}** {col3}"
    # Empty chapter column — depth from leading whitespace in the raw cell.
    n = len(col1_raw) - len(col1_raw.lstrip())
    if n >= 5:
        return f"    - {col2} {col3}"
    return f"  - {col2} {col3}"


def _convert_toc_table(md: str) -> str:
    """Convert TOC pipe-tables to a nested Markdown list.

    Handles two formats pymupdf4llm produces:
    • 2-column ("| Contents |" header): rows are "| entry | page |".
    • 3-column ("| Chapter | Section | Page |" header): rows encode depth
      via the number of leading spaces in the Chapter cell.
    """
    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        # ── 2-column TOC ─────────────────────────────────────────────────────
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

        # ── 2-column TOC with "| Seite |" header (page first, title second) ────
        if _TOC_SEITE_HEADER_RE.match(stripped):
            items = []
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
                    page = cells[1].strip()
                    entry = cells[2].strip()
                    if entry:
                        items.append(_toc_2col_entry(entry, page))
                i += 1
            result.append("## Contents")
            result.append("")
            result.extend(items)
            continue

        # ── 3-column TOC continuation ─────────────────────────────────────────
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
    """Convert an inline bold abbreviation list to a two-column pipe table.

    pymupdf4llm renders List of Abbreviations pages with all entries on one
    line:  **AI** artificial intelligence **API** application...

    Detects ≥3 such pairs and emits a proper Markdown table instead.
    """
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
    """Split 'N.N Description text' into ('N.N', 'Description text')."""
    m = re.match(r"^(\d+\.\d+(?:\.\d+)?)\s+(.+)$", entry)
    if m:
        return m.group(1), m.group(2)
    return "", entry


def _parse_lof_entries(raw_text: str) -> list[tuple[str, str, str]]:
    """Parse (figure_num, description, page) triples from raw fitz page text.

    Handles two layouts emitted by fitz for List of Figures pages:
    • Separate lines:  "1.1\\nSix-phase pipeline . . .\\n2"
    • Combined line:   "4.10 Experimentation flow . . .\\n31"
      (sometimes with a trailing dot-leader line before the page number)
    """
    lines = [ln.strip() for ln in raw_text.split("\n")]

    # Find the "List of Figures" header line.
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
            break  # left the List of Figures block

        num = m.group(1)
        rest = m.group(2).strip()

        if rest:
            # Number and description on the same fitz line.
            desc = re.sub(r"\s*\.+\s*", " ", rest).strip().rstrip(".")
            # Peek: next non-empty line may be a dot-leader continuation or page.
            j = i + 1
            while j < len(lines) and not lines[j]:
                j += 1
            page = ""
            if j < len(lines):
                if _PAGE_NUM_ONLY_RE.match(lines[j]):
                    page = lines[j]
                    i = j + 1
                elif _DOT_LEADER_LINE_RE.match(lines[j]):
                    # Skip the dot-leader continuation and grab the page.
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
            # Number alone on its own fitz line.
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
                    # Dot-leader continuation after description — skip it.
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
    """Rebuild a List of Figures table to include the figure numbers.

    VLMs often produce a 2-column table (description | page) with the figure
    number column missing.  This pass detects that and rebuilds the section as
    a proper 3-column table using the figure numbers parsed from raw fitz text.
    """
    if not raw_page_text or not re.search(r'List of Figures|Abbildungsverzeichnis', raw_page_text, re.IGNORECASE):
        return md

    entries = _parse_lof_entries(raw_page_text)
    if not entries:
        return md

    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        is_lof = re.match(r"^\|\s*(List of Figures|Abbildungsverzeichnis)\s*\|", stripped, re.IGNORECASE) or re.match(
            r"^#{1,3}\s*(List of Figures|Abbildungsverzeichnis)\s*$", stripped, re.IGNORECASE
        )
        if is_lof:
            # Consume the rest of the section (table rows and blank separators).
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    # Blank line — stop unless the next non-blank is still a table row.
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

            # Emit the rebuilt 3-column table.
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
    """Convert single-header figure/listing tables to clean 3-column tables.

    pymupdf4llm renders List of Figures, List of Tables, and Listings pages
    with a single-cell heading row and 2-column data rows where the item
    number and description are merged.  The Listings page also has dot-leader
    debris where each dot became a separate column.

    Both formats are normalised to:
        ## List of Figures
        | Figure | Description | Page |
        |---|---|---|
        | 1.1 | Six-phase research pipeline | 2 |
    """
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
                # Last non-dot cell is the page number if it is a short
                # alphanumeric token distinct from the entry text.
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
    """Fix a 'Table | Description' header that is missing the Page column.

    The List of Tables page is sometimes extracted with a 2-column header
    while data rows already carry an (empty) third column for page numbers.
    This corrects the header and adds a '## List of Tables' heading when
    none precedes the table.
    """
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
    """Convert wrongly-promoted bold labels to bold text.

    pymupdf4llm's layout parser promotes bold body-size text to headings.
    A heading is demoted when it (and has no leading section number):
      - is a single word that is not a recognised structural keyword
      - ends with ' :' (citation/author label, e.g. "Köhler, Sven :")
      - exceeds 80 characters (repeated thesis title in abstract, not a section)

    Numbered headings (starting with digits) are always kept.
    """
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


def _fix_bold_space_before_colon(md: str) -> str:
    """Remove the space before the colon in bold author/label lines.

    PDFs sometimes store citation labels as 'Schmitt, Steven :' with a space
    before the colon.  pymupdf4llm preserves it, producing **Schmitt, Steven :**
    which looks wrong in Markdown.  This normalises them to **Schmitt, Steven:**.
    """
    return _BOLD_SPACE_COLON_RE.sub(r"**\1:**", md)


def _fix_bold_listing_headings(md: str) -> str:
    """Convert bold front-matter section titles to proper Markdown headings.

    The VLM sometimes outputs 'List of Figures', 'List of Tables' or 'Listings'
    as **bold text** on a standalone line instead of as a pipe-table header row.
    This converts those to ## headings so the section is formatted consistently.
    """
    return _BOLD_LISTING_TITLE_RE.sub(lambda m: f"## {m.group(1)}", md)


def _promote_declaration_heading(md: str) -> str:
    """Promote a standalone 'Erklärung / Declaration' line to a ## heading.

    The declaration page is classified as MIXED (it contains a signature image),
    so it goes to the VLM.  The VLM sometimes outputs the page title as plain
    text instead of a heading.  This converts the standalone line to ## so the
    section appears correctly in the document hierarchy.
    """
    return _DECLARATION_LINE_RE.sub(lambda m: f"## {m.group(1)}", md)


def _unwrap_symbol_italics(md: str) -> str:
    """Strip italic/bold markers wrapping a single non-word Unicode symbol.

    pymupdf4llm wraps arrow characters in underscore italic because the glyph
    uses an italic font variant in the PDF, e.g. ``_⇒_``.  Most Markdown
    renderers do not apply italic styling to non-alphabetic characters and
    leave the underscores as literal text, which looks wrong.  This pass
    removes those markers so ``_⇒_`` becomes ``⇒``.
    """
    return _SYMBOL_ITALIC_RE.sub(lambda m: m.group(1) or m.group(2), md)


def _convert_greek_italic_math(md: str) -> str:
    """Convert italic Greek letter spans to inline LaTeX.

    pymupdf4llm renders math variables that use a Greek italic font as
    Markdown italic spans, e.g. ``_φj_`` or ``_Δt_``.  Greek letters never
    appear as intentional italic prose, so these can be converted to
    ``$\\varphi_j$`` / ``$\\Delta_t$`` safely.

    Single trailing Latin letter(s) or digit(s) after the Greek prefix are
    treated as subscripts: ``_φj_`` → ``$\\varphi_j$``.
    Content without any Greek character is left unchanged so that ordinary
    italic words like ``_result_`` are not affected.

    The pass is skipped inside fenced code blocks.
    """
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
        # Drop label-only italic captions (no descriptive text), e.g. "*Figure 1:*"
        if _EMPTY_ITALIC_CAPTION_RE.match(line):
            i += 1
            continue

        cm = _CAPTION_RE.match(line)
        if cm:
            label = cm.group(1).rstrip(":")
            text = cm.group(2).strip()
            if not text:
                i += 1
                continue  # label-only bold caption — drop it too
            caption_line = f"*{label}: {text}*"
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


def _recover_bare_number_headings(md: str, raw_text: str) -> str:
    """Patch headings that are missing either their title or their section number.

    pymupdf4llm sometimes drops the section number or the title from a heading:

    Case A — bare number, e.g. "## 2.3" with no title:
        The fitz raw text has "2.3 Neuronale Netze" → restored to "## 2.3 Neuronale Netze".

    Case B — title without number, e.g. "## Neuronale Netze":
        The fitz raw text has "2.3 Neuronale Netze" → number prepended: "## 2.3 Neuronale Netze".
        Only fires for N.N or N.N.N numbered sections (single-number chapter titles
        like "1 Einleitung" are intentionally excluded — they become # headings elsewhere).
    """
    if not raw_text:
        return md

    # Build lookup tables from fitz raw text.
    fitz_titles: dict[str, str] = {}   # number → title  (case A)
    fitz_numbers: dict[str, str] = {}  # normalised title → number  (case B)
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

    # Case A: heading is just a bare number ("## 2.3") — attach the title.
    def _patch_bare_number(m: re.Match) -> str:
        hashes, num = m.group(1), m.group(2).strip()
        title = fitz_titles.get(num)
        if title:
            return f"{hashes} {num} {title}"
        return m.group(0)

    md = re.sub(r"^(#{1,6})\s+(\d[\d.]+)[ \t]*$", _patch_bare_number, md, flags=re.MULTILINE)

    # Case B: heading has a title but no number prefix — prepend the number.
    def _patch_missing_number(m: re.Match) -> str:
        hashes, content = m.group(1), m.group(2).strip()
        # Skip if the heading already starts with a number.
        if re.match(r"^\d", content):
            return m.group(0)
        # Skip structural keywords — they are unnumbered by design.
        if content.lower() in _STRUCTURAL_KEYWORDS:
            return m.group(0)
        num = fitz_numbers.get(content.lower())
        if num:
            return f"{hashes} {num} {content}"
        return m.group(0)

    return re.sub(r"^(#{2,6})\s+(\S[^\n]*)$", _patch_missing_number, md, flags=re.MULTILINE)


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
    """Remove redundant bold markers from heading lines, preserving italic.

    pymupdf4llm emits lines like '## **Section Title**' when the heading text
    is bold in the PDF — redundant because headings are already visually bold.
    Bold-italic content like '## _**Bag of Words**_' should keep the italic
    marker so the formatting intent is preserved: → '## _Bag of Words_'.

    Rules:
      ***text*** → _text_   (bold-italic: drop bold, keep italic)
      **text**   → text     (plain bold: drop entirely)
      __text__   → text     (plain bold with underscores: drop entirely)
      _text_ and *text* are left untouched (they carry italic meaning).
    """
    def _strip_markers(m: re.Match) -> str:
        hashes = m.group(1)
        content = m.group(2)
        content = re.sub(r"\*\*\*(.+?)\*\*\*", r"_\1_", content)
        content = re.sub(r"\*\*(.+?)\*\*", r"\1", content)
        content = re.sub(r"__(.+?)__", r"\1", content)
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


def clean_page(md: str, raw_page_text: str = "") -> str:
    """Clean a single page's Markdown before pages are joined.

    Removes PDF visual artifacts (decorative horizontal rules, code-fence
    wrappers) and normalises heading levels.  Called per-page so that the
    page-break separators added afterwards are not affected.

    `raw_page_text` is the plain text from fitz for the same page.  When
    provided, bare section-number headings whose title was dropped by
    pymupdf4llm are patched by looking up the number in the fitz text.
    """
    md = md.replace("\r\n", "\n").replace("\r", "\n")

    # Strip figure-ref instruction text that some models copy verbatim from the prompt.
    md = _FIGURE_INSTRUCTION_RE.sub("", md)

    # LLMs sometimes wrap their entire response in ```markdown ... ```.
    md = re.sub(r"```markdown\n(.*?)```", lambda m: m.group(1), md, flags=re.DOTALL)

    # Remove horizontal rules that appear immediately after a heading — these are
    # PDF decorative underlines extracted as artifacts, not intentional separators.
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

# Heading whose entire content is a single italic span — almost always a
# styled subtitle or repeated title, not a real section heading.
_FULLY_ITALIC_HEADING_RE = re.compile(
    r"^#{1,6}\s+(_[^_\n]+_)\s*$", re.MULTILINE
)

# Heading that is really a numbered source-code line: "## 11 `return ...`"
# pymupdf4llm misidentifies the line number as a section number.
_CODE_LISTING_HEADING_RE = re.compile(
    r"^#{1,6}\s+(\d+\s+`[^`\n]+`)\s*$", re.MULTILINE
)

# OCR text block extracted from a figure image, wrapped in marker lines.
_PICTURE_TEXT_BLOCK_RE = re.compile(
    r"\*\*----- Start of picture text -----\*\*<br>\n(.*?)"
    r"\*\*----- End of picture text -----\*\*<br>",
    re.DOTALL,
)


def _demote_italic_headings(md: str) -> str:
    """Demote headings whose entire content is italic to plain italic text.

    pymupdf4llm promotes styled subtitle lines (e.g. the paper title repeated
    in italic below '## Abstract') to headings.  A heading like
        ## _A System for Research Paper Generation_
    should be body text, not a section heading.
    """
    return _FULLY_ITALIC_HEADING_RE.sub(r"\1", md)


def _demote_code_listing_headings(md: str) -> str:
    """Demote numbered source-code lines misidentified as section headings.

    pymupdf4llm sometimes promotes a code listing line like
        ## 11 `return ''.join(parts)`
    to a heading because the line number looks like a section number.
    These are converted back to list items to match adjacent listing lines:
        - 11 `return ''.join(parts)`
    """
    return _CODE_LISTING_HEADING_RE.sub(r"- \1", md)


def _clean_picture_text_blocks(md: str) -> str:
    """Remove picture-text blocks produced by pymupdf4llm's Tesseract OCR pass.

    pymupdf4llm runs Tesseract on embedded figure images and wraps the result in:
        **----- Start of picture text -----**<br>
        Some text<br>More text<br>
        **----- End of picture text -----**<br>
    This OCR output is inaccurate (word-wrap artefacts, symbol misreads) and
    redundant — the figure image itself is already included as a Markdown image
    link one line above.  Dropping the block avoids misleading noise.
    """
    return _PICTURE_TEXT_BLOCK_RE.sub("", md)


def _demote_title_page_headings(md: str) -> str:
    """Demote title-page metadata lines that pymupdf4llm promotes to headings.

    The title page spans from the start of the document to the first structural
    front-matter section (Erklärung, Abstrakt, Inhaltsverzeichnis, …).  Within
    that zone every H2+ heading is really a styled label — author name, date,
    institution, document type — and should be plain text, not a heading.

    The document title itself (first H1 in the zone) is kept as-is.
    """
    lines = md.split("\n")

    # Find the line index of the first structural front-matter heading.
    title_page_end = len(lines)
    for i, line in enumerate(lines):
        m = re.match(r"^#{1,6}\s+(.+)$", line)
        if m:
            title = m.group(1).strip().lower()
            if title in _FRONT_MATTER_SECTIONS:
                title_page_end = i
                break

    if title_page_end == len(lines):
        return md  # no structural section found — leave untouched

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
                result.append(line)  # keep document title
            elif level >= 2:
                content = m.group(2).strip().rstrip(": ")
                result.append(content)  # demote to plain text
            else:
                result.append(line)
        else:
            result.append(line)
    return "\n".join(result)


def _merge_kapitel_headings(md: str) -> str:
    """Merge chapter-separator headings with the chapter title.

    Handles two forms produced by the pipeline:

    H2 form (pymupdf4llm before normalize_heading_levels):
        ## Kapitel 1  +  ## Einleitung  →  # Kapitel 1: Einleitung

    H1 form (after normalize_heading_levels assigns depth=1 to Chapter lines):
        # Chapter 2  +  ## Execution plan  →  # Chapter 2: Execution plan

    The chapter word ("Chapter"/"Kapitel") and number are preserved so the
    output reads naturally as a single top-level section title.
    """
    lines = md.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        # Match H1 form first (post-normalisation).
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
        # Match H2 form (legacy / fallback).
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
    """Remove heading duplicates produced by PDF running headers.

    Two kinds of duplicates are handled:

    1. Numbered → unnumbered: the title text of a numbered ## heading was
       already seen, and a later unnumbered ## heading repeats it.
         ## 2.2 Dataset research   (real)
         ...
         ## Dataset research       (running header — drop)

    2. Exact numbered duplicate: the PDF embeds the same numbered heading
       twice on the same page (e.g. "4.3 Training…" appears in both the
       body and a sidebar), so pymupdf4llm outputs it twice.
         ## 4.3 Training…          (real — keep)
         ## 4.3 Training…          (duplicate — drop)

    3. # Kapitel N Title running header: interior pages of a chapter carry a
       combined "Kapitel N Title" header.  If the Title part was already seen
       as a standalone ## heading, the combined form is a running header.
         # Kapitel 2               (real chapter marker — keep)
         ## Theoretische Grundlagen (real section heading — keep, record title)
         ...
         # Kapitel 2 Theoretische Grundlagen  (interior page header — drop)
    """
    lines = md.split("\n")
    seen_titled_headings: set[str] = set()   # titles from numbered ## headings
    seen_all_headings: set[str] = set()       # every heading title seen
    seen_exact_numbered: set[str] = set()     # full text of numbered headings
    result: list[str] = []

    for line in lines:
        # ── numbered ## heading ──────────────────────────────────────────────
        m_numbered = re.match(r"^##\s+(\d[\d.]*\s+.+)$", line)
        if m_numbered:
            full = m_numbered.group(1).strip()
            key = full.lower()
            if key in seen_exact_numbered:
                continue  # exact duplicate numbered heading — drop
            seen_exact_numbered.add(key)
            title_part = re.sub(r"^\d[\d.]*\s+", "", full).strip().lower()
            seen_titled_headings.add(title_part)
            seen_all_headings.add(title_part)
            result.append(line)
            continue

        # ── unnumbered ## heading ─────────────────────────────────────────────
        m_unnumbered = re.match(r"^##\s+(\S[^\n]*)$", line)
        if m_unnumbered:
            title = m_unnumbered.group(1).strip().lower()
            if title in seen_titled_headings:
                continue  # unnumbered repeat of a numbered heading — drop
            seen_all_headings.add(title)
            result.append(line)
            continue

        # ── # Kapitel/Chapter N Title running header ──────────────────────────
        m_kapitel = re.match(
            r"^#\s+(?:Kapitel|Chapter)\s+\d+\s+(.+)$", line, re.IGNORECASE
        )
        if m_kapitel:
            title = m_kapitel.group(1).strip().lower()
            if title in seen_all_headings:
                continue  # already seen as a real heading — this is a repeat
            seen_all_headings.add(title)
            result.append(line)
            continue

        result.append(line)

    return "\n".join(result)


def _strip_bibliography_dash(md: str) -> str:
    """Remove em-dash artifacts in bibliography paragraphs.

    In German academic PDFs, bibliography entries use the format:
        Author, Name:
        – Title / Author. – Publisher, Year.

    The '–' is a typographic separator within the citation.  Two artefacts
    appear depending on where the PDF line break falls:

    1. Leading dash — pymupdf4llm places it at the start of the next paragraph:
           **Schmitt, Steven:**
           – Ein Human-in-the-Loop…
       → stripped.

    2. Trailing dash — the line-break falls after the authorship statement, so
       the dash ends up at the end of the citation line:
           … / Steven Schmitt. –
       → stripped.
    """
    # Leading '– ' from paragraphs that follow a bold author label.
    md = re.sub(
        r"(^\*\*[^\n]+\*\*\s*\n\n)([–—])\s+",
        r"\1",
        md,
        flags=re.MULTILINE,
    )
    # Trailing ' –' or ' —' after a sentence-ending period.
    md = re.sub(r"\.\s*[–—][ \t]*$", ".", md, flags=re.MULTILINE)
    return md


def _strip_mid_doc_page_numbers(md: str) -> str:
    """Remove lone page-footer numbers that appear mid-document.

    pymupdf4llm sometimes extracts PDF page-footer numbers as isolated
    paragraphs in the middle of the document (not just before a page-break
    separator).  A paragraph consisting solely of 1–3 digits is almost always
    a page number artefact, not body content.
    """
    # Lone Arabic number between two blank lines (middle of document).
    md = re.sub(r"\n\n\d{1,3} ?\n\n", "\n\n", md)
    # Lone Roman numeral page number (i–xiii range covers all typical front-matter).
    md = re.sub(r"\n\n[ivxIVX]{1,8} ?\n\n", "\n\n", md)
    return md


def _strip_mid_doc_running_headers(md: str) -> str:
    """Remove plain-text running headers that appear mid-document.

    PDF page headers (Kopfzeilen) repeat the current chapter or section title
    at the top of every page.  pymupdf4llm extracts these as standalone plain-
    text paragraphs, e.g. "Kapitel 2 Theoretische Grundlagen" or "4.1 Setup".
    They are surrounded by blank lines and carry no new information.
    """
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
    """Unify LaTeX math delimiters to the $ / $$ style.

    pymupdf4llm and some LLMs output inline math as \\(...\\) and display math
    as \\[...\\].  Normalise these to the dollar-sign style used everywhere else
    in the document so renderers don't need to support both conventions.
        \\( expr \\)  →  $expr$
        \\[ expr \\]  →  $$expr$$
    """
    # Display math first (so \\[ isn't accidentally matched by the inline rule).
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

    # Remove PDF page-footer numbers before page-break separators or at end.
    md = re.sub(r"\n\n(\d{1,3})\n\n---", "\n\n---", md)
    md = re.sub(r"\n\n(\d{1,3})\s*$", "", md)

    while "\n\n\n" in md:
        md = md.replace("\n\n\n", "\n\n")

    return md.strip() + "\n"
