# CLAUDE.md

## General Guidelines

### Write code with unit tests in mind
Prefer dependency injection over hard-coded calls so behaviour can be tested without network or file I/O. Follow the pattern used throughout this project: injectable `llm_call`, `text_call`, `image_call` parameters with the real implementation as the default.

---

## Session Summary (June 2026)

### What was done this session

#### 1. Citation cleanup (all 7 preprint citations resolved)
The professor flagged 7 arXiv preprint citations. All were replaced with peer-reviewed alternatives in `Thesis_Paper/NoorMartini_Thesis.tex`:

| Old key | Replaced with | Venue |
|---|---|---|
| parsing2024 | whitington2012, gao2011, zhu2022 | various peer-reviewed |
| gotocr2024 | blecher2023 + subramani2020 | EMNLP 2023 / ACM Computing Surveys |
| adhikari2024 | meuschke2023 | iConference 2023, Springer LNCS |
| wang2024 | mineru_software | OpenDataLab GitHub |
| cassel2025 | duan2025 | NLDB 2025, Springer LNCS |
| ding2025 | ding2026 | Artificial Intelligence Review 59(4) |
| parsebench2026 | omnidocbench2025 | CVPR 2025 |

`docr_inspector2025` was investigated and found to be arXiv-only — removed entirely.

#### 2. Literature folder cleanup
`Thesis_Paper/Literatures/` was audited. 7 unused PDF/TXT files (old arXiv preprints for removed citations) were deleted. The 3 new paper PDFs were confirmed present.

#### 3. Thesis scope and RQ5 update
- RQ5 renamed from "Generalizability" to "Consistency" (thesis documents only, not four categories)
- Scope section updated: four document category list removed, replaced with thesis-only + language detection detail
- Dataset section updated to reflect thesis-only scope
- `experiments/sample.json` category labels left as `"academic"` (correct for thesis docs)
- `TODO.md` added to `.gitignore` and untracked from git

#### 4. Five thesis errors corrected + missing implementation detail added
Errors fixed in `NoorMartini_Thesis.tex`:
- Scope (line ~332): removed false four-category claim
- Contributions (line ~360): "five types" → "six types", TABLE added
- Ch5.1: "one Markdown string per page" → "one combined document"; sequential → parallel thread pool
- Ch5.3: `fitz.Matrix(2, 2)` → correct 150 DPI formula; bulk extraction explanation improved; page label preservation added
- Ch5.5: added three new postprocessing passes (markdown wrapper stripping, TOC dot-leader cleaning, bare number heading recovery)

#### 5. Dead code removed
`extraction/toc.py` and `extraction/toc_test.py` deleted — `toc.py` was never imported in `app.py`.

#### 6. Postprocessing pipeline improved (4 new passes)
Added to `postprocess.py`, called in `clean_page()`:

- **`_convert_toc_table`** — converts pipe-table TOC pages (both 2-col `| Contents |` format and 3-col `| Chapter | Section | Page |` format) to a clean nested Markdown list
- **`_fix_listing_table`** — converts single-header List of Figures / List of Tables / Listings tables to proper 3-column tables; handles dot-leader debris (the `| ... | ... |` mess on the Listings page)
- **`_fix_table_list_header`** — adds missing `Page` column header and `## List of Tables` heading when the extractor omits them
- **`_convert_abbreviations`** — converts inline bold abbreviation lists (all on one line: `**AI** artificial intelligence **API**...`) to a proper 2-column table

16 new tests added. All 123 postprocess tests pass.

---

### Current code status

**Tests:** 242 passing, 4 pre-existing failures in `strategies/text_only_test.py` (unrelated: `token_usage` returns `0` instead of `None` — needs a live LM Studio run to investigate).

**Branch:** `noor/adaptive` — pushed to GitHub.

**Key files:**
- `postprocess.py` — 14 clean_page passes, 6 postprocess_markdown passes, 123 tests
- `app.py` — adaptive pipeline with ThreadPoolExecutor, bulk extraction, per-page classification
- `extraction/` — classifier, language detection (no toc.py anymore)
- `evaluation/` — compare, metrics, report modules
- `experiments/sample.json` — 3 PDFs, adaptive strategy, qwen2.5-vl-7b model

**What still needs a live LM Studio run:**
- Run the full experiment: `python3 -m evaluation.compare -c experiments/sample.json -o output/results.json`
- Then generate the report: `python3 -m evaluation.report -i output/results.json -o output/report.md`
- Check whether `token_usage` is still null for image/hybrid results

---

### Current thesis status

**File:** `Thesis_Paper/NoorMartini_Thesis.tex`

**Completed chapters:**
- Chapter 1 — Introduction (done)
- Chapter 2 — Foundations (done)
- Chapter 3 — Related Work (done)
- Chapter 4 — Research Design (done)
- Chapter 5 — System Design and Implementation (done, all sections expanded with real implementation detail)

**Blocked chapters (need experiment results):**
- Chapter 6 — Results and Evaluation
- Chapter 7 — Discussion
- Chapter 8 — Conclusion

**All professor feedback applied:**
- 7 preprint citations replaced with peer-reviewed alternatives
- Scope narrowed to bachelor/master thesis documents (4-category list removed)
- RQ5 updated to "Consistency"

**Writing rules (from memory):** short sentences, simple words, no AI buzzwords, keep all detail, patterns from the HITL thesis (short impact sentences, standalone gap paragraphs, 4–6 sentence paragraphs, closing "so what?" sentences).
