from postprocess import (
    clean_page,
    postprocess_markdown,
    _clean_list_dot_leaders,
    _clean_toc_dot_leaders,
    _clean_picture_text_blocks,
    _convert_abbreviations,
    _convert_greek_italic_math,
    _convert_list_bullets_to_table_rows,
    _convert_toc_table,
    _demote_code_listing_headings,
    _demote_italic_headings,
    _demote_outline_chapter_refs,
    _demote_title_page_headings,
    _demote_unlabeled_single_word_headings,
    _fix_bold_listing_headings,
    _fix_bold_space_before_colon,
    _fix_listing_table,
    _fix_split_code_span_tokens,
    _fix_table_list_header,
    _fix_table_row_bold_span,
    _format_figure_captions,
    _fix_ocr_superscripts,
    _interleave_batched_figures,
    _merge_kapitel_headings,
    _merge_wrapped_listing_table_rows,
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
    _wrap_monospace_code_blocks,
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
    # Figure captions are normalised to the bold-label style
    assert "**Figure 2.1:** content here" in result


def test_clean_page_leaves_output_without_instruction_untouched():
    md = "## 1.1 Section Title\n\nSome paragraph text.\n\n![](figures/fig.png)"
    assert clean_page(md) == md


def test_format_figure_captions_bold_after_image():
    md = "![Figure 1](figures/page_009_fig_001.png)\n\n**Figure 1.1:** What is this Thesis about?"
    result = _format_figure_captions(md)
    # blank lines between image and caption removed; caption stays bold-label style
    assert result == "![Figure 1](figures/page_009_fig_001.png)\n**Figure 1.1:** What is this Thesis about?"


def test_format_figure_captions_standalone_bold_caption():
    md = "Some text.\n\n**Figure 2.3:** Description here.\n\nMore text."
    result = _format_figure_captions(md)
    assert "**Figure 2.3:** Description here." in result


def test_format_figure_captions_italic_converted_to_bold():
    md = "![img](figures/fig.png)\n*Figure 1.1: caption*"
    result = _format_figure_captions(md)
    assert result == "![img](figures/fig.png)\n**Figure 1.1:** caption"


def test_format_figure_captions_german_abb():
    md = "![img](figures/fig.png)\n**Abb. 2.1:** Ergebnis der Analyse"
    result = _format_figure_captions(md)
    assert "**Abb. 2.1:** Ergebnis der Analyse" in result


def test_fix_ocr_superscripts_emc2():
    assert _fix_ocr_superscripts("According to _EMC_[2] 1,7 MB") == "According to EMC² 1,7 MB"


def test_fix_ocr_superscripts_multi_digit_citation_unchanged():
    assert _fix_ocr_superscripts("cited by [2016]") == "cited by [2016]"
    assert _fix_ocr_superscripts("Smith et al. [12]") == "Smith et al. [12]"


def test_fix_ocr_superscripts_nasa():
    assert _fix_ocr_superscripts("_NASA_[3]") == "NASA³"


def test_fix_ocr_superscripts_negative_exponent():
    assert _fix_ocr_superscripts("10 _[−]_[6]") == "10 ⁻⁶"


def test_fix_ocr_superscripts_negative_exponent_multi_digit():
    assert _fix_ocr_superscripts("10 _[−]_[15]") == "10 ⁻¹⁵"


def test_fix_ocr_superscripts_latex_logo():
    assert _fix_ocr_superscripts("it generates a full L[A] TEX paper") == "it generates a full LaTeX paper"


def test_fix_ocr_superscripts_plain_negative_exponent():
    assert _fix_ocr_superscripts("2.25×10−1") == "2.25×10⁻¹"


def test_fix_ocr_superscripts_bold_exponent():
    assert _fix_ocr_superscripts("Chi**2") == "Chi²"


def test_fix_ocr_superscripts_leaves_normal_bold_unchanged():
    assert _fix_ocr_superscripts("**bold text**") == "**bold text**"


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


def test_unwrap_symbol_italics_leaves_table_cell_boundary_untouched():
    # Regression: "**|**" at the boundary between two individually bold-wrapped
    # table cells used to be mistaken for a pipe symbol wrapped in emphasis,
    # collapsing "**ID**|**document**" back into "**ID|document**".
    md = "|**ID**|**document**|**sentiment**|"
    assert _unwrap_symbol_italics(md) == md


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


def test_reorder_captions_bold_before_image():
    md = "**Figure 1.1:** What is this Thesis about?\n\n![Figure 1](figures/page_009_fig_001.png)"
    result = _reorder_captions_after_images(md)
    assert result.index("![") < result.index("*")
    assert "Figure 1.1" in result


def test_reorder_captions_correct_order_unchanged():
    md = "![Figure 1](figures/img.png)\n**Figure 1.1:** caption"
    assert _reorder_captions_after_images(md) == md


def test_clean_page_swaps_bold_caption_before_image():
    md = "**Figure 2.1:** Some chart\n\n![Figure 2](figures/fig2.png)"
    result = clean_page(md)
    assert result.index("![") < result.index("*")
    assert "Figure 2.1" in result


def test_reorder_captions_german_abb_before_image():
    md = "**Abb. 3.1:** Ergebnis\n\n![Figure 3](figures/fig3.png)"
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


def test_strip_mid_doc_page_numbers_removes_number_directly_after_table_row():
    # No blank line between the table's last row and the page-footer number —
    # the plain "\n\n56\n\n" pattern above doesn't match this case.
    md = "| RBQL | Recursive Backwards Q-Learning |\n56\n\n---\n"
    result = _strip_mid_doc_page_numbers(md)
    assert "56" not in result
    assert "| RBQL | Recursive Backwards Q-Learning |" in result


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


def test_strip_mid_doc_running_headers_keeps_paragraph_starting_with_chapter_number():
    # Regression: the "Chapter N ..." running-header pattern used to match
    # greedily with ".*", which swallowed a full paragraph that merely
    # started with "Chapter 4" followed by a sentence containing a period.
    md = (
        "This section explains how the requirements are verified.\n\n"
        "Chapter 4 defines eleven requirements (FR1-FR8, NFR1-NFR2, C1). "
        "As discussed in that chapter, the requirements are scoped to "
        "deterministic system behaviors.\n\n"
        "Besides the requirements verification, Section 6.3 presents results.\n"
    )
    result = _strip_mid_doc_running_headers(md)
    assert "Chapter 4 defines eleven requirements" in result
    assert "deterministic system behaviors." in result


def test_strip_mid_doc_running_headers_removes_bibliography_header():
    md = "Some entry.\n\nBibliography\n\nAnother entry.\n"
    result = _strip_mid_doc_running_headers(md)
    assert "\n\nBibliography\n\n" not in result
    assert "Some entry." in result
    assert "Another entry." in result


def test_strip_mid_doc_running_headers_removes_tabellenverzeichnis_header():
    md = "- 6.9 Entry one 42\n\nTabellenverzeichnis\n\n- 6.10 Entry two 42\n"
    result = _strip_mid_doc_running_headers(md)
    assert "\n\nTabellenverzeichnis\n\n" not in result


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


# ── _interleave_batched_figures ────────────────────────────────────────────────

def test_interleave_batched_figures_pairs_images_with_captions():
    md = (
        "![Figure 1](figures/page_039_fig_001.png)\n"
        "![Figure 2](figures/page_039_fig_002.jpeg)\n"
        "**Figure 4.8:** The activity diagram shows the hypothesis generation pipeline.\n"
        "**Figure 4.9:** The hypothesis generation screen.\n"
    )
    result = _interleave_batched_figures(md)
    lines = [l for l in result.split("\n") if l.strip()]
    assert lines[0] == "![Figure 1](figures/page_039_fig_001.png)"
    assert lines[1] == "**Figure 4.8:** The activity diagram shows the hypothesis generation pipeline."
    assert lines[2] == "![Figure 2](figures/page_039_fig_002.jpeg)"
    assert lines[3] == "**Figure 4.9:** The hypothesis generation screen."


def test_interleave_batched_figures_leaves_single_pair_untouched():
    md = "![Figure 1](figures/fig.png)\n**Figure 1.1:** A caption.\n"
    assert _interleave_batched_figures(md) == md


def test_interleave_batched_figures_leaves_mismatched_counts_untouched():
    md = (
        "![Figure 1](figures/fig1.png)\n"
        "![Figure 2](figures/fig2.png)\n"
        "**Figure 1.1:** First caption.\n"
        "**Figure 1.2:** Second caption.\n"
        "**Figure 1.3:** Third caption.\n"
    )
    assert _interleave_batched_figures(md) == md


# ── _clean_list_dot_leaders ────────────────────────────────────────────────────

def test_clean_list_dot_leaders_strips_dots_and_keeps_page_number():
    md = "- 6.1 Vergleich der Lernkurven. . . . . . . . 27"
    assert _clean_list_dot_leaders(md) == "- 6.1 Vergleich der Lernkurven 27"


def test_clean_list_dot_leaders_leaves_non_list_line_untouched():
    md = "This is a normal sentence ending in the number 27."
    assert _clean_list_dot_leaders(md) == md


def test_clean_list_dot_leaders_leaves_bullet_without_dot_leader():
    md = "- A plain bullet point with no dots"
    assert _clean_list_dot_leaders(md) == md


# ── _fix_table_row_bold_span ───────────────────────────────────────────────────

def test_fix_table_row_bold_span_rewraps_each_cell():
    md = "|**ID|Requirement|Pass Condition**|\n|---|---|---|\n|FR1|Context|test|"
    result = _fix_table_row_bold_span(md)
    assert result.startswith("|**ID**|**Requirement**|**Pass Condition**|")


def test_fix_table_row_bold_span_handles_mangled_exponent_row():
    md = (
        "|**Variable|MAD|Chi²|**p-value|Classifcation**|\n"
        "|---|---|---|---|---|\n"
        "|Population Count|0.0027|10.60|2.25|Excellent|"
    )
    result = _fix_table_row_bold_span(md)
    assert result.startswith("|**Variable**|**MAD**|**Chi²**|**p-value**|**Classifcation**|")


def test_fix_table_row_bold_span_ignores_row_without_following_separator():
    md = "|**ID|Requirement**|\n\nSome text, not a table.\n"
    assert _fix_table_row_bold_span(md) == md


def test_fix_table_row_bold_span_leaves_data_rows_alone():
    md = "|**ID**|**Requirement**|\n|---|---|\n|FR1|**already bold value**|"
    result = _fix_table_row_bold_span(md)
    assert "|FR1|**already bold value**|" in result


# ── _fix_split_code_span_tokens ────────────────────────────────────────────────

def test_fix_split_code_span_tokens_removes_space_in_url():
    md = "url: `htt ps://arxiv.org/abs/2511.05502`"
    assert _fix_split_code_span_tokens(md) == "url: `https://arxiv.org/abs/2511.05502`"


def test_fix_split_code_span_tokens_removes_space_in_numeric_id():
    md = "arXiv: `2408.0 6292`"
    assert _fix_split_code_span_tokens(md) == "arXiv: `2408.06292`"


def test_fix_split_code_span_tokens_keeps_space_before_category_tag():
    md = "`1908 . 10084 [cs.CL]`"
    assert _fix_split_code_span_tokens(md) == "`1908.10084 [cs.CL]`"


def test_fix_split_code_span_tokens_leaves_normal_inline_code_untouched():
    md = "Call `response_format` with the schema."
    assert _fix_split_code_span_tokens(md) == md


# ── _wrap_monospace_code_blocks ────────────────────────────────────────────────

def test_wrap_monospace_code_blocks_wraps_single_listing():
    code_lines = ["1 def getState(x):", "2 return x"]
    md = "\n".join(code_lines)
    result = _wrap_monospace_code_blocks(md, code_lines)
    assert result == "```\n1 def getState(x):\n2 return x\n```\n"


def test_wrap_monospace_code_blocks_renumbers_sequentially():
    code_lines = ["1 # Paper Specification", "3 ## General Information", "10 ## Section Requirements"]
    md = "\n".join(code_lines)
    result = _wrap_monospace_code_blocks(md, code_lines)
    assert result == "```\n1 # Paper Specification\n2 ## General Information\n3 ## Section Requirements\n```\n"


def test_wrap_monospace_code_blocks_keeps_separate_listings_apart():
    code_lines = ["1 def a():", "2 return 1", "1 def b():", "2 return 2"]
    md = (
        "1 def a(): 2 return 1\n\n"
        "Some prose between the two listings.\n\n"
        "1 def b(): 2 return 2"
    )
    result = _wrap_monospace_code_blocks(md, code_lines)
    assert result.count("```") == 4
    assert "Some prose between the two listings." in result
    before, after = result.split("Some prose between the two listings.")
    assert "def b" not in before
    assert "def b" in after


def test_wrap_monospace_code_blocks_does_not_bleed_into_identical_line():
    # Two different listings that happen to share the exact same opening line
    # must not have the second one's content merged into the first's fence.
    code_lines = [
        "1 def updateQ(reward, state):",
        "2 global er_re",
        "1 def updateQ(reward, state):",
        "2 Q[int(state)] += alpha",
    ]
    md = (
        "1 def updateQ(reward, state): 2 global er_re\n\n"
        "**Quellcode 5.3:** first listing\n\n"
        "1 def updateQ(reward, state): 2 Q[int(state)] += alpha\n"
    )
    result = _wrap_monospace_code_blocks(md, code_lines)
    assert result.count("```") == 4
    first_fence = result.split("```")[1]
    assert "Q[int(state)]" not in first_fence


def test_wrap_monospace_code_blocks_no_targets_returns_unchanged():
    md = "Some plain text with no code."
    assert _wrap_monospace_code_blocks(md, []) == md


# ── _convert_list_bullets_to_table_rows ────────────────────────────────────────

def test_convert_list_bullets_to_table_rows_converts_bullets_in_listing_section():
    md = (
        "**Tabellenverzeichnis**\n\n"
        "- 6.1 Vergleich der Lernkurven 26\n\n"
        "- 6.2 Weitere Ergebnisse 28\n"
    )
    result = _convert_list_bullets_to_table_rows(md)
    assert "| 6.1 | Vergleich der Lernkurven | 26 |" in result
    assert "| 6.2 | Weitere Ergebnisse | 28 |" in result
    assert "- 6.1" not in result


def test_convert_list_bullets_to_table_rows_ignores_bullets_outside_listing_section():
    md = "## Regular Chapter\n\n- 6.1 Not a list-of-tables entry 26\n"
    assert _convert_list_bullets_to_table_rows(md) == md


def test_convert_list_bullets_to_table_rows_stops_at_next_heading():
    md = (
        "**Tabellenverzeichnis**\n\n"
        "- 6.1 Entry 26\n\n"
        "## Kapitel 7\n\n"
        "- 6.2 This looks like a bullet but is past the list section 28\n"
    )
    result = _convert_list_bullets_to_table_rows(md)
    assert "| 6.1 | Entry | 26 |" in result
    assert "- 6.2 This looks like a bullet but is past the list section 28" in result


# ── _merge_wrapped_listing_table_rows ──────────────────────────────────────────

def test_merge_wrapped_listing_table_rows_merges_continuation_rows():
    md = (
        "Tabellenverzeichnis\n\n"
        "|6.9|Vergleich von RBQL und der optimierten Version des RBQL und Experi-||\n"
        "|---|---|---|\n"
        "||ence Replay Q-Learning beim Trainieren.|42|\n"
    )
    result = _merge_wrapped_listing_table_rows(md)
    assert (
        "| 6.9 | Vergleich von RBQL und der optimierten Version des RBQL und "
        "Experience Replay Q-Learning beim Trainieren. | 42 |"
    ) in result


def test_merge_wrapped_listing_table_rows_leaves_normal_table_untouched():
    md = "Some heading\n\n|A|B|\n|---|---|\n|1|2|\n"
    assert _merge_wrapped_listing_table_rows(md) == md
