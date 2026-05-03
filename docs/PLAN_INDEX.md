# doc2md — Plan Index

## Working Documents
- [EXECUTION_PLAN.md](./EXECUTION_PLAN.md) — Step-by-step multi-agent execution plan (canonical reference)
- [architecture.md](./architecture.md) — Architecture notes (populated in P11b)
- [output_schema.md](./output_schema.md) — Output schema reference (populated in P11b)
- [performance.md](./performance.md) — Benchmark results (populated in P11b)

## Current Status
- [x] P0 — Environment Setup
- [ ] P1 — Core Skeleton + PDF Digital MVP
- [ ] P2 — Rendering Layer
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
_pending_

### P2 Summary
_pending_

### P3 Summary
_pending_

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
