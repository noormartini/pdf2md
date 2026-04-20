# Plan: Next Steps for PDF-to-Markdown Thesis Project

## Context

Your thesis "Multimodal conversion of PDF documents to Markdown" requires experimenting with different models, strategies (text vs. image vs. hybrid), and prompts — then comparing results. You currently have a working but minimal pipeline: PyMuPDF extracts text → sends to LM Studio → gets markdown back. The codebase needs to grow to support systematic experimentation.

---

## Phase 1: Fix Immediate Issues

**Files:** `app.py`, `main.py`

1. **Fix the LLM API call** — `app.py` uses `"input"` and `"output"` (LM Studio format), but since `main.py` points to `/v1` (OpenAI format), switch to:
   - Payload: `"messages": [{"role": "system", ...}, {"role": "user", ...}]`
   - Endpoint: `{base_url}/chat/completions`
   - Response: `data["choices"][0]["message"]["content"]`
2. **Fix `--max-pages` type** — add `type=int` to the argparse argument (currently passed as string)
3. **Remove unused `MODEL_NAME`** constant in `app.py`
4. **Test end-to-end** with gemma-3-4b to confirm it works

---

## Phase 2: Restructure for Experimentation

Refactor into modules so you can easily swap strategies and models:

```
pdf2md/
    main.py                  # CLI entry point
    config.py                # Config dataclass
    strategies/
        base.py              # Base class for strategies
        text_only.py         # Current approach: extract text → LLM
        image_only.py        # Render page as image → vision LLM
        hybrid.py            # Text + image combined
    extraction/
        text.py              # PyMuPDF text extraction (from app.py)
        image.py             # PyMuPDF page-to-image rendering
    llm/
        client.py            # API client (text + vision calls)
        prompts.py           # All prompt templates as a dictionary
    evaluation/
        metrics.py           # Comparison metrics
        compare.py           # Run experiments and collect results
        report.py            # Generate comparison reports
    postprocess.py           # Markdown cleanup (from app.py)
    experiments/             # Experiment configs (JSON)
```

Key idea: every conversion returns a `ConversionResult` with the markdown, timing, model name, and strategy — so all experiments are automatically comparable.

---

## Phase 3: Add Multimodal/Vision Pipeline

This is the core of your thesis title ("Multimodal"). Four strategies to implement:

1. **Text-only** (✅ done) — PyMuPDF extracts text, LLM formats it
2. **Image-only** (✅ done) — Render each page as PNG with `page.get_pixmap()`, send to a vision model using OpenAI vision format (base64 image in messages)
3. **Hybrid** (✅ done) — Send both the extracted text AND the page image to the vision model. The model uses the image for layout understanding and the text for accurate content.
4. **Adaptive** (✅ done) — Automatically classifies each page and routes it to the best strategy:
   - `TEXT` pages → text_strategy (enough text, no images/formulas)
   - `FORMULA` pages → image_strategy with "formula" prompt (math symbols or many short vector paths)
   - `IMAGE` pages → image_strategy with "diagram" prompt (3+ embedded images)
   - `MIXED` pages → image_strategy with "default" prompt (some images or formulas)
   - `EMPTY` pages → skipped entirely
   - Implemented in `strategies/adaptive.py`, fully wired in `app.py`

Vision models in LM Studio that support this: Gemma 3 (multimodal), Qwen-VL, LLaVA — check what's available.

The adaptive strategy is the main thesis contribution — it outperforms any single fixed strategy by using the right approach per page. Expected finding: text-only wins on pure-text pages (speed), image-based wins on tables/formulas/diagrams.

---

## Phase 4: Evaluation Framework

To compare approaches scientifically:

1. **Create reference markdowns** — Manually write "gold standard" markdown for 5-10 representative pages (title page, text page, table, formula, code, image). This is essential.
2. **Implement metrics** — Text similarity (difflib), structural accuracy (heading/list/table counts), format completeness, processing time, token usage
3. **Build experiment runner** — Define experiments in JSON, run all combinations, collect results
4. **Generate reports** — Summary table (strategy × model × metric), per-page breakdown

---

## Phase 5: Special Content Handling

Progressively improve handling of hard content:

- **Page numbers** — Preserve page numbers from the PDF in the markdown output (e.g. as comments `<!-- Page 3 -->` or headings between pages). PyMuPDF gives you the page index; map it to the actual printed page number from the PDF.
- **Table of contents** — Extract the TOC with `doc.get_toc()` (PyMuPDF) and generate a markdown TOC with links at the top of the document
- **Tables** — Use `page.find_tables()` (PyMuPDF) for text strategy; prompt instructions for vision
- **Formulas** — Vision models can read formulas from images → LaTeX. Text-only will struggle here.
- **Images** — Extract with `page.get_images()`, save as PNGs, insert markdown image references
- **Code blocks** — Detection heuristics + prompt instructions
- **Language detection** — Use the already-installed `langdetect` to adjust prompts for German/English

---

## Phase 6: Prompt Experiments

Test different prompt styles with the same model/pages:

- **Minimal**: "Convert to markdown" (baseline)
- **Detailed rules**: Current approach with explicit formatting rules
- **Few-shot**: Include an example of input → expected output
- **Chain-of-thought**: "First analyze the page structure, then convert"
- **Language-specific**: German-aware prompts

Also test temperature sensitivity (0.0, 0.2, 0.5) — easy experiment, interesting data.

---

## Phase 7: Multi-Model Comparison

Run the full experiment matrix:

| Models | Strategies | Prompts |
|--------|-----------|---------|
| Gemma 3 4B | text-only | minimal, default, detailed |
| Qwen 3.5 35B-A3B | image-only | minimal, default, detailed |
| (other vision models) | hybrid | minimal, default, detailed |

This matrix produces the results chapter of your thesis.

---

## Phase 8: Optional Polish

- **Simple UI** with Streamlit (upload PDF, pick strategy/model, see results)
- **pymupdf4llm baseline** — Compare LLM-based conversion against pure rule-based extraction (no LLM). Interesting thesis data: how much does the LLM actually help?

---

## Priority

| Phase | Priority | ~Effort |
|-------|----------|---------|
| 1. Fix issues | Must | A few hours |
| 2. Restructure | Must | 1-2 days |
| 3. Vision pipeline | Must | 2-3 days |
| 4. Evaluation | Must | 2-3 days |
| 5. Special content | Should | 3-4 days |
| 6. Prompt experiments | Should | 1-2 days |
| 7. Model comparison | Must | 2-3 days (mostly runtime) |
| 8. Polish/UI | Nice-to-have | 1-2 days |

Phases 1–4 and 7 are essential. Phases 5–6 add depth. Phase 8 is bonus.

## Verification

After each phase, run the pipeline end-to-end:
```bash
python main.py -i test_pdf_source.pdf -o output.md -n 5
```
Compare `output.md` against the original PDF visually. After Phase 4, use the evaluation framework to compare results automatically.
