from postprocess import clean_page


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
    assert "**Figure 2.1:** content here" in result


def test_clean_page_leaves_output_without_instruction_untouched():
    md = "## Section\n\nSome paragraph text.\n\n![](figures/fig.png)"
    assert clean_page(md) == md
