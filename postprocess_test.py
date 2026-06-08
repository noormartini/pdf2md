from postprocess import (
    clean_page,
    _demote_outline_chapter_refs,
    _demote_unlabeled_single_word_headings,
    _format_figure_captions,
    _fix_ocr_superscripts,
    _reorder_captions_after_images,
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


def test_clean_page_demotes_bold_label_headings():
    md = "## Company\n\nAcme Corp\n\n## Department\n\nEngineering"
    result = clean_page(md)
    assert "**Company**" in result
    assert "**Department**" in result
    assert "## Company" not in result
    assert "## Department" not in result
