from postprocess import (
    clean_page,
    postprocess_markdown,
    _clean_toc_dot_leaders,
    _demote_outline_chapter_refs,
    _demote_unlabeled_single_word_headings,
    _format_figure_captions,
    _fix_ocr_superscripts,
    _normalise_latex_delimiters,
    _reorder_captions_after_images,
    _recover_bare_number_headings,
    _strip_bibliography_dash,
    _strip_bold_from_headings,
    _strip_duplicate_section_headers,
    _strip_running_headers,
    _unwrap_symbol_italics,
)


def test_clean_page_strips_figure_instruction_preamble():
    md = (
        "# Dataset research\n\n"
        "The following figures have been extracted from this page and saved as files. "
        "Include them as Markdown image links at the appropriate locations in your output:\n"
        "- ![](figures/page_015_fig_001.png)\n"
        "- ![](figures/page_015_fig_002.png)\n\n"
        "**Figure 2.1:** content here\n\n"
        "![](figures/page_015_fig_001.png)"
    )
    result = clean_page(md)
    assert "The following figures have been extracted" not in result
    assert "Include them as Markdown image links" not in result
    # figure links that appear naturally in the output are kept
    assert "figures/page_015_fig_001.png" in result
    # Bold figure captions are converted to italic captions
    assert "*Figure 2.1: content here*" in result


def test_clean_page_leaves_output_without_instruction_untouched():
    md = "## 1.1 Section Title\n\nSome paragraph text.\n\n![](figures/fig.png)"
    assert clean_page(md) == md


def test_format_figure_captions_bold_after_image():
    md = "![Figure 1](figures/page_009_fig_001.png)\n\n**Figure 1.1:** What is this Thesis about?"
    result = _format_figure_captions(md)
    # blank lines between image and caption removed; caption italicised
    assert result == "![Figure 1](figures/page_009_fig_001.png)\n*Figure 1.1: What is this Thesis about?*"


def test_format_figure_captions_standalone_bold_caption():
    md = "Some text.\n\n**Figure 2.3:** Description here.\n\nMore text."
    result = _format_figure_captions(md)
    assert "*Figure 2.3: Description here.*" in result
    assert "**Figure 2.3:**" not in result


def test_format_figure_captions_already_italic_untouched():
    md = "![img](figures/fig.png)\n*Figure 1.1: caption*"
    assert _format_figure_captions(md) == md


def test_format_figure_captions_german_abb():
    md = "![img](figures/fig.png)\n**Abb. 2.1:** Ergebnis der Analyse"
    result = _format_figure_captions(md)
    assert "*Abb. 2.1: Ergebnis der Analyse*" in result


def test_fix_ocr_superscripts_emc2():
    assert _fix_ocr_superscripts("According to _EMC_[2] 1,7 MB") == "According to EMC² 1,7 MB"


def test_fix_ocr_superscripts_multi_digit_citation_unchanged():
    assert _fix_ocr_superscripts("cited by [2016]") == "cited by [2016]"
    assert _fix_ocr_superscripts("Smith et al. [12]") == "Smith et al. [12]"


def test_fix_ocr_superscripts_nasa():
    assert _fix_ocr_superscripts("_NASA_[3]") == "NASA³"


def test_clean_page_fixes_emc2_superscript():
    md = "According to _EMC_[2] 1,7 MB of new data is created every day."
    result = clean_page(md)
    assert "EMC²" in result
    assert "_EMC_[2]" not in result


def test_unwrap_symbol_italics_arrow():
    assert _unwrap_symbol_italics("- _⇒_ Develop an operational service") == "- ⇒ Develop an operational service"


def test_unwrap_symbol_italics_bold_arrow():
    assert _unwrap_symbol_italics("**→** text") == "→ text"


def test_unwrap_symbol_italics_leaves_word_italic():
    assert _unwrap_symbol_italics("_hello_") == "_hello_"
    assert _unwrap_symbol_italics("**bold**") == "**bold**"


def test_clean_page_unwraps_arrow_sub_bullets():
    md = "- S (specific)\n\n   - _⇒_ Develop an operational service."
    result = clean_page(md)
    assert "⇒" in result
    assert "_⇒_" not in result


def test_strip_running_headers_chapter():
    md = "1 Introduction \n\nWhy is it nowadays so important..."
    result = _strip_running_headers(md)
    assert "1 Introduction" not in result
    assert "Why is it nowadays" in result


def test_strip_running_headers_section():
    md = "2.2 Dataset research \n\nobtained by memorizing movie-unique terms..."
    result = _strip_running_headers(md)
    assert "2.2 Dataset research" not in result
    assert "obtained by memorizing" in result


def test_strip_running_headers_leaves_real_heading():
    md = "## **Chapter 1** \n\n## **Introduction**"
    assert _strip_running_headers(md) == md


def test_strip_running_headers_leaves_prose():
    md = "Some paragraph text starting here."
    assert _strip_running_headers(md) == md


def test_strip_running_headers_leaves_list():
    md = "- bullet item\n- another"
    assert _strip_running_headers(md) == md


def test_clean_page_removes_running_header():
    md = "2 Execution plan \n\numents which are ironically or slang based texts..."
    result = clean_page(md)
    assert "2 Execution plan" not in result
    assert "uments which are" in result


def test_reorder_captions_italic_before_image():
    md = "*Figure 1.1: What is this Thesis about?*\n\n![Figure 1](figures/page_009_fig_001.png)"
    result = _reorder_captions_after_images(md)
    assert result.index("![") < result.index("*")
    assert "Figure 1.1" in result


def test_reorder_captions_correct_order_unchanged():
    md = "![Figure 1](figures/img.png)\n*Figure 1.1: caption*"
    assert _reorder_captions_after_images(md) == md


def test_clean_page_swaps_bold_caption_before_image():
    md = "**Figure 2.1:** Some chart\n\n![Figure 2](figures/fig2.png)"
    result = clean_page(md)
    assert result.index("![") < result.index("*")
    assert "Figure 2.1" in result


def test_reorder_captions_german_abb_before_image():
    md = "*Abb. 3.1: Ergebnis*\n\n![Figure 3](figures/fig3.png)"
    result = _reorder_captions_after_images(md)
    assert result.index("![") < result.index("*")


def test_demote_outline_chapter_refs_converts_to_bold():
    md = "## Chapter 1 - Introduction\n\nSome description."
    result = _demote_outline_chapter_refs(md)
    assert result == "**Chapter 1 - Introduction**\n\nSome description."


def test_demote_outline_chapter_refs_german():
    md = "## Kapitel 2 – Ausführungsplan\n\nBeschreibung."
    result = _demote_outline_chapter_refs(md)
    assert "**Kapitel 2 – Ausführungsplan**" in result
    assert "##" not in result


def test_demote_outline_chapter_refs_leaves_real_chapter_heading():
    # No dash → real chapter heading, must NOT be demoted
    md = "## Chapter 2\n\n## Execution plan"
    result = _demote_outline_chapter_refs(md)
    assert result == md


def test_clean_page_outline_chapters_are_bold_not_headings():
    md = "## **1.2 Outline of this document**\n\n## **Chapter 1 - Introduction**\n\nDescription."
    result = clean_page(md)
    assert "**Chapter 1 - Introduction**" in result
    assert "# Chapter 1" not in result
    assert "## 1.2 Outline" in result


def test_demote_unlabeled_single_word_headings_company():
    assert _demote_unlabeled_single_word_headings("## Company") == "**Company**"


def test_demote_unlabeled_single_word_headings_department():
    assert _demote_unlabeled_single_word_headings("## Department") == "**Department**"


def test_demote_unlabeled_single_word_headings_german():
    assert _demote_unlabeled_single_word_headings("## Hochschule") == "**Hochschule**"


def test_demote_unlabeled_single_word_headings_keyword_kept():
    assert _demote_unlabeled_single_word_headings("## Introduction") == "## Introduction"
    assert _demote_unlabeled_single_word_headings("## Conclusion") == "## Conclusion"
    assert _demote_unlabeled_single_word_headings("## Abstract") == "## Abstract"


def test_demote_unlabeled_single_word_headings_numbered_kept():
    assert _demote_unlabeled_single_word_headings("## 1.3 Surrounding") == "## 1.3 Surrounding"
    assert _demote_unlabeled_single_word_headings("## 2.1 Research") == "## 2.1 Research"


def test_demote_unlabeled_single_word_headings_multi_word_kept():
    assert _demote_unlabeled_single_word_headings("## Research Questions") == "## Research Questions"


def test_demote_unlabeled_single_word_headings_deep_level():
    assert _demote_unlabeled_single_word_headings("#### Company") == "**Company**"


def test_demote_unlabeled_single_word_headings_citation_label():
    assert _demote_unlabeled_single_word_headings("## Köhler, Sven :") == "**Köhler, Sven :**"


def test_demote_unlabeled_single_word_headings_citation_label_no_space_kept():
    # Only the ' :' (space-colon) pattern is a citation label; plain ':' is kept
    assert _demote_unlabeled_single_word_headings("## Some Section:") == "## Some Section:"


def test_demote_unlabeled_single_word_headings_long_title():
    long_title = "Influence of Hyper-Parameter and pipeline tuning for supervised machine classification"
    assert len(long_title) > 80
    assert _demote_unlabeled_single_word_headings(f"## {long_title}") == f"**{long_title}**"


def test_demote_unlabeled_single_word_headings_long_numbered_kept():
    long_numbered = "2.3.4 Tensorflow as ML Framework for deep learning classification tasks and pipelines"
    assert _demote_unlabeled_single_word_headings(f"## {long_numbered}") == f"## {long_numbered}"


def test_clean_page_demotes_bold_label_headings():
    md = "## Company\n\nAcme Corp\n\n## Department\n\nEngineering"
    result = clean_page(md)
    assert "**Company**" in result
    assert "**Department**" in result
    assert "## Company" not in result
    assert "## Department" not in result


def test_strip_duplicate_section_headers_removes_unnumbered_repeat():
    md = "## 2.2 Dataset research\n\nSome content.\n\n---\n\n## Dataset research\n\nMore content."
    result = _strip_duplicate_section_headers(md)
    assert "## 2.2 Dataset research" in result
    assert result.count("## Dataset research") == 0
    assert "More content." in result


def test_strip_duplicate_section_headers_keeps_first_occurrence():
    # Unnumbered heading with no prior numbered counterpart must be kept.
    md = "## Execution plan\n\nSome content."
    result = _strip_duplicate_section_headers(md)
    assert "## Execution plan" in result


def test_strip_duplicate_section_headers_case_insensitive():
    md = "## 2.2 Dataset Research\n\nContent.\n\n## Dataset research\n\nMore."
    result = _strip_duplicate_section_headers(md)
    assert "## 2.2 Dataset Research" in result   # numbered version kept
    assert "## Dataset research" not in result    # unnumbered duplicate removed


def test_strip_duplicate_section_headers_keeps_different_title():
    md = "## 2.2 Dataset research\n\nContent.\n\n## Prototyping\n\nMore."
    result = _strip_duplicate_section_headers(md)
    assert "## Prototyping" in result


def test_postprocess_markdown_strips_duplicate_running_headers():
    page1 = "<!-- Page 6 -->\n\n## 2.2 Dataset research\n\nFirst page content."
    page2 = "<!-- Page 7 -->\n\n## Dataset research\n\nSecond page content."
    md = f"{page1}\n\n---\n\n{page2}"
    result = postprocess_markdown(md)
    assert "## 2.2 Dataset research" in result
    assert result.count("## Dataset research") == 0
    assert "Second page content." in result


def test_clean_toc_dot_leaders_strips_dots_from_cell():
    md = "| 1.1 Motivation . . . . . . . . . . . . 1 | 1 |\n"
    result = _clean_toc_dot_leaders(md)
    assert "1.1 Motivation" in result
    assert ". . ." not in result


def test_clean_toc_dot_leaders_moves_page_number_to_empty_cell():
    # Page vi style: page number absorbed into title cell, second cell empty.
    md = "| 6.4 Results . . . . . . . . . . . . . . 32 |  |\n"
    result = _clean_toc_dot_leaders(md)
    assert "6.4 Results" in result
    assert ". . ." not in result
    assert "32" in result


def test_clean_toc_dot_leaders_leaves_non_table_lines_unchanged():
    md = "Some text with . . . . dots in it.\n"
    assert _clean_toc_dot_leaders(md) == md


def test_clean_toc_dot_leaders_leaves_normal_tables_unchanged():
    md = "| foo | bar |\n| --- | --- |\n| baz | qux |\n"
    assert _clean_toc_dot_leaders(md) == md


def test_clean_page_preserves_toc_table_format():
    # TOC tables should remain as tables, not be converted to text.
    md = (
        "| Inhaltsverzeichnis |  |\n"
        "| --- | --- |\n"
        "| 1 Einleitung | 1 |\n"
        "| 2 Grundlagen | 3 |\n"
    )
    result = clean_page(md)
    assert "|" in result
    assert "1 Einleitung" in result


def test_recover_bare_number_headings_patches_missing_title():
    md = "## 2.3.4\n\nTensorFlow is an open source library."
    raw = "2.3.4 Tensorflow as ML Framework\nTensorFlow is an open source library."
    result = _recover_bare_number_headings(md, raw)
    assert result == "## 2.3.4 Tensorflow as ML Framework\n\nTensorFlow is an open source library."


def test_recover_bare_number_headings_normalises_ligature():
    md = "## 2.3.4\n\nBody text."
    raw = "2.3.4 Tensorﬂow as ML Framework\nBody text."
    result = _recover_bare_number_headings(md, raw)
    assert "Tensorflow as ML Framework" in result
    assert "ﬂ" not in result


def test_recover_bare_number_headings_no_raw_text_unchanged():
    md = "## 2.3.4\n\nBody text."
    assert _recover_bare_number_headings(md, "") == md


def test_recover_bare_number_headings_complete_heading_unchanged():
    md = "## 2.3.3 Scikit-Learn as ML-Framework\n\nBody text."
    raw = "2.3.3 Scikit-Learn as ML-Framework\nBody text."
    result = _recover_bare_number_headings(md, raw)
    assert result == md


def test_clean_page_recovers_bare_heading_from_raw_text():
    md = "## **2.3.4**\n\nTensorFlow is an open source library."
    raw = "2.3.4 Tensorflow as ML Framework\nTensorFlow is an open source library."
    result = clean_page(md, raw_page_text=raw)
    assert "### 2.3.4 Tensorflow as ML Framework" in result


def test_postprocess_markdown_strips_page_footer_before_separator():
    page1 = "<!-- Page 2 -->\n\nSome content here.\n\n2"
    page2 = "<!-- Page 3 -->\n\nNext page content."
    md = f"{page1}\n\n---\n\n{page2}"
    result = postprocess_markdown(md)
    assert "\n2\n" not in result
    assert "Some content here." in result
    assert "Next page content." in result


def test_postprocess_markdown_strips_page_footer_at_end():
    md = "<!-- Page 11 -->\n\nFinal content.\n\n11"
    result = postprocess_markdown(md)
    assert result.strip().endswith("Final content.")
    assert "\n\n11" not in result


def test_postprocess_markdown_keeps_numbers_in_content():
    # A number that is part of actual text (not a lone footer) must be kept.
    page1 = "<!-- Page 2 -->\n\nThere are 2 approaches.\n\n2"
    page2 = "<!-- Page 3 -->\n\nNext."
    md = f"{page1}\n\n---\n\n{page2}"
    result = postprocess_markdown(md)
    assert "There are 2 approaches." in result


# ── _strip_bold_from_headings ────────────────────────────────────────────────

def test_strip_bold_strips_double_asterisk():
    assert _strip_bold_from_headings("## **Section Title**") == "## Section Title"


def test_strip_bold_strips_double_underscore():
    assert _strip_bold_from_headings("## __Section Title__") == "## Section Title"


def test_strip_bold_preserves_italic_underscore():
    # pymupdf4llm emits bold-italic headings as "## _**text**_"
    # After stripping **, the italic _ wrapper must be kept.
    assert _strip_bold_from_headings("## _**Bag of Words**_") == "## _Bag of Words_"


def test_strip_bold_preserves_plain_italic():
    # Headings that are only italic should not be touched.
    assert _strip_bold_from_headings("## _Sentiment Analysis_") == "## _Sentiment Analysis_"


def test_strip_bold_converts_triple_asterisk_to_italic():
    # ***text*** means bold-italic; strip bold, keep italic.
    assert _strip_bold_from_headings("## ***Introduction***") == "## _Introduction_"


def test_strip_bold_leaves_plain_heading_unchanged():
    assert _strip_bold_from_headings("## 2.3 Related Work") == "## 2.3 Related Work"


def test_strip_bold_works_on_all_heading_levels():
    assert _strip_bold_from_headings("# **Title**") == "# Title"
    assert _strip_bold_from_headings("### **Sub**") == "### Sub"


# ── _strip_duplicate_section_headers new behaviour ───────────────────────────

def test_strip_duplicate_numbered_heading_dropped():
    # Exact same numbered heading appearing twice → second one removed.
    md = "## 4.3 Training\n\nContent.\n\n## 4.3 Training\n\nMore."
    result = _strip_duplicate_section_headers(md)
    assert result.count("## 4.3 Training") == 1
    assert "More." in result


def test_strip_kapitel_running_header():
    # "# Kapitel 2 Title" on an interior page should be removed if "Title" was
    # already seen as a ## heading on the chapter-start page.
    md = (
        "# Kapitel 2\n\n## Theoretische Grundlagen\n\nContent.\n\n"
        "---\n\n"
        "# Kapitel 2 Theoretische Grundlagen\n\nNext page content."
    )
    result = _strip_duplicate_section_headers(md)
    assert "# Kapitel 2 Theoretische Grundlagen" not in result
    assert "# Kapitel 2\n" in result
    assert "## Theoretische Grundlagen" in result


def test_strip_kapitel_keeps_first_occurrence():
    # If a "# Kapitel N Title" combined form appears before the ## heading,
    # it is the first occurrence and must not be removed.
    md = "# Kapitel 1 Einleitung\n\nContent."
    result = _strip_duplicate_section_headers(md)
    assert "# Kapitel 1 Einleitung" in result


# ── _recover_bare_number_headings: title-without-number ──────────────────────

def test_recover_adds_missing_section_number():
    md = "## Neuronale Netze\n\nBody text."
    raw = "2.3 Neuronale Netze\nBody text."
    result = _recover_bare_number_headings(md, raw)
    assert "## 2.3 Neuronale Netze" in result


def test_recover_does_not_add_number_to_structural_keyword():
    # "Einleitung" is a structural keyword and should keep no number even if
    # fitz raw text has "1.1 Einleitung".
    md = "## Einleitung\n\nContent."
    raw = "1.1 Einleitung\nContent."
    result = _recover_bare_number_headings(md, raw)
    assert result == md  # unchanged


def test_recover_does_not_add_number_when_already_numbered():
    md = "## 2.3 Neuronale Netze\n\nBody."
    raw = "2.3 Neuronale Netze\nBody."
    result = _recover_bare_number_headings(md, raw)
    assert result == md  # unchanged


# ── _demote_unlabeled_single_word_headings: Abstrakt keyword ─────────────────

def test_abstrakt_kept_as_heading():
    # "Abstrakt" is a structural keyword and must not be demoted to bold.
    result = _demote_unlabeled_single_word_headings("## Abstrakt")
    assert result == "## Abstrakt"


# ── _strip_bibliography_dash ─────────────────────────────────────────────────

def test_strip_bibliography_dash_removes_leading_dash():
    md = "**Halder, Stephan :**\n\n– Recursive Backwards Q-Learning.\n"
    result = _strip_bibliography_dash(md)
    assert result.startswith("**Halder, Stephan :**")
    assert "– " not in result
    assert "Recursive Backwards Q-Learning." in result


def test_strip_bibliography_dash_leaves_inline_dash_unchanged():
    # Em-dash that is NOT at the start of a paragraph is left alone.
    md = "Some text – more text.\n"
    assert _strip_bibliography_dash(md) == md


# ── _normalise_latex_delimiters ──────────────────────────────────────────────

def test_normalise_latex_inline():
    assert _normalise_latex_delimiters(r"\( a + b \)") == "$a + b$"


def test_normalise_latex_display():
    assert _normalise_latex_delimiters(r"\[ E = mc^2 \]") == "$$E = mc^2$$"


def test_normalise_latex_leaves_dollar_unchanged():
    md = "$a + b$\n\n$$E = mc^2$$\n"
    assert _normalise_latex_delimiters(md) == md


def test_postprocess_markdown_normalises_latex():
    md = r"See \( o_j = F(\varphi_j) \) for details."
    result = postprocess_markdown(md)
    assert r"\(" not in result
    assert "$o_j = F(\\varphi_j)$" in result
