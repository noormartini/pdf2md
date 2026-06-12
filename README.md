# PDF2MD — Adaptive PDF-to-Markdown Converter

Bachelor's thesis project. Converts PDF documents to Markdown using local LLMs via LM Studio. Each page is automatically analysed and routed to the most appropriate extraction strategy based on its content type.

---

## How It Works

1. **Analyse** — each PDF page is inspected with PyMuPDF to detect its content type (text, image, formula, mixed, or empty)
2. **Extract** — text pages have their text extracted directly; image/formula/mixed pages are rendered as PNG screenshots
3. **Convert** — the extracted content is sent to a local LLM in LM Studio, which returns clean Markdown
4. **Post-process** — 14 cleanup passes normalise headings, remove extraction artefacts, and produce a single `.md` file

---

## Strategies

| Strategy | How it works | Best for |
|----------|-------------|----------|
| `text` | Extracts raw text → sends to LLM | Clean text-only pages |
| `image` | Renders page as PNG → sends to vision LLM | Image-heavy pages |
| `hybrid` | Sends both text and image to vision LLM | Mixed content |
| `adaptive` | Auto-detects page type, picks the best strategy per page | Full documents |

The **adaptive** strategy is the core thesis contribution. It classifies each page and routes accordingly:

- `TEXT` → text strategy
- `FORMULA` → image rendered, formula-specific prompt
- `IMAGE` → image rendered, diagram-specific prompt
- `MIXED` → image rendered, general prompt
- `EMPTY` → skipped

---

## Requirements

- Python 3.12+
- [LM Studio](https://lmstudio.ai) running locally with a vision-capable model loaded
- Recommended model: **Qwen2.5-VL-7B** or **Qwen 3.5 9B**

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

LM Studio must be running with a model loaded before running any command.

```bash
# default: text strategy on the test PDF
python3 main.py

# specify a PDF and strategy
python3 main.py -i pdf_source/test_pdf_source.pdf -s adaptive

# run on a full thesis PDF
python3 main.py -i "pdf_source/Bachelor_Thesis_Informatik_Koehler_Sven.pdf" -s adaptive

# override model and page limit
python3 main.py -i pdf_source/test_pdf_source.pdf -s adaptive -m qwen/qwen3.5-9b -n 10
```

Output is saved to `output/test_pdf_output.md` by default.

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-i` / `--input` | `pdf_source/test_pdf_source.pdf` | Input PDF file |
| `-o` / `--output` | `output/test_pdf_output.md` | Output Markdown file |
| `-s` / `--strategy` | `text` | Strategy: `text`, `image`, `hybrid`, `adaptive` |
| `-m` / `--model` | `qwen/qwen3.5-9b` | Model name as loaded in LM Studio |
| `-b` / `--base-url` | `http://127.0.0.1:1234/v1` | LM Studio API base URL |
| `-n` / `--max-pages` | `3` | Maximum number of pages to convert |
| `-t` / `--temperature` | `0.2` | LLM sampling temperature (0.0 = deterministic) |
| `-T` / `--max-tokens` | `4096` | Maximum tokens in LLM response |

---

## Running Tests

```bash
pytest postprocess_test.py
```

99 tests cover all postprocessing functions individually as well as end-to-end `postprocess_markdown()` behaviour.

---

## Evaluation

Run a comparison experiment across strategies, models, and temperatures:

```bash
# run experiments (requires LM Studio running)
python3 -m evaluation.compare -c experiments/sample.json -o output/results.json

# generate markdown report from results
python3 -m evaluation.report -i output/results.json -o output/report.md
```

The experiment config (`experiments/sample.json`) controls which PDFs, strategies, models, prompt variants, and temperatures to compare. Reference ground-truth pages are stored in `references/page_NNN.md`.

**Metrics computed per page:**

| Metric | What it measures |
|--------|-----------------|
| Text similarity | Character-level overlap with reference (difflib) |
| Heading structure | H1/H2/H3 count match vs. reference |
| List structure | Bullet and numbered list fidelity |
| Table detection | Presence and count of Markdown tables |
| Code block accuracy | Fenced code block match |
| Paragraph count | Paragraph count vs. reference |
| Word overlap | Bag-of-words Jaccard similarity |

---

## Project Structure

```
PDF2MD/
├── pdf_source/              # Input PDFs for testing
├── references/              # Ground-truth Markdown pages (page_001.md …)
├── experiments/             # Experiment config files (JSON)
├── output/                  # Conversion output and evaluation reports
├── main.py                  # Entry point
├── app.py                   # Main pipeline logic
├── cli.py                   # Argument parsing
├── config.py                # Config dataclass and classification thresholds
├── postprocess.py           # 14-pass Markdown cleanup pipeline
├── postprocess_test.py      # 99 unit tests for postprocessing
├── strategies/
│   ├── adaptive.py          # Per-page classification and routing (core contribution)
│   ├── text_only.py         # Text extraction strategy
│   ├── image_only.py        # Vision/image strategy
│   ├── hybrid.py            # Text + image combined strategy
│   └── result.py            # ConversionResult dataclass
├── extraction/
│   ├── text.py              # PyMuPDF text extraction
│   └── image.py             # PyMuPDF page-to-image rendering
├── llm/
│   ├── client.py            # LM Studio API client
│   └── prompts.py           # Prompt templates per page type
└── evaluation/
    ├── metrics.py           # Metric functions
    ├── compare.py           # Experiment runner
    └── report.py            # Report generator
```

---

## What Has Been Implemented

### Adaptive strategy (core contribution)
- Per-page content classification: `TEXT`, `IMAGE`, `FORMULA`, `MIXED`, `EMPTY`
- Automatic routing to the most appropriate extraction strategy
- Parallelised page conversion; LLM call skipped for plain-text pages

### Postprocessing pipeline (14 passes)
Applied to all output regardless of strategy:

| Pass | What it fixes |
|------|--------------|
| Bold stripping in headings | `## **Title**` → `## Title` |
| Title-page heading demotion | Metadata before first structural section demoted to plain text |
| Chapter heading merging | `## Kapitel N` + `## Title` pairs merged into `# N Title` |
| Duplicate section header removal | Repeated heading immediately following itself removed |
| Bibliography dash stripping | Leading `—` artefacts removed from reference entries |
| LaTeX delimiter normalisation | `\(…\)` and `\[…\]` unified to `$…$` / `$$…$$` |
| Mid-document page number removal | Isolated Arabic digit lines (`3`, `12`) removed |
| Roman numeral page number removal | Isolated front-matter page markers (`v`, `vi`) removed |
| Running header removal | Isolated `Kapitel N Title` and `N.M Title` lines removed |
| Front-matter label removal | Isolated `Inhaltsverzeichnis`, `Abstrakt`, etc. removed mid-document |
| Trailing page number (before separator) | `\n\n42\n\n---` → `\n\n---` |
| Trailing page number (end of file) | Lone digit at end of document removed |
| Blank line normalisation | Runs of 3+ blank lines collapsed to 2 |
| Whitespace trim | Leading/trailing whitespace stripped |

### Evaluation framework
- Experiment runner compares strategies × models × temperatures across multiple PDFs
- Seven metrics computed per page with reference ground truth
- Aggregated Markdown report generation

### Test suite
- 99 unit tests covering every postprocessing function individually
- End-to-end `postprocess_markdown()` integration tests

---

## Known Limitations / Still To Fix

### Easy
- **English "Chapter N" headings not merged** — `## Chapter 1` + `## Introduction` appear as two separate headings instead of `# 1 Introduction`. The merger currently only handles German "Kapitel N".

### Medium
- **Italic abstract subtitle promoted to heading** — some theses style the title in italic below `## Abstract`; pymupdf4llm picks it up as a second H2 (`## _Full Title_`).
- **Numbered code-listing lines become headings** — source code lines like `11 return ''.join(parts)` are misidentified as section headings by the numbering heuristic.
- **Picture-text block markers left in output** — OCR text from scanned figures is wrapped in `**----- Start of picture text -----**` delimiters that should be stripped or reformatted.

### Hard
- **Subscript and inline-math artefacts** — expressions like `( _s_ + 1) _/_ 2` are mangled because pymupdf4llm renders italic/superscript characters as Markdown underscores. No safe regex fix exists without understanding the surrounding math context.
- **Figures not recovered** — diagrams and charts are marked `==> picture [NxN] intentionally omitted <==`. Recovering figure content requires a vision LLM processing the rendered page image; out of scope for the current text-extraction path.

### Out of scope (not a postprocessing problem)
- **Table of contents formatting** — the TOC is extracted as a pipe table with dot-leader characters, which is technically valid Markdown but noisy. Fixing this would require detecting the TOC block and reformatting it.
- **Corpus coverage** — current test PDFs are all academic theses. The evaluation has not yet been run on forms, slides, or scanned documents, which would exercise different classification and extraction paths.
