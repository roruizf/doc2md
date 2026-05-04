# doc2md — Plan Index

## Working Documents
- [EXECUTION_PLAN.md](./EXECUTION_PLAN.md) — Step-by-step multi-agent execution plan (canonical reference)
- [architecture.md](./architecture.md) — Architecture notes (populated in P11b)
- [output_schema.md](./output_schema.md) — Output schema reference (populated in P11b)
- [performance.md](./performance.md) — Benchmark results (populated in P11b)

## Current Status
- [x] P0 — Environment Setup
- [x] P1 — Core Skeleton + PDF Digital MVP
- [x] P2 — Rendering Layer
- [ ] P3 — Docling Integration
- [ ] P4 — Scanned PDFs (OCR)
- [ ] P5 — Locked PDFs
- [ ] P6 — DOCX + ODT
- [ ] P7 — EPUB
- [ ] P8 — HTML + TXT + Images
- [ ] P9 — Batch Mode
- [ ] P10 — VLM (OpenRouter)
- [ ] P11a — Packaging
- [ ] P11b — Quality + CI

## Phase Summaries
(Each agent appends their Phase Summary here after completing their phase)

### P0 Summary
P0 completed with a project-local `.venv` created by `uv` using Python 3.11.13. The fixture generator is at `scripts/generate_fixtures.py` and can be re-run with `.venv/bin/python scripts/generate_fixtures.py`; it generated and confirmed all 11 fixtures: `sample_digital.pdf`, `sample_multicolumn.pdf`, `sample_scanned.pdf`, `sample_locked.pdf`, `sample_mixed.pdf`, `sample.docx`, `sample.odt`, `sample.epub`, `sample.html`, `sample.txt`, and `sample_image.png`. System binaries are reachable at `/usr/bin/tesseract`, `/usr/bin/qpdf`, `/usr/bin/pandoc`, and `/usr/bin/pdftoppm`; `qpdf --version` reports 10.6.3. `requirements.txt` captures the P0 fixture/tooling dependencies for reproducible setup with `uv pip install -r requirements.txt`.

### P1 Summary
P1 completed the core Python package skeleton and PDF digital MVP. The canonical document models are `Frontmatter`, `IndexEntry`, `Page`, and `MarkdownDocument` with fields matching §4; `validate(doc) -> ValidationResult` is implemented and called by `pipeline.run` before writing output. The dispatcher returns `PdfDigitalConverter` for `pdf` only, while unsupported formats raise `UnsupportedFormat`; the pipeline currently renders YAML frontmatter and page anchors inline, to be replaced by `markdown_renderer` in P2. `PdfDigitalConverter` extracts per-page text with PyMuPDF and sets `document_type="digital"` / `ocr_applied=False`, but intentionally does not extract images yet; P2 should add image handling and populate richer `index_entries`.

### P2 Summary
P2 completed the rendering layer and image extraction path. `markdown_renderer.render(doc, output_path, extracted_images, settings) -> str` now composes frontmatter, page anchors, sanitized body content, page image references, and the end-of-document index; `pipeline.run` calls PyMuPDF image extraction for PDFs before rendering, then calls `validate(doc, rendered_markdown=..., output_path=...)` so image references are checked relative to the output file. `PdfDigitalConverter` still uses PyMuPDF only: text comes from `page.get_text("text")`, table detection is best-effort via `page.find_tables()`, and image extraction remains centralized in `images/extractor.py` for reuse by P3. P3 should keep the `MarkdownDocument` model fields `frontmatter`, `pages`, and `index_entries`; it should populate richer heading hierarchy in `Page.content` and add `IndexEntry(kind="section", label, anchor_id)` entries while preserving page/table/figure entries.

### P3 Summary
P3 completed Docling integration for digital PDFs. `PdfDigitalConverter` now uses Docling as the primary path with `PdfPipelineOptions(do_ocr=False, accelerator_options=CPU)` and falls back to the previous PyMuPDF raw extraction path when Docling raises, setting `fallback_used=True` and logging `Docling failed (...), falling back to PyMuPDF raw extraction`; PyMuPDF remains responsible for encryption checks, page count, fallback extraction, and shared image extraction through `images/extractor.py`. The dispatcher still routes every detected `"pdf"` to `PdfDigitalConverter`; P4 must split scanned vs digital routing there or behind that converter. Docling is installed and working in the venv with an explicit `docling==2.92.0` dependency; tests confirm multicolumn reading order, heading rendering, section `IndexEntry` population, and fallback behavior.

### P4 Summary
_pending_

### P5 Summary
_pending_

### P6 Summary
_pending_

### P7 Summary
_pending_

### P8 Summary
_pending_

### P9 Summary
_pending_

### P10 Summary
_pending_

### P11a Summary
_pending_

### P11b Summary
_pending_
