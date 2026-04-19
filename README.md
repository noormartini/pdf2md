# Multimodal PDF-to-Markdown Converter

Bachelor's thesis project — converts PDF documents to Markdown using local LLMs via LM Studio. Each page is automatically analysed and routed to the most appropriate extraction strategy based on its content type.

---

## How It Works

1. **Analyse** — each PDF page is inspected with PyMuPDF to detect its content type (text, image, formula, mixed, or empty)
2. **Extract** — text pages have their text extracted directly; image/formula/mixed pages are rendered as PNG screenshots
3. **Convert** — the extracted content is sent to a local LLM in LM Studio, which returns clean Markdown
4. **Post-process** — the output is cleaned and all pages are joined into a single `.md` file

---

## Strategies

| Strategy | How it works | Best for |
|----------|-------------|----------|
| `text` | Extracts raw text → sends to LLM | Clean text-only pages |
| `image` | Renders page as PNG → sends to vision LLM | Image-heavy pages |
| `hybrid` | Sends both text and image to vision LLM | Mixed content |
| `adaptive` | Auto-detects page type, picks the best strategy per page | Full documents |

The **adaptive** strategy is the main thesis contribution. It classifies each page:
- `TEXT` → uses text strategy
- `FORMULA` → renders as image, uses formula-specific prompt
- `IMAGE` → renders as image, uses diagram-specific prompt
- `MIXED` → renders as image, uses general prompt
- `EMPTY` → skipped

---

## Requirements

- Python 3.12+
- [LM Studio](https://lmstudio.ai) running locally with a vision-capable model loaded
- Recommended models: **Gemma 3** (multimodal), **Qwen 3.5 35B-A3B**

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py -i yourfile.pdf -o output.md -s adaptive -m google/gemma-3-4b
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `-i` / `--input` | `test_pdf_source.pdf` | Input PDF file |
| `-o` / `--output` | `output/test_pdf_output.md` | Output Markdown file |
| `-s` / `--strategy` | `text` | Strategy: `text`, `image`, `hybrid`, `adaptive` |
| `-m` / `--model` | `google/gemma-3-4b` | Model name loaded in LM Studio |
| `-b` / `--base-url` | `http://127.0.0.1:1234/v1` | LM Studio API base URL |
| `-n` / `--max-pages` | `3` | Max number of pages to convert |
| `-t` / `--temperature` | `0.2` | LLM temperature (0.0 = deterministic) |
| `-T` / `--max-tokens` | `4096` | Max tokens in LLM response |

---

## Project Structure

```
thesis-pdf-to-markdown/
├── main.py                  # Entry point
├── app.py                   # Main pipeline logic
├── cli.py                   # Argument parsing
├── config.py                # Config dataclass + thresholds
├── postprocess.py           # Markdown cleanup
├── strategies/
│   ├── adaptive.py          # Per-page auto-detection (core thesis contribution)
│   ├── text_only.py         # Text extraction strategy
│   ├── image_only.py        # Vision/image strategy
│   ├── hybrid.py            # Text + image combined strategy
│   └── result.py            # ConversionResult dataclass
├── extraction/
│   ├── text.py              # PyMuPDF text extraction
│   └── image.py             # PyMuPDF page-to-image rendering
├── llm/
│   ├── client.py            # LM Studio API client
│   └── prompts.py           # Prompt templates
├── evaluation/
│   ├── metrics.py           # Scoring metrics (text similarity, structure, etc.)
│   ├── compare.py           # Experiment runner
│   └── report.py            # Report generator
└── experiments/             # Experiment config files (JSON)
```

---

## Evaluation

Run experiments comparing all strategies across models and pages:

```bash
python -m evaluation.compare -c experiments/sample.json -o output/results.json
python -m evaluation.report -i output/results.json -o output/report.md
```

Metrics used: text similarity, heading structure, list structure, table detection, code block accuracy, paragraph count, word overlap.
