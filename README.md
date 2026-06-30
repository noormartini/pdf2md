# PDF2MD — Adaptive PDF-to-Markdown Converter

Bachelor's thesis project. Converts PDF documents to Markdown using local LLMs via LM Studio. Each page is automatically analysed and routed to the most appropriate extraction strategy based on its content type.

---

## How It Works

1. **Analyse** — each PDF page is inspected with PyMuPDF to detect its content type (text, image, formula, table, mixed, or empty)
2. **Extract** — text pages have their Markdown extracted directly with pymupdf4llm; all other pages are rendered as PNG screenshots
3. **Convert** — image pages are sent to a local vision LLM in LM Studio, which returns clean Markdown
4. **Post-process** — over 20 per-page cleanup passes plus 10 document-level passes normalise headings, fix tables, remove extraction artefacts, and produce a single `.md` file

---

## Strategies

| Strategy | How it works | Best for |
|----------|-------------|----------|
| `text` | Extracts raw text with pymupdf4llm | Clean text-only documents |
| `image` | Renders every page as PNG → vision LLM | Image-heavy documents |
| `hybrid` | Sends both text and image to vision LLM | Mixed-content documents |
| `adaptive` | Auto-detects page type, picks best strategy per page | Full thesis documents |

The **adaptive** strategy is the core thesis contribution. It classifies each page and routes accordingly:

- `TEXT` → pymupdf4llm extraction, no LLM call
- `TABLE` → rendered as PNG, table-specific prompt → vision LLM
- `FORMULA` → rendered as PNG, formula-specific prompt → vision LLM
- `IMAGE` → rendered as PNG, diagram-specific prompt → vision LLM
- `MIXED` → rendered as PNG, general prompt → vision LLM
- `EMPTY` → skipped

Pages are processed in parallel using a `ThreadPoolExecutor`.

---

## Requirements

- Python 3.12+
- [LM Studio](https://lmstudio.ai) running locally with a vision-capable model loaded
- Recommended model: **Qwen2.5-VL-7B**

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

LM Studio must be running with a model loaded before running any command.

```bash
# default: adaptive strategy
python3 main.py

# specify a PDF and strategy
python3 main.py -i pdf_source/thesis.pdf -s adaptive

# limit to first 20 pages
python3 main.py -i pdf_source/thesis.pdf -s adaptive -n 20

# override model
python3 main.py -i pdf_source/thesis.pdf -s adaptive -m qwen/qwen2.5-vl-7b
```

Output is saved to `output/test_pdf_output.md` by default.

### Single-file version

`project.py` is a self-contained single-file version of the entire pipeline — no imports from other modules required.

```bash
python3 project.py -i pdf_source/thesis.pdf -o output/result.md -s adaptive -n 20
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-i` / `--input` | `pdf_source/test_pdf_source.pdf` | Input PDF file |
| `-o` / `--output` | `output/test_pdf_output.md` | Output Markdown file |
| `-s` / `--strategy` | `text` | Strategy: `text`, `image`, `hybrid`, `adaptive` |
| `-m` / `--model` | `qwen/qwen2.5-vl-7b` | Model name as loaded in LM Studio |
| `-b` / `--base-url` | `http://127.0.0.1:1234/v1` | LM Studio API base URL |
| `-n` / `--max-pages` | `3` | Maximum number of pages to convert |
| `-t` / `--temperature` | `0.2` | LLM sampling temperature (0.0 = deterministic) |
| `-T` / `--max-tokens` | `4096` | Maximum tokens in LLM response |
| `-c` / `--concurrency` | `4` | Number of parallel worker threads |

---

## Running Tests

```bash
pytest postprocess_test.py
```

147 tests cover all postprocessing functions individually as well as end-to-end `postprocess_markdown()` behaviour.

---

## Evaluation

Run a comparison experiment across strategies, models, and temperatures:

```bash
# run experiments (requires LM Studio running)
python3 -m evaluation.compare -c experiments/sample.json -o output/results.json

# generate markdown report from results
python3 -m evaluation.report -i output/results.json -o output/report.md
```

The experiment config (`experiments/sample.json`) controls which PDFs, strategies, models, prompt variants, and temperatures to compare. Reference ground-truth pages are stored in `references/`.

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
├── references/              # Ground-truth Markdown pages (hand-corrected)
├── experiments/             # Experiment config files (JSON)
├── output/                  # Conversion output and evaluation reports
├── main.py                  # Entry point (multi-module version)
├── project.py               # Self-contained single-file version of the pipeline
├── app.py                   # Main pipeline logic
├── cli.py                   # Argument parsing
├── config.py                # Config dataclass and classification thresholds
├── postprocess.py           # Multi-pass Markdown cleanup pipeline
├── postprocess_test.py      # 147 unit tests for postprocessing
├── strategies/
│   ├── adaptive.py          # Per-page classification and routing (core contribution)
│   ├── text_only.py         # Text extraction strategy
│   ├── image_only.py        # Vision/image strategy
│   ├── hybrid.py            # Text + image combined strategy
│   └── result.py            # ConversionResult dataclass
├── extraction/
│   ├── text.py              # PyMuPDF text extraction
│   ├── image.py             # PyMuPDF page-to-image rendering
│   └── language.py          # Document language detection (German / English)
├── llm/
│   ├── client.py            # LM Studio API client
│   └── prompts.py           # Prompt templates per page type and language
└── evaluation/
    ├── metrics.py           # Metric functions
    ├── compare.py           # Experiment runner
    └── report.py            # Report generator
```

---

## What Has Been Implemented

### Adaptive strategy (core contribution)
- Per-page content classification: `TEXT`, `IMAGE`, `FORMULA`, `TABLE`, `MIXED`, `EMPTY`
- Automatic routing: text pages bypass the LLM entirely; all other types go to the vision LLM with a typed prompt
- Parallelised page conversion with `ThreadPoolExecutor`
- Bulk text extraction with pymupdf4llm once per document (avoids O(N²) font-histogram rescanning)
- Document language detection; prompts sent in the detected language

### Postprocessing pipeline
Applied in two stages: per-page passes inside `clean_page()`, then document-level passes inside `postprocess_markdown()`.

Selected passes:

| Pass | What it fixes |
|------|--------------|
| Bold stripping in headings | `## **Title**` → `## Title` |
| Space before colon in labels | `**Schmitt, Steven :**` → `**Schmitt, Steven:**` |
| Declaration heading promotion | Standalone `Erklärung / Declaration` promoted to `##` heading |
| Listing title promotion | `**Listings**` as bold text → `## Listings` |
| TOC dot-leader cleaning | `. . . . . 32` artefacts removed from table-of-contents cells |
| TOC table conversion | Pipe-table TOC → clean nested Markdown list |
| List of Figures/Tables repair | Dot-leader page numbers recovered from raw text; missing headers added |
| Listings table repair | Dot-leader debris in Listings page cleaned to proper 3-column table |
| Abbreviation table conversion | Inline bold abbreviation lists → 2-column Markdown table |
| Greek letter → LaTeX | `_φ_` → `$\varphi$` |
| OCR superscript cleanup | Citation markers like `[1]` extracted from garbled OCR runs |
| Figure caption formatting | Captions normalised; reordered after their image when extracted before |
| Chapter heading merging | `# Chapter N` + `## Title` pairs merged into `# Chapter N: Title` |
| Title-page heading demotion | Metadata before first structural section demoted to plain text |
| Bibliography dash stripping | Leading and trailing `—` artefacts removed from citation entries |
| Picture-text block removal | Tesseract OCR noise from embedded figure images dropped |
| Running header removal | Repeated chapter/section titles at top of each page stripped |
| Mid-document page number removal | Isolated page-footer numbers removed |

### Evaluation framework
- Experiment runner compares strategies × models × temperatures across multiple PDFs
- Seven metrics computed per page with hand-corrected reference ground truth
- Aggregated Markdown report generation

### Test suite
- 147 unit tests covering every postprocessing function individually
- End-to-end `postprocess_markdown()` integration tests

---

## Known Limitations

### Medium
- **Subscript and inline-math artefacts** — expressions like `( _s_ + 1) _/_ 2` are mangled because pymupdf4llm renders italic/superscript characters as Markdown underscores. No safe regex fix exists without understanding the surrounding math context.
- **Bibliography dash mid-sentence** — in German bibliography format the em-dash separator sometimes ends up in the middle of a title string rather than at the end of the authorship line, depending on where the PDF line break falls. The trailing-dash case is handled; the mid-sentence case is not.

### Hard / Out of scope
- **LLM output quality** — the vision LLM occasionally misreads page numbers in List of Tables/Figures, confuses listing numbers with page numbers, or omits post-table text. These are model-quality issues, not postprocessing problems.
- **Figures in text-strategy path** — diagrams and charts are marked `==> picture [NxN] intentionally omitted <==` when using the text strategy. The adaptive strategy avoids this by routing image pages to the vision LLM.
