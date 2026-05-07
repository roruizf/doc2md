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
- [x] P7 — EPUB
- [x] P8 — HTML + TXT + Images
- [x] P9 — Batch Mode
- [x] P10 — VLM (OpenRouter)
- [x] P11a — Packaging
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
P4 completed scanned and mixed PDF routing/OCR. `core.dispatcher.classify_pdf(path)` opens PDFs with PyMuPDF, counts meaningful extractable text per page, and is called by `get_converter("pdf", input_path)` to route to `PdfDigitalConverter`, `PdfScannedConverter`, or `PdfMixedConverter`; `pipeline.run` now passes the input path into dispatcher. The P3 encryption check in `PdfDigitalConverter` still raises `LockedDocument`, but P5 must intercept encrypted PDFs before classification because dispatcher currently opens the file for routing. `Settings` now includes `ocr_lang: str | None` and `ocr_engine: Literal["docling","direct"]`, wired to CLI flags `--ocr-lang` and `--ocr-engine`; scanned PDFs default to Docling OCR with direct Tesseract fallback, while `--ocr-engine=direct` renders pages via PyMuPDF and calls `ocr/tesseract_runner.py`. Existing converters are `PdfDigitalConverter`, `PdfScannedConverter`, and `PdfMixedConverter` in `converters/pdf_mixed.py`; mixed handling combines PyMuPDF digital pages with direct OCR for scanned pages and sets `document_type="mixed"`, `ocr_applied=True`.

### P5 Summary
P5 completed locked PDF handling. PDF routing now checks encryption first in `core.dispatcher.get_converter("pdf", input_path)` via `utils/pdf_unlock.is_encrypted`; encrypted PDFs route to `PdfLockedConverter`, which calls `try_decrypt`, then classifies the decrypted temp file and delegates to `PdfDigitalConverter`, `PdfScannedConverter`, or `PdfMixedConverter`. All PDF subtypes now route correctly: digital, scanned, mixed, and locked; temp decrypted PDFs are used as `image_source_path` during pipeline rendering and cleaned up through converter `cleanup()`. `Settings` fields are now `images_strategy`, `converter_version`, `ocr_lang`, `ocr_engine`, and `password`; `--password` is wired in the CLI and wrong passwords exit 1 with a clear `LockedDocument` message. The rendering pipeline remains shared and stable (`markdown_renderer` + image strategy + sanitizer + validator); converters only need to populate `MarkdownDocument`.

### P6 Summary
P6 completed DOCX and ODT conversion. `DocxConverter` and `OdtConverter` are both wired into `core.dispatcher.get_converter`; DOCX uses Docling as a best-effort primary probe and falls back to `python-docx` for section-aware conversion, heading mapping, GFM table rendering, and ZIP-based image extraction from `word/media/`. ODT uses `pypandoc.convert_file(..., "gfm-raw_html")`, strips pandoc's original media references from body text, and uses pandoc `--extract-media` to copy/rename images into the standard `images/figN_page1.ext` convention. DOCX page synthesis uses one page anchor per section when section breaks exist; if no section breaks are present, `page_count=None` and only section index entries are emitted. The shared rendering pipeline remains unchanged: converters populate `MarkdownDocument`, and pipeline handles frontmatter, images strategy, sanitizer, index, validator, and write-out.

### P7 Summary
P7 completed EPUB conversion. `EpubConverter` is wired in through `core.dispatcher.get_converter("epub")`, uses `ebooklib.epub.read_epub` to read spine-ordered chapter documents, converts chapter XHTML through `markitdown.MarkItDown().convert_stream`, and emits one `Page` per chapter with `document_type="epub"` and EPUB metadata-derived title/language frontmatter. EPUB images are extracted from `ITEM_IMAGE` into the shared `images/figN_pageM.ext` naming convention, using the chapter that references each image or page `0` for global images; `markitdown` is installed and declared in `pyproject.toml` for P8 reuse with HTML. Tests cover three chapter anchors, metadata frontmatter, image extraction, dispatcher routing, and pipeline-rendered Markdown output.

### P8 Summary
P8 completed lightweight format conversion. `HtmlConverter`, `TxtConverter`, and `ImageConverter` are wired through `core.dispatcher.get_converter` for `html`, `txt`, and `image`; HTML uses MarkItDown with a BeautifulSoup/markdownify fallback and extracts local `<img>` assets into the shared `images/figN_page1.ext` convention, TXT uses chardet-based decoding with low-confidence UTF-8 replacement fallback plus heading inference and language detection, and standalone images use PIL plus Tesseract OCR with `document_type="scanned-image"` while copying the source image as figure 1. All converters now work end-to-end for PDF digital/scanned/mixed/locked, DOCX, ODT, EPUB, HTML, TXT, and image; the CLI still accepts only a single file input path, so P9 should add directory input plus recursive batch traversal.

### P9 Summary
P9 completed batch mode. The CLI now accepts either a single file or directory input; directory mode walks supported files with `utils.fs.iter_input_files`, supports `--recursive/-r`, `--flatten`, and `--no-progress`, mirrors or flattens output paths via `utils.fs.mirror_output_path`, wraps conversion with `utils.progress.ProgressBar`, isolates per-file failures, and prints a success/failure/elapsed summary while exiting zero for batch failures so the rest of the batch can complete. Batch mode works for the existing converter set (PDF digital/scanned/mixed/locked, DOCX, ODT, EPUB, HTML, TXT, image) and single-file CLI behavior remains unchanged. `images_strategy` remains fully Settings-driven; `markdown_renderer.render` calls `_render_image`, which builds `ImageMeta` and delegates to `rendering.images_strategy.apply_strategy`, where `vlm` still raises `NotImplementedError` for P10.

### P10 Summary
P10 completed VLM image descriptions. `pyproject.toml` now includes the runtime dependencies `openai`, `httpx`, and `tenacity`, plus optional extra `anthropic = ["anthropic"]`; no version pins were added beyond the existing `docling==2.92.0`. VLM settings are exposed through CLI flags `--vlm-provider`, `--vlm-model`, and `--vlm-cost-threshold`; `pipeline.run` auto-selects `deepseek/deepseek-vl2-small` for general documents and `deepseek/deepseek-ocr-2` for scanned/scanned-image documents, estimates cost via `images.vlm_pricing`, and falls back to placeholders when cost is denied. `rendering.markdown_renderer.render` still calls `_render_image`, which builds `ImageMeta` and delegates to `rendering.images_strategy.apply_strategy`; that strategy now calls `images.vlm_client.VlmClient.describe_image` for `--images=vlm`, caches results under `~/.cache/doc2md/vlm/`, retries 429/5xx responses with tenacity, and falls back to placeholder on terminal VLM failure. Mocked tests cover successful OpenRouter-style responses, retry then success, terminal failure fallback, cache hits, and non-interactive cost denial.

### P11a Summary
P11a completed packaging and install documentation. `pyproject.toml` now has package metadata (`description`, `readme`, MIT license, authors, classifiers), console script `doc2md = "doc2md.cli:main"`, runtime dependencies (`beautifulsoup4`, `chardet`, `docling==2.92.0`, `ebooklib`, `httpx`, `langdetect`, `markitdown`, `openai`, `pillow`, `pytesseract`, `pypandoc`, `python-docx`, `typer`, `pymupdf`, `pyyaml`, `python-magic`, `pydantic>=2`, `markdownify`, `tenacity`, `tqdm`), dev extras, and optional `anthropic = ["anthropic"]`; no new version pins were added beyond the existing Docling pin. `README.md`, `LICENSE`, `Makefile`, `scripts/install_wsl.sh`, `docs/architecture.md`, and `docs/output_schema.md` are in place; README covers install, examples for every format, CLI flags, schema, env vars, and troubleshooting. Build/install was verified with `pip install .` in the project venv and `doc2md --version` returns `0.1.0`; `pipx` was not available in this environment, and a clean `uv` install was stopped because the Docling/PyTorch dependency chain began downloading large CUDA wheels, which is documented as a WSL/Linux caveat.

### P11b Summary
_pending_
