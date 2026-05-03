# doc2md — Step-by-Step Execution Document

This document is the working reference for multi-agent execution of the doc2md project. It replaces the prior plan. Each phase is a self-contained block to be handed to a single LLM agent in its own session.

---

## Session Handoff Protocol

doc2md is built across many independent agent sessions. To keep token cost low and prevent context drift, **each agent receives only its own phase block plus minimal shared references** — never the full execution document.

When starting a new agent session, paste exactly:

1. **The phase block for that phase** (one of P0..P11b below)
2. **§1 Project Structure** (the full tree)
3. **§4 Output Schema** (the full schema section)
4. **§5 Quality Gates** (the full gates section)
5. **The Phase Summary from the previous phase agent** (1 short paragraph — the only state transfer between sessions)

Do **not** paste this entire document into any single agent session. The Phase Summary from the previous agent is the load-bearing handoff: it must contain the key facts the next agent needs (e.g., "validator returns ValidationResult(valid, warnings); pipeline calls validator before render; frontmatter schema_version is 1.0"). If the Phase Summary is missing or unclear, the orchestrator (the human) should produce it from the prior agent's deliverables before starting the next phase.

**Recommended workflow per phase:**
1. Paste the inputs listed above into a fresh agent session
2. Let the agent execute the phase to completion (passing all quality gates)
3. Capture the Phase Summary the agent delivers
4. **Commit the code** to git before starting the next phase (so a failed phase can be rolled back without losing the previous one)
5. Hand the Phase Summary to the next agent's session

---

## Inter-Phase Dependency Graph

```
P0 (env setup, human checklist)
 │
 └─► P1 (skeleton + PDF digital MVP + validator)
      │
      └─► P2 (rendering layer + image strategies)
           │
           ├─► P3 (Docling for digital PDF)
           │    │
           │    └─► P4 (scanned PDF OCR)
           │         │
           │         └─► P5 (locked PDF — uses P3 + P4)
           │
           └─► P6 (DOCX + ODT)
                │
                └─► P7 (EPUB)
                     │
                     └─► P8 (HTML + TXT + image)
                          │
                          └─► P9 (batch mode)
                               │
                               └─► P10 (VLM via OpenRouter)
                                    │
                                    └─► P11a (packaging)
                                         │
                                         └─► P11b (quality + CI)
```

**Theoretically parallelizable** (after P2 completes): P3-chain (P3→P4→P5) and P6-chain (P6→P7→P8) can be developed in parallel by separate agents — they touch disjoint converters. P9 onward must be serial because they depend on the converter set being complete.

For a single-developer flow, run strictly serial top-to-bottom — simpler handoffs.

---

## §1 Project Structure (canonical reference for all phases)

```
doc2md/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .python-version
├── Makefile
│
├── scripts/
│   ├── install_wsl.sh              # System deps + pipx install + verify
│   └── generate_fixtures.py        # Programmatically generates all test fixtures
│
├── src/
│   └── doc2md/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── config.py
│       ├── logging_setup.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── base_converter.py
│       │   ├── document.py
│       │   ├── detector.py
│       │   ├── dispatcher.py
│       │   ├── pipeline.py
│       │   ├── validator.py
│       │   └── exceptions.py
│       │
│       ├── converters/
│       │   ├── __init__.py
│       │   ├── pdf_digital.py
│       │   ├── pdf_scanned.py
│       │   ├── pdf_locked.py
│       │   ├── docx.py
│       │   ├── odt.py
│       │   ├── epub.py
│       │   ├── html.py
│       │   ├── txt.py
│       │   └── image.py
│       │
│       ├── rendering/
│       │   ├── __init__.py
│       │   ├── markdown_renderer.py
│       │   ├── frontmatter.py
│       │   ├── page_anchors.py
│       │   ├── table_renderer.py
│       │   ├── index_builder.py
│       │   ├── images_strategy.py
│       │   └── sanitizer.py
│       │
│       ├── images/
│       │   ├── __init__.py
│       │   ├── extractor.py
│       │   ├── vlm_client.py
│       │   ├── vlm_pricing.py
│       │   └── naming.py
│       │
│       ├── ocr/
│       │   ├── __init__.py
│       │   └── tesseract_runner.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── fs.py
│           ├── progress.py
│           ├── pdf_unlock.py
│           └── text_heuristics.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── sample_digital.pdf
│   │   ├── sample_scanned.pdf
│   │   ├── sample_locked.pdf
│   │   ├── sample_mixed.pdf
│   │   ├── sample_multicolumn.pdf
│   │   ├── sample.docx
│   │   ├── sample.odt
│   │   ├── sample.epub
│   │   ├── sample.html
│   │   ├── sample.txt
│   │   └── sample_image.png
│   ├── unit/
│   │   ├── test_detector.py
│   │   ├── test_dispatcher.py
│   │   ├── test_validator.py
│   │   ├── test_frontmatter.py
│   │   ├── test_table_renderer.py
│   │   ├── test_index_builder.py
│   │   ├── test_page_anchors.py
│   │   ├── test_sanitizer.py
│   │   └── test_images_strategy.py
│   ├── converters/
│   │   ├── test_pdf_digital.py
│   │   ├── test_pdf_scanned.py
│   │   ├── test_pdf_locked.py
│   │   ├── test_docx.py
│   │   ├── test_odt.py
│   │   ├── test_epub.py
│   │   ├── test_html.py
│   │   ├── test_txt.py
│   │   └── test_image.py
│   └── integration/
│       ├── test_cli_single_file.py
│       ├── test_cli_batch.py
│       ├── test_full_pipeline.py
│       └── test_vlm_mocked.py
│
└── docs/
    ├── architecture.md
    ├── output_schema.md
    ├── performance.md               # P11b benchmark documentation
    └── examples/
```

---

## §4 Output Schema (canonical reference for all phases)

### Required frontmatter fields

```yaml
schema_version: "1.0"
title: string
source_file: string
format: string                  # pdf|docx|odt|epub|html|txt|image
page_count: int | null          # null when synthesized (e.g., HTML, TXT, DOCX without sections)
date_converted: ISO 8601 string
document_type: string           # digital|scanned|mixed|scanned-image|html|txt|epub|docx|odt
language: string | null
ocr_applied: bool
images_strategy: string         # placeholder|vlm|omit
converter_version: string
```

### Anchor format (fixed)
`<a id="page-N"></a>` immediately followed by `**[Page N]**` on the next line.

### Output template — 3-page digital PDF with one table (page 2) and one image (page 3)

```markdown
---
schema_version: "1.0"
title: "Annual Report 2025"
source_file: "annual_report_2025.pdf"
format: "pdf"
page_count: 3
date_converted: "2026-05-03T18:15:00+07:00"
document_type: "digital"
language: "en"
ocr_applied: false
images_strategy: "placeholder"
converter_version: "0.1.0"
---

<a id="page-1"></a>
**[Page 1]**

# Annual Report 2025

## Executive Summary

This report covers the fiscal year 2025 results...

<a id="page-2"></a>
**[Page 2]**

## Financial Highlights

| Quarter | Revenue (M$) | Growth (%) |
|---------|--------------|------------|
| Q1      | 12.4         | +5.2       |
| Q2      | 14.1         | +13.7      |
| Q3      | 15.8         | +12.1      |
| Q4      | 17.2         | +8.9       |

The thermal coefficient `$U = 0.35 W/m²K$` remained stable.

<a id="page-3"></a>
**[Page 3]**

## Outlook

![Figure 1 — Projected revenue growth chart](images/fig1_page3.png)

We anticipate continued growth into 2026...

---

## Document Index

### Pages
- [Page 1](#page-1) — Executive Summary
- [Page 2](#page-2) — Financial Highlights
- [Page 3](#page-3) — Outlook

### Sections
- [Annual Report 2025](#page-1)
  - [Executive Summary](#page-1)
  - [Financial Highlights](#page-2)
  - [Outlook](#page-3)

### Tables
- Table 1 — Quarterly performance ([Page 2](#page-2))

### Figures
- Figure 1 — Projected revenue growth chart ([Page 3](#page-3))
```

### Sanitization rules (`rendering/sanitizer.py`)
- LaTeX-like expressions (`$...$`, `\(...\)`, `\[...\]`) preserved inside backtick code spans
- Unicode dashes (`—`, `–`) → ASCII (`--`, `-`) outside code spans
- Smart quotes (`"`, `"`, `'`, `'`) → ASCII (`"`, `'`)
- Replaced characters logged at INFO with counts

### Validation rules (`core/validator.py`)
- All required frontmatter fields present and non-empty (except nullable ones)
- Page anchors sequential from 1 to `page_count` (when non-null)
- Every index entry references an anchor that exists
- Returns `ValidationResult(valid: bool, warnings: list[str])` — never blocks output, logs warnings

---

## §5 Quality Gates (mandatory at end of every phase)

Every phase agent MUST, before declaring the phase done:

1. Run `ruff check src/ tests/` and fix all errors
2. Run `mypy src/doc2md` — no new type errors on phase's files
3. Run `pytest tests/` — all pre-existing tests pass
4. Write tests for new code with **≥80% coverage** on new modules (verify with `pytest --cov=src/doc2md --cov-report=term-missing`)
5. Deliver a one-paragraph **Phase Summary** describing what was built and any deviations from the plan

These gates are non-negotiable. A phase is not complete until all five are satisfied.

---

## Fixture Generation Reference

Before P1 starts, fixtures must exist in `tests/fixtures/`. They are produced by `scripts/generate_fixtures.py`, generated programmatically so the repo stays small and reproducible. The script generates:

| Fixture | Generation strategy |
|---|---|
| `sample_digital.pdf` | reportlab — single-column, 3 pages, public-domain text (e.g. excerpt from a Project Gutenberg work), one table on page 2, one embedded image on page 3 |
| `sample_multicolumn.pdf` | reportlab — 2 pages with 2-column layout via `BaseDocTemplate` + `Frame`, public-domain text |
| `sample_scanned.pdf` | reportlab → render each page to PNG via Pillow (or pdf2image) → reassemble image-only PDF via PyMuPDF (no text layer) |
| `sample_locked.pdf` | pikepdf — encrypt `sample_digital.pdf` with password `"test123"` (user pw) and a separate owner password |
| `sample_mixed.pdf` | pikepdf — concatenate first 2 pages from `sample_digital.pdf` + 1 image-only page from `sample_scanned.pdf` |
| `sample.docx` | python-docx — title, two headings, one table, one inline image, two section breaks |
| `sample.odt` | pypandoc — convert `sample.docx` → odt |
| `sample.epub` | ebooklib — 3 chapters, metadata (title, author, lang=en), one image in chapter 2 |
| `sample.html` | hand-written string with headings, paragraph, table, image tag |
| `sample.txt` | hand-written string with ALL CAPS section markers and `===`/`---` underlines |
| `sample_image.png` | Pillow — 600×400 white background with rendered text "Hello world from doc2md" via PIL.ImageDraw |

`scripts/generate_fixtures.py` must be **idempotent** — re-running it overwrites fixtures cleanly. It is invoked once at end of P0, and re-invoked any time a phase needs a new fixture variant.

The script is part of P0's deliverables (the human runs it manually after creating the venv).

---

## PHASE 0 — Environment Setup (Human Checklist)

**Agent role:** None — this is a human-executed checklist. No code agent.
**Complexity:** S
**Dependencies:** none
**Input context this agent receives:** N/A (human follows this block directly)

**Pre-conditions (verify before starting):**
- [ ] WSL Ubuntu shell available
- [ ] sudo apt access on the WSL machine
- [ ] Empty or new project directory at `~/projects/doc2md`

**Step-by-step instructions:**

1. **Install system binaries** (paste the whole block):
   ```bash
   sudo apt-get update && sudo apt-get install -y \
     python3.11 python3.11-venv python3-pip \
     tesseract-ocr tesseract-ocr-eng tesseract-ocr-fra \
     qpdf pandoc libmagic1 poppler-utils
   ```

2. **Verify Python**: `python3.11 --version` → expect `Python 3.11.x` (3.10+ acceptable; 3.11 recommended).

3. **Verify each system binary** is on PATH:
   ```bash
   tesseract --version
   qpdf --version
   pandoc --version
   pdftoppm -v
   ```
   All four must print versions without error.

4. **Pin the Python version** for the project:
   ```bash
   cd ~/projects/doc2md
   echo "3.11" > .python-version
   ```

5. **Create the virtual environment** (using stdlib `venv`; `uv` is fine but optional):
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   ```

6. **Install dev tools globally in the venv** (used by every phase):
   ```bash
   pip install ruff mypy pytest pytest-cov pytest-mock pre-commit
   ```

7. **Initialize git** if not already a repo:
   ```bash
   git init
   git add .python-version
   git commit -m "P0: pin Python version"
   ```

8. **Install pre-commit hooks** (will be configured in P1; for now just install the binary — done in step 6).

9. **Create empty directory skeleton** so subsequent phases never have to mkdir:
   ```bash
   mkdir -p src/doc2md/{core,converters,rendering,images,ocr,utils} \
            tests/{unit,converters,integration,fixtures} \
            scripts docs/examples
   ```

10. **Add fixture generation script and run it.** P1 needs fixtures present. The exact contents of `scripts/generate_fixtures.py` are produced as part of the P0 human work — see "Fixture Generation Reference" above. Approach:
    - Install fixture-generation deps inside venv: `pip install reportlab pikepdf pillow python-docx ebooklib pypandoc pymupdf`
    - Write `scripts/generate_fixtures.py` per the reference table
    - Run: `python scripts/generate_fixtures.py`
    - Verify: `ls tests/fixtures/` shows all 11 expected fixtures

11. **Commit the baseline**:
    ```bash
    git add .
    git commit -m "P0: environment + fixtures baseline"
    ```

**Files to create/modify:**
- `.python-version` — pin to 3.11
- `scripts/generate_fixtures.py` — produces all 11 test fixtures
- `tests/fixtures/*` — 11 fixture files
- Empty directory skeleton

**Tests to write:** None for this phase.

**Quality gate checklist (mandatory before delivery):**
- [ ] `python --version` ≥ 3.10 inside activated venv
- [ ] All four system binaries verified on PATH
- [ ] All 11 fixtures exist in `tests/fixtures/`
- [ ] `git log --oneline` shows two commits (`P0: pin Python version`, `P0: environment + fixtures baseline`)
- [ ] Phase Summary written

**Output contract:**
Inside an activated `.venv`:
- `python --version` returns 3.10+
- `which tesseract qpdf pandoc pdftoppm` all return paths
- `ls tests/fixtures/` lists all 11 fixture files
- `python -m doc2md --help` does **not** yet work — that arrives in P1

**Handoff to next phase:**
The Phase Summary for P1 must state:
- Python version active in venv
- Confirmation all 11 fixtures exist (list them)
- Confirmation all system binaries are reachable
- Path to `scripts/generate_fixtures.py` and how to re-run it

---

## PHASE 1 — Core Skeleton + PDF Digital MVP + Validator

**Agent role:** Python scaffolder
**Complexity:** M
**Dependencies:** P0
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure (full tree)
- §4 Output Schema (full)
- §5 Quality Gates (full)
- Phase Summary from: P0

**Pre-conditions (verify before starting):**
- [ ] Active venv with Python 3.10+
- [ ] `tests/fixtures/sample_digital.pdf` exists
- [ ] System binaries present (already verified in P0)
- [ ] `pyproject.toml` does not yet exist (this phase creates it)

**Step-by-step instructions:**

1. **Create `pyproject.toml`** with build-backend `hatchling`, project name `doc2md`, version `0.1.0`, Python `>=3.10`, console script `doc2md = "doc2md.cli:main"`. Core deps for P1 only: `typer`, `pymupdf`, `pyyaml`, `python-magic`, `pydantic>=2`. Dev deps in `[project.optional-dependencies].dev`: `pytest`, `pytest-cov`, `pytest-mock`, `ruff`, `mypy`. Configure ruff (line-length 100, `select=["E","F","I","UP","B"]`) and mypy (`strict_optional = true`, `disallow_untyped_defs = true`).
2. **Run** `pip install -e ".[dev]"` to install the package in editable mode.
3. **Create `src/doc2md/__init__.py`** with `__version__ = "0.1.0"`.
4. **Create `src/doc2md/__main__.py`** that imports and calls `cli.main()`.
5. **Create `src/doc2md/logging_setup.py`** with `setup_logging(verbose: bool) -> None` configuring root logger (INFO default, DEBUG when verbose, format `%(levelname)s %(name)s: %(message)s`).
6. **Create `src/doc2md/config.py`** with a Pydantic `Settings` model holding defaults (e.g., `images_strategy: str = "placeholder"`, `converter_version: str = "0.1.0"`).
7. **Create `src/doc2md/core/exceptions.py`** with: `Doc2MdError` (base), `UnsupportedFormat`, `LockedDocument`, `ConversionFailed`.
8. **Create `src/doc2md/core/document.py`** with Pydantic models:
   - `Frontmatter` — fields exactly per §4 with proper types, `schema_version: Literal["1.0"]`
   - `IndexEntry` (kind: Literal["page","section","table","figure"], label, anchor_id)
   - `Page` (number: int, anchor_id: str, content: str)
   - `MarkdownDocument` (frontmatter, pages: list[Page], index_entries: list[IndexEntry])
9. **Create `src/doc2md/core/detector.py`** with `detect_format(path: Path) -> str` using extension + `python-magic` MIME. Return one of: `pdf|docx|odt|epub|html|txt|image|unsupported`.
10. **Create `src/doc2md/core/base_converter.py`** with abstract `BaseConverter` defining `convert(self, input_path: Path) -> MarkdownDocument`.
11. **Create `src/doc2md/core/dispatcher.py`** with `get_converter(format: str) -> BaseConverter`. For P1, only `pdf` returns a real converter; others raise `UnsupportedFormat`.
12. **Create `src/doc2md/core/validator.py`** with:
    - `ValidationResult` dataclass: `valid: bool`, `warnings: list[str]`
    - `validate(doc: MarkdownDocument) -> ValidationResult`:
      - Check all required frontmatter fields populated (None only allowed where schema permits)
      - When `frontmatter.page_count` is not None: verify pages are numbered 1..N sequentially
      - For each `index_entry.anchor_id`: assert there exists a page or section with that ID in the document (page IDs are `page-N`)
    - Validator never raises on warnings — returns the result; pipeline logs them
13. **Create `src/doc2md/converters/pdf_digital.py`** — class `PdfDigitalConverter(BaseConverter)`:
    - Open with `fitz.open(path)`
    - Per page: extract text with `page.get_text("text")`
    - Build `Page(number, anchor_id=f"page-{n}", content=text)` per page
    - Build `Frontmatter` with format=pdf, document_type=digital, ocr_applied=False, language=None, images_strategy from settings, page_count=len(pages), title=path.stem (Docling/heading detection deferred to P3)
    - No image extraction yet (deferred to P2)
    - No index entries yet beyond pages (full index in P2)
14. **Create `src/doc2md/core/pipeline.py`** — `run(input_path: Path, output_path: Path, settings: Settings) -> None`:
    - Detect → get converter → convert → validate (log warnings) → render to plain MD string → write
    - For P1, render minimally inline: produce frontmatter as YAML (use `yaml.safe_dump`), then for each page emit `<a id="page-N"></a>\n**[Page N]**\n\n{content}\n\n` (full renderer arrives in P2)
15. **Create `src/doc2md/cli.py`** — Typer app with single command:
    ```
    doc2md INPUT --output/-o PATH [--verbose]
    ```
    Calls `setup_logging`, builds `Settings`, calls `pipeline.run`.
16. **Create `tests/conftest.py`** exposing fixture path constants:
    ```python
    FIXTURES = Path(__file__).parent / "fixtures"
    ```
17. **Write tests** as listed under "Tests to write" below.
18. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — package config + ruff + mypy
- `src/doc2md/__init__.py`, `__main__.py`, `cli.py`, `config.py`, `logging_setup.py`
- `src/doc2md/core/{base_converter,document,detector,dispatcher,pipeline,validator,exceptions}.py`
- `src/doc2md/converters/pdf_digital.py` — PyMuPDF-only
- `src/doc2md/converters/__init__.py`, `src/doc2md/core/__init__.py` — empty for now
- `tests/conftest.py`
- Test files listed below

**Tests to write:**
- `tests/unit/test_detector.py`:
  - `.pdf` extension on a valid PDF returns `"pdf"`
  - `.docx` returns `"docx"` (even if converter not implemented yet)
  - File with no extension but PDF MIME returns `"pdf"`
  - Unknown extension returns `"unsupported"`
- `tests/unit/test_dispatcher.py`:
  - `get_converter("pdf")` returns `PdfDigitalConverter` instance
  - `get_converter("docx")` raises `UnsupportedFormat`
- `tests/unit/test_validator.py`:
  - Valid doc → `ValidationResult(valid=True, warnings=[])`
  - Missing required field → `valid=False`, warning mentions field
  - Page-count mismatch (page_count=3, only 2 pages) → warning
  - Index entry referencing nonexistent anchor → warning
- `tests/unit/test_frontmatter.py` (basic for P1; expanded in P2):
  - Frontmatter Pydantic model accepts schema_version="1.0"
  - schema_version other than "1.0" raises validation error
- `tests/converters/test_pdf_digital.py`:
  - Convert `sample_digital.pdf`: returns `MarkdownDocument` with 3 pages, page numbers 1-2-3, anchor IDs page-1/2/3, document_type=digital, ocr_applied=False, format=pdf
- `tests/integration/test_cli_single_file.py`:
  - Invoke `doc2md tests/fixtures/sample_digital.pdf -o /tmp/out.md` via Typer's CliRunner; assert exit code 0, file exists, contains `schema_version: "1.0"`, contains `<a id="page-1"></a>`, valid YAML frontmatter (parse with yaml.safe_load)

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors on this phase's files
- [ ] `pytest tests/` — all pre-existing tests pass (this phase is the first; all new tests pass)
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary paragraph written

**Output contract:**
Running `doc2md tests/fixtures/sample_digital.pdf -o /tmp/out.md` from an activated venv exits 0 and produces `/tmp/out.md` with:
- Valid YAML frontmatter parseable by `yaml.safe_load`, including `schema_version: "1.0"`, `format: "pdf"`, `page_count: 3`, `document_type: "digital"`, `ocr_applied: false`
- Three page anchors `<a id="page-1"></a>`, `<a id="page-2"></a>`, `<a id="page-3"></a>` each followed by `**[Page N]**`
- Per-page extracted text from the PDF

**Handoff to next phase:**
The Phase Summary for P2 must state:
- Confirm `MarkdownDocument`, `Frontmatter`, `Page`, `IndexEntry` model field names (P2 will populate `index_entries` and figure/table data)
- Confirm validator signature `validate(doc) -> ValidationResult` and that pipeline already calls it
- Confirm pipeline currently renders inline (P2 will replace with `markdown_renderer`)
- Confirm PdfDigitalConverter currently does NOT extract images (P2 adds extraction)

---

## PHASE 2 — Rendering Layer + Image Strategies (placeholder, omit)

**Agent role:** Rendering specialist
**Complexity:** M
**Dependencies:** P1
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P1

**Pre-conditions (verify before starting):**
- [ ] P1 delivered: `MarkdownDocument`, validator, pipeline, PDF digital converter all working
- [ ] `pyproject.toml` exists; venv installed editable
- [ ] `tests/fixtures/sample_digital.pdf` exists with a table on page 2 and an image on page 3

**Step-by-step instructions:**

1. **`rendering/frontmatter.py`** — `render_frontmatter(fm: Frontmatter) -> str` using `yaml.safe_dump(..., sort_keys=False, allow_unicode=True)` wrapped in `---\n...\n---\n`.
2. **`rendering/page_anchors.py`** — `render_anchor(page_num: int) -> str` returns `<a id="page-N"></a>\n**[Page N]**\n`. Helper `anchor_id(page_num) -> str` → `f"page-{page_num}"`.
3. **`rendering/table_renderer.py`** — `render_table(headers: list[str], rows: list[list[str]]) -> str`:
   - If any cell contains a newline, an unescaped pipe that can't be safely escaped, or merged-cell markers → return fenced code block with raw content + `> Note: complex table preserved as raw text` line above
   - Else render GFM table with proper alignment row
4. **`rendering/index_builder.py`** — `build_index(doc: MarkdownDocument) -> str` produces the four sub-sections (Pages, Sections, Tables, Figures) per §4 template, only emitting non-empty sections.
5. **`rendering/sanitizer.py`** — `sanitize(text: str) -> tuple[str, dict[str, int]]`:
   - Tokenize protecting backtick code spans (single `` ` `` and triple ``` ``` ```)
   - Outside code spans: replace `—`→`--`, `–`→`-`, smart quotes → ASCII
   - LaTeX-like math `$...$`, `\(...\)`, `\[...\]` already inside code spans are preserved unchanged
   - Returns sanitized text and replacement counts dict (logged at INFO by caller)
6. **`rendering/images_strategy.py`** — `apply_strategy(strategy: str, image_meta: ImageMeta) -> str`:
   - `placeholder` → `![Figure {n} — {description}]({images/path})`
   - `omit` → `[IMAGE OMITTED: Figure {n}]`
   - `vlm` → `raise NotImplementedError("VLM strategy lands in P10")`
   - `ImageMeta` is a small dataclass: `figure_number, description, output_path, page_number`
7. **`images/naming.py`** — `image_filename(figure_number: int, page_number: int, ext: str) -> str` → `f"fig{figure_number}_page{page_number}.{ext}"`.
8. **`images/extractor.py`** — `extract_images_from_pdf(pdf_path: Path, output_dir: Path) -> list[ExtractedImage]`:
   - Use PyMuPDF `page.get_images(full=True)` and `doc.extract_image(xref)`
   - Save to `output_dir / "images" / fig{n}_page{p}.{ext}` (numbering monotonic across the document)
   - Return list of `ExtractedImage(figure_number, page_number, path, ext, width, height)`
9. **`rendering/markdown_renderer.py`** — `render(doc: MarkdownDocument, output_path: Path, extracted_images: list[ExtractedImage], settings: Settings) -> str`:
   - Compose frontmatter + each page (anchor + content with images interpolated via `images_strategy.apply_strategy`) + horizontal rule + index
   - Apply `sanitize` last to body (NOT to frontmatter to avoid breaking YAML)
   - Log replacement counts at INFO
10. **Update `core/pipeline.py`** to:
    - After `convert()`, call `extract_images_from_pdf` (only for PDF format) into `output_path.parent / "images"`
    - Call `markdown_renderer.render` instead of inline rendering
    - Then validate (validator now also checks image references in body resolve to extracted files)
    - Write final string
11. **Update `converters/pdf_digital.py`** to populate `index_entries` for each page and to detect simple tables via PyMuPDF `page.find_tables()` (best-effort; complex tables fall back to code block via renderer). Add detected tables/figures to `MarkdownDocument.index_entries`.
12. **Update validator** — additionally warn if a body image reference points to a file that doesn't exist on disk relative to output.
13. **Tests** per below.
14. **Run quality gates** per §5.

**Files to create/modify:**
- `src/doc2md/rendering/__init__.py`
- `src/doc2md/rendering/{frontmatter,page_anchors,table_renderer,index_builder,sanitizer,images_strategy,markdown_renderer}.py`
- `src/doc2md/images/__init__.py`, `extractor.py`, `naming.py`
- Modify `src/doc2md/core/pipeline.py` — wire renderer + extractor
- Modify `src/doc2md/converters/pdf_digital.py` — populate index entries, detect tables
- Modify `src/doc2md/core/validator.py` — image-on-disk check

**Tests to write:**
- `tests/unit/test_frontmatter.py` (extend): YAML escaping for special chars in titles, null page_count serializes as `null`, all field combinations including ISO 8601 dates
- `tests/unit/test_page_anchors.py`: format correctness, page 0, page 10000
- `tests/unit/test_table_renderer.py`: simple GFM table, table with pipes in cells, table with newlines in cells (→ fallback code block), empty table, single-column table
- `tests/unit/test_index_builder.py`: empty doc (no index sections emitted), pages-only, full doc with all four entry types, anchor links well-formed
- `tests/unit/test_sanitizer.py`: dash normalization outside code, dashes preserved inside backticks, LaTeX `$...$` preserved inside backticks, smart quote replacement, mixed content, replacement counts correct
- `tests/unit/test_images_strategy.py`: placeholder format, omit format, vlm raises NotImplementedError
- `tests/integration/test_full_pipeline.py`: convert `sample_digital.pdf` → assert images extracted to `images/` next to output, MD contains GFM table from page 2, MD contains placeholder image reference, end-of-doc index lists pages + table + figure, frontmatter valid YAML with schema_version=1.0

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
`doc2md tests/fixtures/sample_digital.pdf -o /tmp/out.md` produces:
- `/tmp/out.md` schema-compliant per §4 (frontmatter, page anchors, GFM table on page 2, image reference on page 3, end-of-doc index with Pages + Tables + Figures)
- `/tmp/images/` directory with at least one extracted image named `figN_pageM.ext`
- Sanitization applied (no smart quotes, em-dashes normalized) outside code spans
- Validator warnings logged at WARN level (not blocking)

**Handoff to next phase:**
The Phase Summary for P3 must state:
- Confirm `markdown_renderer.render` signature and that pipeline calls it
- Confirm PdfDigitalConverter currently uses **PyMuPDF only** (table detection is `page.find_tables()`, no layout analysis); P3 must replace text + heading + table extraction with Docling while keeping image extraction via PyMuPDF
- Confirm `images/extractor.py` is shared and should NOT be replaced by P3
- List the `MarkdownDocument` fields P3 must populate (especially nested heading hierarchy in `Page.content` and `IndexEntry` of kind=section)

---

## PHASE 3 — Docling Integration for Digital PDFs

**Agent role:** PDF/layout integration
**Complexity:** L
**Dependencies:** P2
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P2

**Pre-conditions (verify before starting):**
- [ ] P2 delivered: rendering pipeline working, image extraction working, sample PDF produces schema-compliant MD
- [ ] `tests/fixtures/sample_multicolumn.pdf` exists (generated in P0)
- [ ] PyMuPDF still installed (still needed for image extraction + encryption check)

**Step-by-step instructions:**

1. **Add `docling` to `pyproject.toml`** dependencies. `pip install -e ".[dev]"` to refresh.
2. **Refactor `converters/pdf_digital.py`**:
   - Use `docling.document_converter.DocumentConverter` to convert PDF
   - Extract reading-order text per page from Docling's structured output
   - Map Docling heading levels → Markdown `#`, `##`, `###` (preserve hierarchy)
   - Use Docling's table extraction; pass each table to `rendering/table_renderer.render_table`
   - Keep PyMuPDF for: encryption check (`fitz.open(path).is_encrypted` → if True, raise `LockedDocument` for now; P5 handles it), page count, image extraction (still via existing `images/extractor.py`)
3. **Heading-to-section index entries**: when Docling reports a heading on page N, add `IndexEntry(kind="section", label=heading_text, anchor_id=f"page-{N}")`.
4. **Multi-column reading order**: rely on Docling's layout; verify that `sample_multicolumn.pdf` produces text in correct logical order in test.
5. **Fallback path**: wrap Docling call in try/except. On exception, log `WARNING: Docling failed (<reason>), falling back to PyMuPDF raw extraction`, then use the previous P1/P2 PyMuPDF flow (preserve P2 behavior). Add a flag on the converter for whether the fallback was used (for testing).
6. **Performance note**: log the Docling conversion time at DEBUG.
7. **Tests** per below.
8. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — add `docling` dependency
- `src/doc2md/converters/pdf_digital.py` — Docling primary path + PyMuPDF fallback
- `tests/converters/test_pdf_digital.py` — new tests for Docling and fallback

**Tests to write:**
- `tests/converters/test_pdf_digital.py` (extend):
  - Convert `sample_multicolumn.pdf` → assert text appears in left-column-first order (test by checking that a known left-column phrase appears in the output before a known right-column phrase)
  - Heading hierarchy: convert `sample_digital.pdf` and assert at least one `# ` and one `## ` line in output corresponding to known headings in the fixture
  - Index entries of kind="section" present in `MarkdownDocument`
  - Force fallback (monkeypatch Docling to raise) → assert log contains "falling back to PyMuPDF" and conversion still succeeds with valid output
  - Fixture without images still produces valid MD (no regression from P2)

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass (P1, P2 tests still green)
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on modified modules
- [ ] Phase Summary written

**Output contract:**
`doc2md tests/fixtures/sample_multicolumn.pdf -o /tmp/out.md` produces MD where:
- Reading order respects column structure
- Heading levels reflect document layout (at least one heading detected)
- All P2 schema fields still present
- If Docling raises, fallback logs the warning and produces valid (less-structured) output

**Handoff to next phase:**
The Phase Summary for P4 must state:
- Confirm `PdfDigitalConverter` now uses Docling primary, PyMuPDF fallback
- Confirm where in the dispatcher digital vs scanned routing happens (currently dispatcher just routes "pdf" → digital; P4 must split routing)
- Confirm Docling is already installed and working
- Note any Docling version pin chosen

---

## PHASE 4 — Scanned PDFs (OCR via Docling)

**Agent role:** OCR specialist
**Complexity:** L
**Dependencies:** P3
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P3

**Pre-conditions (verify before starting):**
- [ ] P3 delivered: digital PDFs work via Docling
- [ ] `tests/fixtures/sample_scanned.pdf` exists (image-only, no text layer)
- [ ] `tests/fixtures/sample_mixed.pdf` exists (digital + scanned pages)
- [ ] `tesseract` binary on PATH

**Step-by-step instructions:**

1. **Add deps to `pyproject.toml`**: `pytesseract`, `langdetect`, `pillow`. `pip install -e ".[dev]"`.
2. **Create `ocr/__init__.py`** and **`ocr/tesseract_runner.py`**:
   - `ocr_image(image: PIL.Image.Image, lang: str) -> tuple[str, float]` — returns (text, mean_confidence). Use `pytesseract.image_to_data` to compute mean confidence per page.
3. **Create `utils/text_heuristics.py`** with `detect_language(sample: str) -> str | None` using `langdetect`. Returns ISO language code or None on failure.
4. **Add per-page digital/scanned heuristic** in `core/dispatcher.py` (or a new helper `core/pdf_routing.py`):
   - `classify_pdf(path: Path) -> Literal["digital","scanned","mixed"]`
   - Open with PyMuPDF; for each page count extractable chars
   - If <20% of pages have meaningful text → "scanned"
   - If 100% have meaningful text → "digital"
   - Else → "mixed"
   - Update dispatcher: format=="pdf" branches on this classification to pick PdfDigitalConverter, PdfScannedConverter, or a new MixedConverter that routes per page.
5. **Create `converters/pdf_scanned.py`** — `PdfScannedConverter`:
   - Use Docling's OCR-enabled pipeline (`PipelineOptions(do_ocr=True)`) by default
   - When `--ocr-engine=direct`: bypass Docling, render each page to image via PyMuPDF (`page.get_pixmap(dpi=300)`), call `tesseract_runner.ocr_image`
   - For language: if `--ocr-lang` provided, use it; else run a one-page sample OCR with Tesseract (`eng` default), then `langdetect.detect` on the result, then re-run OCR with detected lang if non-en
   - Frontmatter: `document_type="scanned"`, `ocr_applied=True`, `language=<detected>`
   - Per-page confidence <70% → emit warning log with page number
6. **Mixed handler**: implement inside dispatcher or as `converters/pdf_mixed.py` (your choice — document in Phase Summary). Per-page classify; route digital pages through PdfDigitalConverter logic, scanned pages through PdfScannedConverter logic; merge into one `MarkdownDocument`. `document_type="mixed"`, `ocr_applied=True`.
7. **Add CLI flags** to `cli.py`:
   - `--ocr-lang TEXT` (default: None → auto-detect)
   - `--ocr-engine [docling|direct]` (default: `docling`; layout-preserving via Docling vs raw pytesseract for speed; agent must document this trade-off in `--help` text)
   Wire flags into Settings; pass to converters.
8. **Tests** per below. Mock OCR calls where the fixture's actual OCR output is brittle; use real OCR for the simple synthetic fixture.
9. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — add `pytesseract`, `langdetect`, `pillow`
- `src/doc2md/ocr/__init__.py`, `tesseract_runner.py`
- `src/doc2md/utils/text_heuristics.py`
- `src/doc2md/converters/pdf_scanned.py`
- `src/doc2md/converters/pdf_mixed.py` (if chosen) OR mixed logic in dispatcher
- `src/doc2md/core/dispatcher.py` — classify and route
- `src/doc2md/cli.py` — add `--ocr-lang`, `--ocr-engine` flags
- `src/doc2md/config.py` — add corresponding settings fields

**Tests to write:**
- `tests/converters/test_pdf_scanned.py`:
  - Convert `sample_scanned.pdf` → `document_type="scanned"`, `ocr_applied=True`, language detected, at least some OCR text present
  - With `--ocr-engine=direct` flag → still produces valid output
- `tests/unit/test_dispatcher.py` (extend):
  - `classify_pdf` returns "digital" for `sample_digital.pdf`
  - Returns "scanned" for `sample_scanned.pdf`
  - Returns "mixed" for `sample_mixed.pdf`
- `tests/converters/test_pdf_digital.py` (extend if needed): regression test still passes after dispatcher changes
- `tests/integration/test_full_pipeline.py` (extend): mixed PDF produces `document_type="mixed"` with both OCR'd and non-OCR'd content

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
- `doc2md tests/fixtures/sample_scanned.pdf -o /tmp/out.md` exits 0 with `document_type: "scanned"` and `ocr_applied: true` in frontmatter and OCR'd text in body
- `doc2md tests/fixtures/sample_mixed.pdf -o /tmp/out.md` exits 0 with `document_type: "mixed"`, mixing digital-extracted and OCR'd pages
- `--ocr-engine=direct` and `--ocr-lang=eng` flags both functional

**Handoff to next phase:**
The Phase Summary for P5 must state:
- Confirm dispatcher classification path (`classify_pdf`) and where it's called
- Confirm encryption check still raises `LockedDocument` (P3 set this up); P5 must intercept before classification
- Confirm Settings fields for `ocr_lang` and `ocr_engine`
- List converters that exist: `PdfDigitalConverter`, `PdfScannedConverter`, mixed handling location

---

## PHASE 5 — Locked PDFs

**Agent role:** PDF security
**Complexity:** S
**Dependencies:** P4
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P4

**Pre-conditions (verify before starting):**
- [ ] P4 delivered: digital, scanned, mixed PDFs all work
- [ ] `tests/fixtures/sample_locked.pdf` exists (encrypted with password "test123")
- [ ] `qpdf` binary on PATH

**Step-by-step instructions:**

1. **Create `utils/pdf_unlock.py`** with:
   - `is_encrypted(path: Path) -> bool` (PyMuPDF `is_encrypted`)
   - `try_decrypt(path: Path, password: str | None) -> Path` — returns path to decrypted PDF (input path if not encrypted, else a temp file)
     - First attempt: if password provided, PyMuPDF `doc.authenticate(password)`
     - Second attempt: empty owner password via qpdf subprocess: `qpdf --decrypt --password='' input output`
     - On all failures: raise `LockedDocument(f"Cannot decrypt {path}: provide --password or document is DRM-protected")`
2. **Create `converters/pdf_locked.py`** — `PdfLockedConverter`:
   - Calls `try_decrypt` to obtain a decrypted path
   - Re-routes through `dispatcher.classify_pdf` on the decrypted file → delegates to digital/scanned/mixed converter
   - Stores temp file lifecycle so it's cleaned up after rendering completes (use `tempfile.TemporaryDirectory` context manager around the entire pipeline call from this converter)
3. **Update `core/dispatcher.py`** — when format is `pdf`, FIRST check `pdf_unlock.is_encrypted`. If encrypted → `PdfLockedConverter`. Else → existing classify_pdf path.
4. **Add CLI flag** to `cli.py`: `--password TEXT` (default: None). Wire into Settings, pass to PdfLockedConverter.
5. **Tests** per below. Use the actual `sample_locked.pdf` for real decryption tests.
6. **Run quality gates** per §5.

**Files to create/modify:**
- `src/doc2md/utils/pdf_unlock.py`
- `src/doc2md/converters/pdf_locked.py`
- `src/doc2md/core/dispatcher.py` — encryption-first routing
- `src/doc2md/cli.py` — `--password` flag
- `src/doc2md/config.py` — `password: str | None` setting

**Tests to write:**
- `tests/converters/test_pdf_locked.py`:
  - Convert `sample_locked.pdf` with `password="test123"` → succeeds, produces valid MD
  - Convert `sample_locked.pdf` without password → if owner-only-locked, succeeds via qpdf; if user-locked, raises `LockedDocument`
  - Convert with wrong password → raises `LockedDocument` with helpful message
- `tests/unit/test_pdf_unlock.py`:
  - `is_encrypted` true on locked, false on plain
  - `try_decrypt` returns same path on plain PDF
  - `try_decrypt` returns temp path on locked PDF with correct password

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
- `doc2md tests/fixtures/sample_locked.pdf --password test123 -o /tmp/out.md` produces a valid MD (delegating to digital converter post-unlock)
- Wrong password → exit code 1 with clear `LockedDocument` error
- Temp decrypted files cleaned up after run

**Handoff to next phase:**
The Phase Summary for P6 must state:
- Confirm all PDF subtypes (digital, scanned, mixed, locked) now route correctly
- Confirm Settings fields: `images_strategy`, `ocr_lang`, `ocr_engine`, `password`
- Confirm rendering pipeline (markdown_renderer + image_strategy + sanitizer + validator) is shared and stable — converters only need to populate `MarkdownDocument`

---

## PHASE 6 — DOCX + ODT

**Agent role:** Office formats
**Complexity:** M
**Dependencies:** P5
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P5

**Pre-conditions (verify before starting):**
- [ ] P5 delivered: all PDF paths working
- [ ] `tests/fixtures/sample.docx`, `sample.odt` exist
- [ ] `pandoc` binary on PATH

**Step-by-step instructions:**

1. **Add deps**: `python-docx`, `pypandoc` to `pyproject.toml`. Reinstall.
2. **Create `converters/docx.py`** — `DocxConverter`:
   - Try Docling `DocumentConverter` for DOCX first (preferred path — best heading/table fidelity)
   - Fallback to python-docx with manual style→heading mapping (`Heading 1` → `#`, `Heading 2` → `##`, etc.); table cells → `table_renderer.render_table`
   - Final fallback: `pypandoc.convert_file(path, 'gfm-raw_html')` and parse the result back into `MarkdownDocument` pages (single page if no section breaks)
   - Page synthesis (Q3): inspect python-docx `document.sections`; if multiple sections present → one anchor per section, `page_count = len(sections)`; else `page_count = None` and emit only heading-level section index entries (no page anchors)
   - Extract embedded images via python-docx by reading the `.docx` zip's `word/media/` folder (`zipfile.ZipFile`); save to `images/` via `images/naming.py`
   - Apply `images_strategy` from Settings
3. **Create `converters/odt.py`** — `OdtConverter`:
   - Use `pypandoc.convert_file(path, 'gfm-raw_html')` to get markdown
   - Wrap in single-page `MarkdownDocument` with `page_count=None`, `document_type="odt"`
   - If pandoc not on PATH → raise `ConversionFailed("pandoc binary not found; install with apt install pandoc")`
   - Image extraction: pandoc with `--extract-media` flag to a temp dir, then move/rename images to the standard `images/` location
4. **Update `core/dispatcher.py`** to route `docx` → `DocxConverter`, `odt` → `OdtConverter`.
5. **Tests** per below.
6. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — add `python-docx`, `pypandoc`
- `src/doc2md/converters/docx.py`, `odt.py`
- `src/doc2md/core/dispatcher.py` — route docx, odt
- Tests below

**Tests to write:**
- `tests/converters/test_docx.py`:
  - Convert `sample.docx` → valid MD, headings preserved, table preserved (GFM), image extracted, page anchors per section break (or null page_count if no sections)
  - With `--images=omit` → no extracted image files produced; placeholders replaced
  - Force Docling failure → fallback to python-docx works
- `tests/converters/test_odt.py`:
  - Convert `sample.odt` → valid MD, `document_type="odt"`, `page_count=None`
  - Pandoc-missing simulation → clear `ConversionFailed` error (mock subprocess)

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
- `doc2md tests/fixtures/sample.docx -o /tmp/out.md` produces schema-compliant MD
- `doc2md tests/fixtures/sample.odt -o /tmp/out.md` produces schema-compliant MD
- DOCX with section breaks produces one anchor per section; without sections produces null page_count and only section-level index entries

**Handoff to next phase:**
The Phase Summary for P7 must state:
- Confirm `DocxConverter` and `OdtConverter` both wired into dispatcher
- Confirm image extraction works for DOCX zip media; pandoc `--extract-media` works for ODT
- Confirm the page-anchor synthesis convention used (page_count null when no section breaks)

---

## PHASE 7 — EPUB

**Agent role:** EPUB
**Complexity:** S
**Dependencies:** P6
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P6

**Pre-conditions (verify before starting):**
- [ ] P6 delivered: DOCX, ODT working
- [ ] `tests/fixtures/sample.epub` exists with 3 chapters and one image

**Step-by-step instructions:**

1. **Add deps**: `ebooklib`, `markitdown` to `pyproject.toml`. Reinstall.
2. **Create `converters/epub.py`** — `EpubConverter`:
   - Open with `ebooklib.epub.read_epub`
   - For each `ITEM_DOCUMENT` (chapter) in spine order:
     - Convert chapter HTML → MD via `markitdown.MarkItDown().convert_stream`
     - Build `Page(number=chapter_index, anchor_id=f"page-{chapter_index}", content=md)`
   - Pull metadata via `book.get_metadata('DC', '...')`: title (`title`), language (`language`), authors → join into `title` if no proper title
   - Extract images: iterate `book.get_items_of_type(ITEM_IMAGE)`, save to `images/` via `images/naming.py` (figure_number monotonic, page_number = chapter that referenced them — or `0` if global)
   - Apply images_strategy
   - `document_type="epub"`, `page_count=len(chapters)`
3. **Update `core/dispatcher.py`** to route `epub` → `EpubConverter`.
4. **Tests** per below.
5. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — add `ebooklib`, `markitdown`
- `src/doc2md/converters/epub.py`
- `src/doc2md/core/dispatcher.py` — route epub
- Test file below

**Tests to write:**
- `tests/converters/test_epub.py`:
  - Convert `sample.epub` → valid MD with 3 page anchors (one per chapter)
  - Frontmatter contains title and language from EPUB metadata
  - Image extracted to `images/`
  - `document_type="epub"`, `page_count=3`

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
`doc2md tests/fixtures/sample.epub -o /tmp/out.md` produces schema-compliant MD with chapter-level page anchors and metadata-derived frontmatter.

**Handoff to next phase:**
The Phase Summary for P8 must state:
- Confirm `EpubConverter` wired in
- Confirm `markitdown` package is available (P8 will reuse it for HTML)

---

## PHASE 8 — HTML + TXT + Standalone Image

**Agent role:** Lightweight formats
**Complexity:** S
**Dependencies:** P7
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P7

**Pre-conditions (verify before starting):**
- [ ] P7 delivered: EPUB working
- [ ] Fixtures `sample.html`, `sample.txt`, `sample_image.png` exist

**Step-by-step instructions:**

1. **Add deps**: `beautifulsoup4`, `markdownify`, `chardet` to `pyproject.toml`. Reinstall. (`markitdown` already present from P7.)
2. **Create `converters/html.py`** — `HtmlConverter`:
   - Primary: `markitdown.MarkItDown().convert_local(path)`
   - On exception: BeautifulSoup parse + markdownify fallback (log WARNING)
   - Single-page document, `document_type="html"`, `page_count=None`, anchor `page-1` synthesized
3. **Create `converters/txt.py`** — `TxtConverter`:
   - Read raw bytes; detect encoding with `chardet.detect`; if confidence <0.7, log WARNING and decode as UTF-8 with `errors='replace'`
   - Heuristic section inference (apply in order):
     - Lines that are ALL CAPS and >=3 chars → `## {line}` (heading-2)
     - Lines underlined with `===` → `# {line}`
     - Lines underlined with `---` → `## {line}`
     - Lines starting with `1.` `1.1` numbered patterns at column 0 → preserve as-is (not converted)
   - Single-page synthesized doc, `document_type="txt"`, `page_count=None`, anchor `page-1`
   - Detect language via `langdetect` on the body
4. **Create `converters/image.py`** — `ImageConverter`:
   - Open with PIL.Image; OCR via `ocr/tesseract_runner.ocr_image`
   - Single-page synthesized doc, `document_type="scanned-image"`, `ocr_applied=True`, `page_count=1`, anchor `page-1`
   - The image itself is also copied/referenced into `images/` next to output (figure 1)
5. **Update `core/dispatcher.py`** to route `html`, `txt`, `image` to their converters.
6. **Tests** per below.
7. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — add `beautifulsoup4`, `markdownify`, `chardet`
- `src/doc2md/converters/html.py`, `txt.py`, `image.py`
- `src/doc2md/core/dispatcher.py` — route html, txt, image
- Tests below

**Tests to write:**
- `tests/converters/test_html.py`: convert `sample.html` → MD with headings/table/image converted; force MarkItDown failure (monkeypatch) → BS4 fallback path; both produce schema-compliant MD
- `tests/converters/test_txt.py`: convert `sample.txt` → headings inferred, language detected; low-confidence encoding scenario warns and uses UTF-8 replacement
- `tests/converters/test_image.py`: convert `sample_image.png` → MD contains OCR'd "Hello world" text, `document_type="scanned-image"`, image present in `images/`

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
- `doc2md tests/fixtures/sample.html -o /tmp/out.md` → schema-compliant MD
- `doc2md tests/fixtures/sample.txt -o /tmp/out.md` → schema-compliant MD with inferred sections
- `doc2md tests/fixtures/sample_image.png -o /tmp/out.md` → schema-compliant MD with OCR'd text

**Handoff to next phase:**
The Phase Summary for P9 must state:
- Confirm all converters (PDF×4, DOCX, ODT, EPUB, HTML, TXT, image) work end-to-end
- Confirm CLI currently accepts only single-file input — P9 will add directory + recursive

---

## PHASE 9 — Batch Mode + Recursive Directory

**Agent role:** Batch/CLI UX
**Complexity:** S
**Dependencies:** P8
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P8

**Pre-conditions (verify before starting):**
- [ ] P8 delivered: all 9 converters working
- [ ] All fixtures exist for integration tests

**Step-by-step instructions:**

1. **Add dep**: `tqdm` to `pyproject.toml`. Reinstall.
2. **Create `utils/fs.py`** with:
   - `iter_input_files(path: Path, recursive: bool) -> Iterator[Path]` — yields supported files; skips hidden files and any directory named `images`
   - `mirror_output_path(input_root: Path, input_file: Path, output_root: Path, flatten: bool) -> Path` — returns the .md output path under output_root, mirroring the input tree relative to input_root, or flattened (use `<stem>__<parent>.md` to disambiguate name clashes when flat)
3. **Create `utils/progress.py`** with `ProgressBar` wrapper (thin shim over tqdm; allow disabling via env var or CLI flag).
4. **Update `cli.py`**:
   - Accept either a file or directory as `INPUT`
   - Add flags: `--recursive/-r` (default off), `--flatten` (default off)
   - When INPUT is a directory:
     - Iterate via `iter_input_files`
     - Per file: try/except, log errors with file path, continue
     - Wrap loop in tqdm progress
     - At end, print summary: `{success} succeeded, {fail} failed, {elapsed:.1f}s elapsed`; if any failed, print bullet list of failed files
   - When INPUT is a file: existing single-file behavior
5. **Tests** per below.
6. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — add `tqdm`
- `src/doc2md/utils/fs.py`, `progress.py`
- `src/doc2md/cli.py` — directory + flags
- Tests below

**Tests to write:**
- `tests/integration/test_cli_batch.py`:
  - Run on `tests/fixtures/` directory non-recursive → produces .md per supported file at top level only
  - Run with `--recursive` → produces .md for nested files (create a temp tree with subdirs)
  - Run with `--flatten` → all outputs in one flat dir, no name collisions
  - Force one file to fail (point to a corrupted PDF created at runtime) → other files still convert; summary lists the failure; exit code 0 (batch isolation) — document this choice in code
- `tests/unit/test_fs.py`:
  - `iter_input_files` skips hidden files, skips `images/`
  - `mirror_output_path` produces correct relative path under output root
  - `mirror_output_path` flatten mode disambiguates same-name files in different folders

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
- `doc2md tests/fixtures/ -o /tmp/out_dir/ --recursive` walks the directory, produces a per-file .md, prints tqdm progress and an end-of-batch summary; one failed file does not abort the batch.

**Handoff to next phase:**
The Phase Summary for P10 must state:
- Confirm batch mode works; one-file failure isolated
- Confirm `images_strategy` is fully Settings-driven; vlm strategy still raises NotImplementedError (P10 implements it)
- Confirm where `apply_strategy` is called in `markdown_renderer.render` so P10 can swap in the VLM path

---

## PHASE 10 — VLM Image Strategy (OpenRouter)

**Agent role:** VLM integration
**Complexity:** M
**Dependencies:** P9
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P9

**Pre-conditions (verify before starting):**
- [ ] P9 delivered: batch mode working
- [ ] `OPENROUTER_API_KEY` available for manual smoke test (do NOT commit)
- [ ] Tests will mock the OpenRouter API; real key not required for CI

**Step-by-step instructions:**

1. **Add deps**: `openai`, `httpx`, `tenacity` to `pyproject.toml`. Add optional extra `[anthropic]` for later opt-in. Reinstall.
2. **Create `images/vlm_pricing.py`**:
   - `fetch_model_pricing(model_id: str) -> ModelPricing` — `httpx.get("https://openrouter.ai/api/v1/models", timeout=10)` — parse the response, find `model_id`, return prompt and image pricing
   - `estimate_cost(num_images: int, pricing: ModelPricing) -> float`
   - `confirm_cost(estimated_cost: float, threshold: float) -> bool` — interactive prompt if estimated > threshold; non-interactive runs (no TTY) auto-deny if over threshold (log error)
3. **Create `images/vlm_client.py`**:
   - `VlmClient` class. Constructor takes provider, model, api_key.
   - For provider="openrouter": `openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])`
   - For provider="openai": real OpenAI base URL + `OPENAI_API_KEY`
   - For provider="anthropic": import `anthropic` inside function (extra `doc2md[anthropic]`)
   - `describe_image(image_path: Path) -> str`:
     - sha256 the file bytes; check cache at `~/.cache/doc2md/vlm/{hash}.txt`; cache hit → return
     - Build chat completion with image content (base64 data URL); prompt: `"Describe this image as concise alt-text (one sentence). If it contains a chart or table, summarize the data shown."`
     - Wrap in `tenacity.retry`: stop after 3 attempts, exponential backoff 1s→4s, retry only on 429 and 5xx, per-call timeout 30s
     - On terminal failure: raise `VlmError`; caller falls back to placeholder for that image and logs WARNING
     - On success: write cache, return text
4. **Update `rendering/images_strategy.py`**:
   - When strategy="vlm", call `vlm_client.describe_image`; on `VlmError`, fall back to placeholder and log
5. **Update `cli.py`** — add flags:
   - `--images [placeholder|vlm|omit]` (default: placeholder)
   - `--vlm-provider [openrouter|openai|anthropic]` (default: openrouter)
   - `--vlm-model TEXT` (default: None — auto-pick `deepseek/deepseek-vl2-small` for general docs, `deepseek/deepseek-ocr-2` when document_type is `scanned` or `scanned-image`)
   - `--vlm-cost-threshold FLOAT` (default: 1.00)
6. **Update `core/pipeline.py`** — when strategy is vlm and there are extracted images, call `vlm_pricing.confirm_cost` once before processing images. Auto-pick the OCR model when document_type calls for it (per flag rule above).
7. **Tests** per below — mock everything; no real network in CI.
8. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — add `openai`, `httpx`, `tenacity`; optional `[anthropic]`
- `src/doc2md/images/vlm_client.py`, `vlm_pricing.py`
- `src/doc2md/rendering/images_strategy.py` — wire vlm path with placeholder fallback
- `src/doc2md/cli.py` — VLM flags
- `src/doc2md/config.py` — VLM settings fields
- `src/doc2md/core/pipeline.py` — cost confirmation hook + auto OCR model
- Tests below

**Tests to write:**
- `tests/integration/test_vlm_mocked.py`:
  - Mock `openai.OpenAI` to return a known alt-text → MD contains the alt-text
  - Mock to raise 429 twice then succeed → tenacity retries; final output succeeds
  - Mock to always 500 → falls back to placeholder for that image, log captured, batch continues
  - Cache hit (pre-populate cache file) → no API call made (assert mock not called)
  - Cost over threshold + non-interactive → strategy auto-denies and logs error
- `tests/unit/test_vlm_pricing.py`:
  - Mock httpx response → parses pricing correctly
  - `estimate_cost` math is correct
- Existing `tests/unit/test_images_strategy.py` — extend: vlm strategy invokes `VlmClient.describe_image`; on error returns placeholder

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
- `doc2md sample.pdf --images=vlm -o /tmp/out.md` (with valid `OPENROUTER_API_KEY` env) calls OpenRouter for each extracted image, embeds returned alt-text in MD, caches results
- Per-image API failure → that image becomes placeholder, doc continues
- Cost above threshold → user prompted (interactive) or auto-denied (non-interactive)

**Handoff to next phase:**
The Phase Summary for P11a must state:
- Confirm all features functional end-to-end including VLM
- List all installed dependencies that should appear in pyproject.toml
- Confirm optional extras (`[anthropic]`)
- Note any dependency version pins chosen

---

## PHASE 11a — Packaging

**Agent role:** Packaging
**Complexity:** S
**Dependencies:** P10
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P10

**Pre-conditions (verify before starting):**
- [ ] P10 delivered: full feature set working
- [ ] All tests passing
- [ ] `pyproject.toml` exists from prior phases

**Step-by-step instructions:**

1. **Finalize `pyproject.toml`**:
   - `version = "0.1.0"`, `description`, `readme`, `license`, `authors`
   - Classifiers (Python versions, License, Topic)
   - `[project.optional-dependencies]` — `dev` (pytest etc.), `anthropic` (`anthropic` SDK)
   - Console script `doc2md = "doc2md.cli:main"`
2. **Write `scripts/install_wsl.sh`** (`#!/usr/bin/env bash`, `set -euo pipefail`):
   - Step 1: `sudo apt-get update && sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-fra qpdf pandoc libmagic1 poppler-utils`
   - Step 2: detect pipx (`command -v pipx`); if present `pipx install .`; else `pip install --user .`
   - Step 3: `doc2md --version` to verify
   - Clear error message at each failure step (e.g., "apt install failed — check your sudo access")
   - `chmod +x scripts/install_wsl.sh`
3. **Write complete `README.md`**:
   - Project description (one paragraph)
   - Quick install (WSL one-liner: `bash scripts/install_wsl.sh`)
   - Manual install (pipx, pip)
   - Usage examples for every format with expected output snippets
   - Full CLI reference table (every flag from cli.py)
   - Output schema example (small version of §4 template)
   - Environment variables (`OPENROUTER_API_KEY`, optional alternatives)
   - Troubleshooting section (common errors and fixes)
4. **Write `Makefile`** with shortcuts: `install`, `test`, `lint`, `format`, `clean`.
5. **Write `LICENSE`** — MIT.
6. **Write minimal `docs/architecture.md`** (high-level pipeline diagram in text), `docs/output_schema.md` (mirror §4).
7. **Verify** `pipx install .` succeeds in a clean venv (or document the manual verification).
8. **Run quality gates** per §5.

**Files to create/modify:**
- `pyproject.toml` — finalize all metadata
- `scripts/install_wsl.sh`
- `README.md`
- `Makefile`
- `LICENSE`
- `docs/architecture.md`, `docs/output_schema.md`

**Tests to write:**
- `tests/integration/test_install_script.py` (best-effort): assert `scripts/install_wsl.sh` is executable and starts with `#!/usr/bin/env bash`. Skip actual apt steps in CI (would need sudo).
- Smoke test: `doc2md --version` after install returns version string.

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all pre-existing tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% on new modules
- [ ] Phase Summary written

**Output contract:**
- `bash scripts/install_wsl.sh` on a fresh WSL Ubuntu installs system deps and the package, then prints version
- `pipx install .` succeeds
- `doc2md --version` returns `0.1.0`
- README documents all flags and provides usage examples for every format

**Handoff to next phase:**
The Phase Summary for P11b must state:
- Confirm package installs cleanly via pipx
- Confirm README is complete
- Note any installation warnings or platform caveats

---

## PHASE 11b — Quality + CI

**Agent role:** Quality + CI
**Complexity:** S
**Dependencies:** P11a
**Input context this agent receives:**
- This phase block (complete)
- §1 Project Structure
- §4 Output Schema
- §5 Quality Gates
- Phase Summary from: P11a

**Pre-conditions (verify before starting):**
- [ ] P11a delivered: package installable, README complete
- [ ] All tests passing across all phases

**Step-by-step instructions:**

1. **Audit error messages** — grep the codebase for all `raise` and `logger.error` sites. Ensure every error message includes (a) the input file path being processed and (b) a concrete next step (e.g., "provide --password", "install pandoc"). Fix any that don't.
2. **Performance profiling**:
   - Generate or obtain a 500-page digital PDF (test with `reportlab` if needed) and a 50-page scanned PDF
   - Time `doc2md` on each; record time, memory peak (`/usr/bin/time -v`), and any bottlenecks (Docling, Tesseract, image extraction)
   - Document numbers and methodology in `docs/performance.md`
3. **Refine logging**:
   - Default INFO level: terse, useful (one line per file in batch, plus warnings)
   - DEBUG only on `--verbose`
   - Suppress chatty third-party loggers (`docling`, `httpx`, `urllib3`) unless `--verbose`
4. **Add `.github/workflows/ci.yml`**:
   - Trigger on push and PR
   - Matrix: Python 3.10, 3.11, 3.12
   - Steps: checkout, set up Python, `apt install` system deps, `pip install -e ".[dev]"`, `python scripts/generate_fixtures.py`, `ruff check`, `mypy src/doc2md`, `pytest --cov=src/doc2md --cov-report=term-missing --cov-fail-under=80`
5. **Tests** per below.
6. **Run quality gates** per §5.

**Files to create/modify:**
- `docs/performance.md` — benchmark results and methodology
- `.github/workflows/ci.yml`
- Audited error messages across the codebase
- Logging refinements in `logging_setup.py`

**Tests to write:**
- `tests/unit/test_logging.py`: with verbose=False, third-party loggers suppressed; with verbose=True, DEBUG records emitted
- Where error messages were updated, ensure existing tests still assert on the new wording (or update assertions)

**Quality gate checklist (mandatory before delivery):**
- [ ] `ruff check src/ tests/` — zero errors
- [ ] `mypy src/doc2md` — zero new type errors
- [ ] `pytest tests/` — all tests pass
- [ ] `pytest --cov=src/doc2md --cov-report=term-missing` — ≥80% overall
- [ ] CI workflow file syntactically valid (run `actionlint` or equivalent)
- [ ] Phase Summary written

**Output contract:**
- CI passes on a fresh push to a feature branch (matrix: 3.10/3.11/3.12)
- `docs/performance.md` exists and documents 500-page and 50-page benchmarks
- Logging is clean at default INFO; verbose adds DEBUG; third-party noise suppressed
- Error messages all include file path + next step

**Handoff to next phase:**
None — this is the final phase. Cut release tag `v0.1.0`.

---

EXECUTION DOCUMENT READY — HAND TO PHASE 0
