"""Tests for extraction/toc.py."""

from unittest.mock import patch, MagicMock

from extraction.toc import extract_toc


def _mock_doc(toc):
    doc = MagicMock()
    doc.get_toc.return_value = toc
    doc.__enter__ = lambda s: s
    doc.__exit__ = MagicMock(return_value=False)
    return doc


def test_extract_toc_empty_returns_empty_string():
    with patch("extraction.toc.fitz.open", return_value=_mock_doc([])):
        assert extract_toc("any.pdf") == ""


def test_extract_toc_formats_flat_entries():
    toc = [[1, "Introduction", 1], [1, "Methods", 5]]
    with patch("extraction.toc.fitz.open", return_value=_mock_doc(toc)):
        result = extract_toc("any.pdf")
    assert "Introduction (1)" in result
    assert "Methods (5)" in result


def test_extract_toc_indents_nested_levels():
    toc = [
        [1, "Chapter 1", 1],
        [2, "Section 1.1", 2],
        [3, "Subsection 1.1.1", 3],
    ]
    with patch("extraction.toc.fitz.open", return_value=_mock_doc(toc)):
        result = extract_toc("any.pdf")
    lines = result.splitlines()
    chapter_line = next(l for l in lines if "Chapter 1" in l)
    section_line = next(l for l in lines if "Section 1.1" in l)
    subsection_line = next(l for l in lines if "Subsection 1.1.1" in l)
    # Each deeper level has more leading spaces
    assert len(section_line) - len(section_line.lstrip()) > len(chapter_line) - len(chapter_line.lstrip())
    assert len(subsection_line) - len(subsection_line.lstrip()) > len(section_line) - len(section_line.lstrip())


def test_extract_toc_starts_with_heading():
    toc = [[1, "Intro", 1]]
    with patch("extraction.toc.fitz.open", return_value=_mock_doc(toc)):
        result = extract_toc("any.pdf")
    assert result.startswith("## Table of Contents")
