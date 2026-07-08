# PDF2MD — Adaptive PDF-to-Markdown Converter

Bachelor's thesis project. Converts PDF documents to Markdown using local LLMs via LM Studio. Each page is automatically analysed and routed to the most appropriate extraction strategy based on its content type.

---

## How It Works

1. **Analyse** — each PDF page is inspected with PyMuPDF to detect its content type (text, image, formula, table, mixed, or empty)
2. **Extract** — text pages have their Markdown extracted directly with pymupdf4llm; all other pages are rendered as PNG screenshots
3. **Convert** — image pages are sent to a local vision LLM in LM Studio, which returns clean Markdown
4. **Post-process** — 38 cleanup passes normalise headings, fix tables, remove extraction artefacts, and produce a single `.md` file

---

## Requirements

- Python 3.12+
- [LM Studio](https://lmstudio.ai) running locally with a vision-capable model loaded
- Recommended model: **Qwen2.5-VL-7B**

```bash
pip install -r requirements.txt
```

---

## Quick Start

Start LM Studio, load a vision model, then:

```bash
# convert a PDF using the adaptive strategy (recommended)
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result.md -s adaptive
```

---

## Strategies

| Strategy | How it works | Best for |
|----------|-------------|----------|
| `text` | Extracts raw text with pymupdf4llm — no LLM | Fast, clean text-only documents |
| `image` | Renders every page as PNG → vision LLM | Image-heavy documents |
| `hybrid` | Sends both text and image to vision LLM | Mixed-content documents |
| `adaptive` | Auto-detects page type, picks best strategy per page | Full thesis documents (recommended) |

The **adaptive** strategy is the core thesis contribution. It classifies each page and routes accordingly:

- `TEXT` → pymupdf4llm extraction, no LLM call
- `TABLE` → rendered as PNG, table-specific prompt → vision LLM
- `FORMULA` → rendered as PNG, formula-specific prompt → vision LLM
- `IMAGE` → rendered as PNG, diagram-specific prompt → vision LLM
- `MIXED` → rendered as PNG, general prompt → vision LLM
- `EMPTY` → skipped

---

## All Commands

### Convert each PDF (full document)

```bash
# Sentiment analysis thesis
python3 main.py \
  -i pdf_source/test_pdf_source.pdf \
  -o output/sentiment_thesis.md \
  -s adaptive

# HITL thesis
python3 main.py \
  -i "pdf_source/A_human_in_the_loop_system_for_research_paper_generation_using_local_large_language_models.pdf" \
  -o output/hitl_thesis.md \
  -s adaptive

# Neural networks thesis
python3 main.py \
  -i pdf_source/Bachelor_Thesis_Informatik_Koehler_Sven.pdf \
  -o output/koehler_thesis.md \
  -s adaptive
```

### Convert first N pages only

```bash
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result.md -s adaptive -n 20
```

### Try each strategy on a PDF

```bash
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result_text.md    -s text
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result_image.md   -s image
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result_hybrid.md  -s hybrid
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result_adaptive.md -s adaptive
```

### Use a different model

```bash
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result.md -s adaptive \
  -m your-model-name-in-lmstudio
```

### Deterministic output (for reproducible results)

```bash
python3 main.py -i pdf_source/test_pdf_source.pdf -o output/result.md -s adaptive -t 0.0
```

---

## Evaluation Experiment

Runs all four strategies on all three PDFs, computes seven metrics per page against hand-written reference files, and produces a comparison report.

**Requires LM Studio running with Qwen2.5-VL-7B loaded.**

```bash
# step 1 — run the experiment (takes ~30–60 min)
python3 -m evaluation.compare -c experiments/sample.json -o output/results.json

# step 2 — generate the Markdown report
python3 -m evaluation.report -i output/results.json -o output/report.md
```

The experiment config (`experiments/sample.json`) controls which PDFs, strategies, models, and temperatures to compare. Reference ground-truth pages are in `references/`.

### Metrics computed per page

| Metric | What it measures |
|--------|-----------------|
| Text similarity | Character-level overlap with reference (difflib) |
| Heading structure | H1/H2/H3 count match vs. reference |
| List structure | Bullet and numbered list fidelity |
| Table detection | Presence and count of Markdown tables |
| Code block accuracy | Fenced code block match |
| Paragraph count | Paragraph count vs. reference (20% tolerance) |
| Word overlap | Bag-of-words Jaccard similarity |

---

## Running Tests

```bash
pytest postprocess_test.py
```

147 tests cover all postprocessing functions individually and end-to-end `postprocess_markdown()` behaviour.

---

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-i` / `--input` | `pdf_source/test_pdf_source.pdf` | Input PDF file |
| `-o` / `--output` | `output/test_pdf_output.md` | Output Markdown file |
| `-s` / `--strategy` | `text` | Strategy: `text`, `image`, `hybrid`, `adaptive` |
| `-m` / `--model` | `qwen2.5-vl-7b-instruct-abliterated` | Model name as loaded in LM Studio |
| `-b` / `--base-url` | `http://127.0.0.1:1234/v1` | LM Studio API base URL |
| `-n` / `--max-pages` | entire PDF | Maximum number of pages to convert |
| `-t` / `--temperature` | `0.2` | LLM sampling temperature (0.0 = deterministic) |
| `-T` / `--max-tokens` | `4096` | Maximum tokens in LLM response |
| `-c` / `--concurrency` | `4` | Number of parallel worker threads |

---

## Project Structure

```
PDF2MD/
├── pdf_source/              # Input PDFs
├── references/              # Hand-written ground-truth Markdown pages
├── experiments/             # Experiment config files (JSON)
├── output/                  # Conversion output and evaluation reports
├── main.py                  # Entry point
├── app.py                   # Main pipeline logic
├── cli.py                   # Argument parsing
├── config.py                # Config dataclass and classification thresholds
├── postprocess.py           # 38-pass Markdown cleanup pipeline
├── postprocess_test.py      # 147 unit tests for postprocessing
├── strategies/
│   ├── adaptive.py          # Per-page classification and routing (core contribution)
│   ├── text_only.py         # Text extraction strategy
│   ├── image_only.py        # Vision/image strategy
│   ├── hybrid.py            # Text + image combined strategy
│   └── result.py            # ConversionResult dataclass
├── extraction/
│   ├── text.py              # PyMuPDF text extraction with font-size heading detection
│   ├── image.py             # PyMuPDF page-to-image rendering
│   └── language.py          # Document language detection
├── llm/
│   ├── client.py            # LM Studio API client
│   └── prompts.py           # Prompt templates per page type and language
└── evaluation/
    ├── metrics.py           # Metric functions
    ├── compare.py           # Experiment runner
    └── report.py            # Report generator
```

---

## Known Limitations

- **Scanned PDFs** — the page classifier relies on the PDF text layer. Image-path strategies can still process scanned pages (they render to PNG), but the classifier thresholds were designed for native PDFs. Scanned documents are not part of the evaluation.
- **Subscript and inline-math artefacts** — expressions like `(_s_ + 1) _/_ 2` are mangled because pymupdf4llm renders italic/superscript characters as Markdown underscores. No safe regex fix without math context.
- **Figures in text strategy** — diagrams are marked `==> picture [NxN] intentionally omitted <==`. The adaptive strategy avoids this by routing image pages to the vision LLM.
