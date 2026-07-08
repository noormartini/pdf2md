from postprocess import (
    clean_page,
    postprocess_markdown,
    _clean_toc_dot_leaders,
    _clean_picture_text_blocks,
    _convert_abbreviations,
    _convert_greek_italic_math,
    _convert_toc_table,
    _demote_code_listing_headings,
    _demote_italic_headings,
    _demote_outline_chapter_refs,
    _demote_title_page_headings,
    _demote_unlabeled_single_word_headings,
    _fix_bold_listing_headings,
    _fix_bold_space_before_colon,
    _fix_listing_table,
    _fix_table_list_header,
    _format_figure_captions,
    _fix_ocr_superscripts,
    _merge_kapitel_headings,
    _normalise_latex_delimiters,
    _promote_declaration_heading,
    _reorder_captions_after_images,
    _recover_bare_number_headings,
    _strip_bibliography_dash,
    _strip_bold_from_headings,
    _strip_duplicate_section_headers,
    _strip_mid_doc_page_numbers,
    _strip_mid_doc_running_headers,
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


# ── _convert_greek_italic_math ────────────────────────────────────────────────

def test_greek_italic_single_letter():
    assert _convert_greek_italic_math("_φ_") == "$\\varphi$"


def test_greek_italic_with_subscript():
    assert _convert_greek_italic_math("_φj_") == "$\\varphi_j$"


def test_greek_italic_long_subscript():
    assert _convert_greek_italic_math("_φjk_") == "$\\varphi_{jk}$"


def test_greek_italic_uppercase():
    assert _convert_greek_italic_math("_Δt_") == "$\\Delta_t$"


def test_greek_italic_inline_formula():
    line = "lineare Funktion: _oj_ = _F_ ( _φj_ ) = _φ_ (2.6)"
    result = _convert_greek_italic_math(line)
    assert "$\\varphi_j$" in result
    assert "$\\varphi$" in result
    assert "_oj_" in result   # no Greek, left alone
    assert "_F_" in result    # no Greek, left alone


def test_greek_italic_leaves_plain_italic():
    assert _convert_greek_italic_math("_hello_") == "_hello_"
    assert _convert_greek_italic_math("_result_") == "_result_"


def test_greek_italic_skips_code_block():
    md = "```python\n_φ_ = value\n```"
    assert _convert_greek_italic_math(md) == md


def test_greek_italic_multiple_in_line():
    line = "where _α_ and _β_ are parameters"
    result = _convert_greek_italic_math(line)
    assert "$\\alpha$" in result
    assert "$\\beta$" in result


def test_greek_italic_sigma():
    assert _convert_greek_italic_math("_σ_") == "$\\sigma$"


def test_greek_italic_omega():
    assert _convert_greek_italic_math("_ω_") == "$\\omega$"


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


def test_clean_page_converts_toc_table_to_nested_list():
    md = (
        "| Inhaltsverzeichnis |  |\n"
        "| --- | --- |\n"
        "| 1 Einleitung | 1 |\n"
        "| 2 Grundlagen | 3 |\n"
    )
    result = clean_page(md)
    assert "## Contents" in result
    assert "**1 Einleitung** 1" in result
    assert "**2 Grundlagen** 3" in result
    assert "| --- | --- |" not in result


def test_convert_toc_table_two_col_nesting():
    md = (
        "| Contents |\n"
        "| --- | --- |\n"
        "| List of Abbreviations | vii |\n"
        "| 1 Introduction | 1 |\n"
        "| 2 Foundations | 3 |\n"
        "| 2.1 Background | 4 |\n"
        "| 2.1.1 Details | 5 |\n"
    )
    result = _convert_toc_table(md)
    assert "## Contents" in result
    assert "- List of Abbreviations vii" in result
    assert "- **1 Introduction** 1" in result
    assert "- **2 Foundations** 3" in result
    assert "  - 2.1 Background 4" in result
    assert "    - 2.1.1 Details 5" in result
    assert "|" not in result


def test_convert_toc_table_three_col_depth():
    md = (
        "| Chapter | Section | Page |\n"
        "|---|---|---|\n"
        "| 6 | Evaluation | 46 |\n"
        "|   | Methodology | 46 |\n"
        "|     | Setup | 47 |\n"
        "| 7 | Discussion | 61 |\n"
        "| Bibliography | | xi |\n"
    )
    result = _convert_toc_table(md)
    assert "- **6 Evaluation** 46" in result
    assert "  - Methodology 46" in result
    assert "    - Setup 47" in result
    assert "- **7 Discussion** 61" in result
    assert "- **Bibliography** xi" in result
    assert "|" not in result


def test_convert_abbreviations_inline_to_table():
    md = (
        "**AI** artificial intelligence "
        "**API** application programming interface "
        "**CLI** command line interface "
        "**DOI** digital object identifier"
    )
    result = _convert_abbreviations(md)
    assert "| Abbreviation | Definition |" in result
    assert "| AI | artificial intelligence |" in result
    assert "| API | application programming interface |" in result
    assert "**AI**" not in result


def test_convert_abbreviations_leaves_normal_bold_alone():
    md = "**Bold text** that is not an abbreviation list."
    assert _convert_abbreviations(md) == md


def test_fix_listing_table_figures():
    md = (
        "| List of Figures |\n"
        "| --- | --- |\n"
        "| 1.1 Six-phase research pipeline | 2 |\n"
        "| 4.1 High-level system architecture | 13 |\n"
    )
    result = _fix_listing_table(md)
    assert "## List of Figures" in result
    assert "| Figure | Description | Page |" in result
    assert "| 1.1 | Six-phase research pipeline | 2 |" in result
    assert "| 4.1 | High-level system architecture | 13 |" in result
    assert "| --- | --- |" not in result


def test_fix_listing_table_with_dot_debris():
    md = (
        "| Listings |\n"
        "| --- | --- |\n"
        "\n"
        "| 4.1 Paper specification template | ... | ... | ... |\n"
        "| 5.1 Hypothesis response schema | ... | ... |\n"
    )
    result = _fix_listing_table(md)
    assert "## Listings" in result
    assert "| Listing | Description | Page |" in result
    assert "| 4.1 | Paper specification template |" in result
    assert "| 5.1 | Hypothesis response schema |" in result


def test_fix_table_list_header_adds_heading_and_page_column():
    md = (
        "| Table | Description |\n"
        "|---|---|\n"
        "| 3.1 | Comparison of systems |  |\n"
    )
    result = _fix_table_list_header(md)
    assert "## List of Tables" in result
    assert "| Table | Description | Page |" in result
    assert "|---|---|---|" in result
    assert "| 3.1 | Comparison of systems |  |" in result


def test_fix_table_list_header_no_duplicate_heading():
    md = (
        "## List of Tables\n\n"
        "| Table | Description |\n"
        "|---|---|\n"
        "| 3.1 | Comparison |  |\n"
    )
    result = _fix_table_list_header(md)
    assert result.count("## List of Tables") == 1


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


# ── _demote_title_page_headings ───────────────────────────────────────────────

def test_demote_title_page_headings_basic():
    md = (
        "# My Thesis Title\n\n"
        "## Author Name\n\n"
        "## 14.08.2025\n\n"
        "## Abstrakt\n\n"
        "Some abstract text.\n"
    )
    result = _demote_title_page_headings(md)
    assert "## Author Name" not in result
    assert "Author Name" in result
    assert "## 14.08.2025" not in result
    assert "14.08.2025" in result
    assert "## Abstrakt" in result  # structural section kept


def test_demote_title_page_headings_keeps_h1_title():
    md = (
        "# The Title\n\n"
        "## Some Metadata\n\n"
        "## Erklärung\n\n"
        "Declaration text.\n"
    )
    result = _demote_title_page_headings(md)
    assert "# The Title" in result
    assert "## Some Metadata" not in result
    assert "## Erklärung" in result


def test_demote_title_page_headings_no_structural_section_unchanged():
    md = "# Title\n\n## Section One\n\nSome text.\n"
    assert _demote_title_page_headings(md) == md


def test_postprocess_markdown_strips_bold_from_headings():
    # No front-matter boundary present, so no title-page demotion fires.
    md = "## **Section Title**\n\nSome text.\n"
    result = postprocess_markdown(md)
    assert "## **Section Title**" not in result
    assert "## Section Title" in result


# ── _merge_kapitel_headings ───────────────────────────────────────────────────

def test_merge_kapitel_headings_basic():
    md = "## Kapitel 1\n\n## Einleitung\n\n## 1.1 Background\n"
    result = _merge_kapitel_headings(md)
    assert "## Kapitel 1" not in result
    assert "# Kapitel 1: Einleitung" in result
    assert "## 1.1 Background" in result


def test_merge_kapitel_headings_multiple_chapters():
    md = (
        "## Kapitel 1\n\n## Introduction\n\nText.\n\n"
        "## Kapitel 2\n\n## Background\n\nText.\n"
    )
    result = _merge_kapitel_headings(md)
    assert "# Kapitel 1: Introduction" in result
    assert "# Kapitel 2: Background" in result
    assert "## Kapitel" not in result


def test_merge_kapitel_headings_no_following_heading_drops_line():
    md = "## Kapitel 3\n\nSome plain text.\n"
    result = _merge_kapitel_headings(md)
    assert "## Kapitel 3" not in result
    assert "Some plain text." in result


def test_merge_kapitel_headings_english_chapter():
    md = "## Chapter 1\n\n## Introduction\n\n## 1.1 Background\n"
    result = _merge_kapitel_headings(md)
    assert "## Chapter 1" not in result
    assert "# Chapter 1: Introduction" in result
    assert "## 1.1 Background" in result


def test_merge_kapitel_headings_english_multiple():
    md = (
        "## Chapter 1\n\n## Introduction\n\nText.\n\n"
        "## Chapter 2\n\n## Foundations\n\nText.\n"
    )
    result = _merge_kapitel_headings(md)
    assert "# Chapter 1: Introduction" in result
    assert "# Chapter 2: Foundations" in result
    assert "## Chapter" not in result


def test_postprocess_markdown_merges_kapitel_headings():
    md = "## **Kapitel 2**\n\n## **Grundlagen**\n\n## **2.1 Basics**\n"
    result = postprocess_markdown(md)
    assert "# Kapitel 2: Grundlagen" in result
    assert "## 2.1 Basics" in result


# ── _demote_italic_headings ───────────────────────────────────────────────────

def test_demote_italic_headings_abstract_subtitle():
    md = "## Abstract\n\n## _A Long Italic Paper Title Here_\n\nBody text.\n"
    result = _demote_italic_headings(md)
    assert "## _A Long Italic Paper Title Here_" not in result
    assert "_A Long Italic Paper Title Here_" in result
    assert "## Abstract" in result


def test_demote_italic_headings_multiple():
    md = "## Abstract\n\n## _Title EN_\n\n## Abstrakt\n\n## _Title DE_\n\nText.\n"
    result = _demote_italic_headings(md)
    assert "## _Title EN_" not in result
    assert "## _Title DE_" not in result
    assert "_Title EN_" in result
    assert "_Title DE_" in result


def test_demote_italic_headings_leaves_partial_italic():
    # Only part of the heading is italic — should not be demoted.
    md = "## 3.1 _Related Work_ Overview\n\nText.\n"
    assert _demote_italic_headings(md) == md


def test_demote_italic_headings_leaves_normal_headings():
    md = "## Introduction\n\n## Background\n"
    assert _demote_italic_headings(md) == md


def test_postprocess_markdown_demotes_italic_abstract_subtitle():
    md = "## Abstract\n\n## _Full Paper Title in Italic_\n\nSome abstract text.\n"
    result = postprocess_markdown(md)
    assert "## _Full Paper Title in Italic_" not in result
    assert "_Full Paper Title in Italic_" in result


# ── _demote_code_listing_headings ─────────────────────────────────────────────

def test_demote_code_listing_headings_converts_to_list_item():
    md = "- 10 `parts.append(x)`\n\n## 11 `return ''.join(parts)`\n"
    result = _demote_code_listing_headings(md)
    assert "## 11" not in result
    assert "- 11 `return ''.join(parts)`" in result


def test_demote_code_listing_headings_different_level():
    md = "### 3 `some_function()`\n"
    result = _demote_code_listing_headings(md)
    assert "### 3" not in result
    assert "- 3 `some_function()`" in result


def test_demote_code_listing_headings_leaves_real_sections():
    # Real numbered section headings — no backtick code span.
    md = "## 3.1 Related Work\n\n## 4 System Design\n"
    assert _demote_code_listing_headings(md) == md


def test_postprocess_markdown_demotes_code_listing_heading():
    md = "- 9 `if x:`\n\n## 11 `return result`\n\nText after.\n"
    result = postprocess_markdown(md)
    assert "## 11" not in result
    assert "- 11 `return result`" in result


# ── _clean_picture_text_blocks ────────────────────────────────────────────────

_PTB_START = "**----- Start of picture text -----**<br>"
_PTB_END = "**----- End of picture text -----**<br>"


def test_clean_picture_text_blocks_removes_markers():
    md = f"{_PTB_START}\nSome OCR text<br>\nMore text<br>\n{_PTB_END}\n"
    result = _clean_picture_text_blocks(md)
    assert "Start of picture text" not in result
    assert "End of picture text" not in result


def test_clean_picture_text_blocks_drops_content():
    md = f"{_PTB_START}\nPhase One<br>\nPhase Two<br>\n{_PTB_END}\n"
    result = _clean_picture_text_blocks(md)
    assert "Phase One" not in result
    assert "Phase Two" not in result


def test_clean_picture_text_blocks_drops_br_tags():
    md = f"{_PTB_START}\nA<br>B<br>C<br>\n{_PTB_END}\n"
    result = _clean_picture_text_blocks(md)
    assert result.strip() == ""


def test_clean_picture_text_blocks_leaves_normal_content_alone():
    md = "## Introduction\n\nSome text.\n"
    assert _clean_picture_text_blocks(md) == md


def test_postprocess_markdown_cleans_picture_text_block():
    md = (
        "Body text.\n\n"
        f"{_PTB_START}\nDiagram label<br>\n{_PTB_END}\n\n"
        "**Figure 1:** Caption.\n"
    )
    result = postprocess_markdown(md)
    assert "Start of picture text" not in result
    assert "Diagram label" not in result
    assert "**Figure 1:** Caption." in result


# ── _strip_mid_doc_page_numbers ───────────────────────────────────────────────

def test_strip_mid_doc_page_numbers_removes_lone_number():
    md = "Some text.\n\n3\n\nMore text.\n"
    result = _strip_mid_doc_page_numbers(md)
    assert "\n\n3\n\n" not in result
    assert "Some text." in result
    assert "More text." in result


def test_strip_mid_doc_page_numbers_removes_number_with_space():
    md = "End of para.\n\n12 \n\nNext para.\n"
    result = _strip_mid_doc_page_numbers(md)
    assert "12" not in result


def test_strip_mid_doc_page_numbers_leaves_inline_numbers():
    md = "There are 3 items listed here.\n"
    assert _strip_mid_doc_page_numbers(md) == md


def test_strip_mid_doc_page_numbers_removes_roman_numeral_v():
    md = "End of section.\n\nv\n\nNext chapter.\n"
    result = _strip_mid_doc_page_numbers(md)
    assert "\n\nv\n\n" not in result
    assert "End of section." in result
    assert "Next chapter." in result


def test_strip_mid_doc_page_numbers_removes_roman_numeral_vi():
    md = "Some text.\n\nvi\n\nMore text.\n"
    result = _strip_mid_doc_page_numbers(md)
    assert "vi" not in result


def test_strip_mid_doc_page_numbers_leaves_inline_roman():
    # Roman numeral not isolated — leave alone.
    md = "Section vi is discussed in chapter v of the document.\n"
    assert _strip_mid_doc_page_numbers(md) == md


# ── _strip_mid_doc_running_headers ────────────────────────────────────────────

def test_strip_mid_doc_running_headers_removes_kapitel_line():
    md = "Body text.\n\nKapitel 2 Theoretische Grundlagen\n\nMore body.\n"
    result = _strip_mid_doc_running_headers(md)
    assert "Kapitel 2 Theoretische Grundlagen" not in result
    assert "Body text." in result
    assert "More body." in result


def test_strip_mid_doc_running_headers_removes_numbered_section():
    md = "Para one.\n\n2.1 Reinforcement Learning\n\nPara two.\n"
    result = _strip_mid_doc_running_headers(md)
    assert "2.1 Reinforcement Learning" not in result


def test_strip_mid_doc_running_headers_keeps_heading_lines():
    md = "## 2.1 Reinforcement Learning\n\nPara.\n"
    assert _strip_mid_doc_running_headers(md) == md


def test_strip_mid_doc_running_headers_keeps_non_isolated_line():
    # Not surrounded by blank lines — leave it alone.
    md = "Some text.\n2.1 Something Capital\nMore text.\n"
    result = _strip_mid_doc_running_headers(md)
    assert "2.1 Something Capital" in result


def test_strip_mid_doc_running_headers_removes_inhaltsverzeichnis():
    # TOC continuation page header appearing as plain text.
    md = "Last toc entry.\n\nInhaltsverzeichnis\n\nNext toc entry.\n"
    result = _strip_mid_doc_running_headers(md)
    assert "Inhaltsverzeichnis" not in result
    assert "Last toc entry." in result
    assert "Next toc entry." in result


def test_strip_mid_doc_running_headers_removes_abstract_header():
    md = "Some para.\n\nAbstrakt\n\nNext para.\n"
    result = _strip_mid_doc_running_headers(md)
    assert "Abstrakt" not in result


def test_strip_mid_doc_running_headers_keeps_non_isolated_front_matter():
    # Embedded in a sentence — not a running header.
    md = "See the Inhaltsverzeichnis for details.\n"
    assert _strip_mid_doc_running_headers(md) == md


def test_fix_bold_space_before_colon_removes_space():
    md = "**Schmitt, Steven :** Some text"
    assert _fix_bold_space_before_colon(md) == "**Schmitt, Steven:** Some text"


def test_fix_bold_space_before_colon_leaves_normal_bold():
    md = "**Bold text** and more."
    assert _fix_bold_space_before_colon(md) == md


def test_fix_bold_listing_headings_converts_listings():
    md = "**Listings**\n\n| Listing | Description | Page |\n"
    result = _fix_bold_listing_headings(md)
    assert result.startswith("## Listings")


def test_fix_bold_listing_headings_converts_list_of_figures():
    md = "Some text\n\n**List of Figures**\n\n| Figure | Caption | Page |\n"
    result = _fix_bold_listing_headings(md)
    assert "## List of Figures" in result


def test_fix_bold_listing_headings_leaves_bold_in_sentence():
    md = "The **List of Figures** is on page ix."
    assert _fix_bold_listing_headings(md) == md


def test_foundations_keyword_not_demoted():
    md = "## Foundations\n\nSome text."
    result = clean_page(md)
    assert "## Foundations" in result


def test_implementation_keyword_not_demoted():
    md = "## Implementation\n\nSome text."
    result = clean_page(md)
    assert "## Implementation" in result


# ── _promote_declaration_heading ──────────────────────────────────────────────

def test_promote_declaration_heading_erklarung_slash_declaration():
    md = "Erklärung / Declaration\n\nI hereby declare..."
    result = _promote_declaration_heading(md)
    assert result.startswith("## Erklärung / Declaration")


def test_promote_declaration_heading_erklarung_only():
    md = "Erklärung\n\nHiermit erkläre ich..."
    result = _promote_declaration_heading(md)
    assert result.startswith("## Erklärung")


def test_promote_declaration_heading_leaves_existing_heading():
    md = "## Erklärung / Declaration\n\nBody text."
    assert _promote_declaration_heading(md) == md


def test_promote_declaration_heading_leaves_inline_occurrence():
    md = "See the Erklärung / Declaration section for details."
    assert _promote_declaration_heading(md) == md


# ── _strip_bibliography_dash (trailing dash) ──────────────────────────────────

def test_strip_bibliography_dash_strips_trailing_dash():
    md = "A Human-in-the-Loop System / Steven Schmitt. –\n"
    result = _strip_bibliography_dash(md)
    assert result == "A Human-in-the-Loop System / Steven Schmitt.\n"


def test_strip_bibliography_dash_strips_trailing_emdash_variant():
    md = "Ein System / Max Mustermann. —\n"
    result = _strip_bibliography_dash(md)
    assert result == "Ein System / Max Mustermann.\n"


def test_strip_bibliography_dash_leaves_mid_sentence_dash():
    md = "The system — which is local — runs offline.\n"
    assert _strip_bibliography_dash(md) == md
