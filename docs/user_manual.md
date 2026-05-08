# doc2md User Manual

doc2md converts documents into Markdown designed for humans, archives, and AI
systems. Outputs include YAML frontmatter, stable page or chapter anchors,
extracted images, and a Document Index when converter metadata is available.

## Installation

### WSL one-liner

From the repository root:

```bash
bash scripts/install_wsl.sh
```

The WSL installer installs system tools used by different converters:
Tesseract, qpdf, pandoc, libmagic, and poppler utilities. It then installs
doc2md with `pipx` when available, or falls back to `pip install --user`.

### Manual system dependencies

On Ubuntu or WSL:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf pandoc libmagic1 poppler-utils
```

Add extra Tesseract language packs when needed, for example:

```bash
sudo apt-get install -y tesseract-ocr-spa tesseract-ocr-fra
```

### Install with pipx

`pipx` is the cleanest option for CLI use:

```bash
pipx install .
doc2md --version
```

### Install with pip

```bash
python -m pip install .
doc2md --version
```

For development:

```bash
python -m pip install -e ".[dev]"
```

Optional Anthropic VLM support:

```bash
python -m pip install -e ".[dev,anthropic]"
```

## First Use

The simplest conversion is one input file and one output Markdown file:

```bash
doc2md tests/fixtures/sample_digital.pdf -o /tmp/sample.md
```

Open `/tmp/sample.md`. It will begin with YAML frontmatter, then page anchors
and converted body text.

## Format Examples

### Digital PDF

Use this for PDFs that already contain selectable text:

```bash
doc2md tests/fixtures/sample_digital.pdf -o /tmp/sample_digital.md
```

Expected behavior:

- `format: "pdf"`
- `document_type: "digital"`
- `ocr_applied: false`
- one anchor per PDF page, such as `<a id="page-1"></a>`

### Scanned PDF

Use OCR for image-only PDFs:

```bash
doc2md tests/fixtures/sample_scanned.pdf -o /tmp/sample_scanned.md --ocr-lang eng
```

For a faster, direct Tesseract path:

```bash
doc2md tests/fixtures/sample_scanned.pdf -o /tmp/sample_scanned.md --ocr-engine direct --ocr-lang eng
```

Expected behavior:

- `document_type: "scanned"`
- `ocr_applied: true`
- OCR text appears under page anchors

### Password-Protected PDF

Pass the owner/user password with `--password`:

```bash
doc2md tests/fixtures/sample_locked.pdf -o /tmp/sample_locked.md --password secret
```

doc2md can unlock encrypted PDFs when the correct password is supplied. It does
not bypass DRM or remove access controls without valid credentials.

### DOCX

```bash
doc2md tests/fixtures/sample.docx -o /tmp/sample_docx.md
```

Expected behavior:

- headings become Markdown headings
- tables are rendered as GitHub-flavored Markdown tables when possible
- embedded images are copied to an `images/` directory next to the output file

### ODT

```bash
doc2md tests/fixtures/sample.odt -o /tmp/sample_odt.md
```

ODT conversion uses pandoc and standard doc2md image naming. Install pandoc if
this command fails with a missing binary error.

### EPUB

```bash
doc2md tests/fixtures/sample.epub -o /tmp/sample_epub.md
```

Expected behavior:

- `format: "epub"`
- `document_type: "epub"`
- one anchor per spine chapter
- EPUB metadata is used for title/language when available

### HTML

```bash
doc2md tests/fixtures/sample.html -o /tmp/sample_html.md
```

Local image references are copied into `images/` when they can be resolved from
the HTML file location.

### TXT

```bash
doc2md tests/fixtures/sample.txt -o /tmp/sample_txt.md
```

doc2md detects encoding with chardet and applies simple heading inference for
plain text.

### Standalone Image

```bash
doc2md tests/fixtures/sample_image.png -o /tmp/sample_image.md --ocr-lang eng
```

The image is OCRed with Tesseract and copied as figure 1 next to the Markdown
output.

## Batch Mode

### Convert a Directory

```bash
doc2md tests/fixtures -o /tmp/doc2md-out
```

This converts supported files directly inside `tests/fixtures`.

### Recursive Conversion

```bash
doc2md tests/fixtures -o /tmp/doc2md-out --recursive
```

Subdirectories are walked recursively. Output paths mirror the input tree.

### Flattened Output

```bash
doc2md tests/fixtures -o /tmp/doc2md-flat --recursive --flatten
```

All Markdown files are written directly under `/tmp/doc2md-flat` with
disambiguated names.

### Batch Without Progress

```bash
doc2md tests/fixtures -o /tmp/doc2md-out --recursive --no-progress
```

Use this in CI logs or non-interactive scripts.

## Image Strategies

### Placeholder

```bash
doc2md report.pdf -o report.md --images=placeholder
```

Images are extracted and referenced with deterministic placeholder alt text.

### Omit

```bash
doc2md report.pdf -o report.md --images=omit
```

Image references are omitted from Markdown. For converters that extract images
after conversion, files may be skipped or ignored depending on converter path.

### VLM

```bash
export OPENROUTER_API_KEY="your_key"
doc2md report.pdf -o report.md \
  --images=vlm \
  --vlm-provider openrouter \
  --vlm-model deepseek/deepseek-vl2-small
```

For scanned or image-heavy documents, you can choose an OCR-oriented model:

```bash
doc2md scanned.pdf -o scanned.md \
  --images=vlm \
  --vlm-provider openrouter \
  --vlm-model deepseek/deepseek-ocr-2 \
  --vlm-cost-threshold 2.00
```

VLM descriptions require network access, provider credentials, and may incur
provider charges. Results are cached under `~/.cache/doc2md/vlm/` by default.

## CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `INPUT_PATH` | path | required | File or directory to convert. |
| `--output`, `-o` | path | required | Output Markdown file for a single input, or output directory for batch mode. |
| `--images` | enum | `placeholder` | Image strategy: `placeholder`, `omit`, or `vlm`. |
| `--ocr-lang` | string | `None` | Tesseract language code, for example `eng`, `spa`, or `fra`. |
| `--ocr-engine` | enum | `docling` | OCR engine for scanned PDFs: `docling` or `direct`. |
| `--password` | string | `None` | Password for encrypted PDFs. |
| `--vlm-provider` | enum | `openrouter` | VLM provider: `openrouter`, `openai`, or `anthropic`. |
| `--vlm-model` | string | auto | VLM model ID. If omitted, doc2md chooses a default by document type or uses `DOC2MD_VLM_MODEL`. |
| `--vlm-cost-threshold` | float | `1.0` | Prompt or deny threshold for estimated VLM cost. Can be overridden with `DOC2MD_VLM_COST_THRESHOLD`. |
| `--recursive`, `-r` | bool | `false` | Recurse into subdirectories in batch mode. |
| `--flatten` | bool | `false` | Write all batch outputs directly under the output directory. |
| `--no-progress` | bool | `false` | Disable progress output in batch mode. |
| `--verbose` | bool | `false` | Enable verbose doc2md logging and less suppression of third-party logs. |
| `--version` | bool | `false` | Print the doc2md version. |

## Reading Generated Markdown

### Frontmatter

Every output begins with YAML frontmatter:

```yaml
schema_version: "1.0"
title: "Annual Report"
source_file: "annual_report.pdf"
format: "pdf"
page_count: 50
date_converted: "2026-05-08T10:00:00+07:00"
document_type: "digital"
language: "en"
ocr_applied: false
images_strategy: "placeholder"
converter_version: "0.1.0"
```

Fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Output schema version. |
| `title` | Best available title from metadata or filename. |
| `source_file` | Original input filename. |
| `format` | Detected source format. |
| `page_count` | Page, chapter, or synthesized page count when known. |
| `date_converted` | ISO 8601 conversion timestamp. |
| `document_type` | More specific classification, such as `digital`, `scanned`, `mixed`, `epub`, or `scanned-image`. |
| `language` | Detected or metadata-provided language when available. |
| `ocr_applied` | Whether OCR was used. |
| `images_strategy` | Image rendering strategy used for this output. |
| `converter_version` | doc2md converter version. |

### Page Anchors

Each page or synthesized page begins with:

```markdown
<a id="page-1"></a>
**[Page 1]**
```

These anchors let humans and AI systems jump to stable locations such as
`#page-1`, `#page-50`, or chapter-level anchors in EPUB output.

### Document Index

When index entries are available, doc2md appends:

```markdown
## Document Index

### Pages
- [Page 1](#page-1)

### Sections
- [Executive Summary](#page-1)
```

The index groups pages, sections, tables, and figures. It is especially useful
for navigation, review, and retrieval workflows.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `OPENROUTER_API_KEY` | for `--images=vlm --vlm-provider openrouter` | OpenRouter API key used for VLM image descriptions. |
| `OPENAI_API_KEY` | for `--vlm-provider openai` | OpenAI API key for VLM image descriptions. |
| `ANTHROPIC_API_KEY` | for `--vlm-provider anthropic` | Anthropic API key; install `doc2md[anthropic]` first. |
| `DOC2MD_VLM_MODEL` | optional | Default VLM model when `--vlm-model` is omitted. |
| `DOC2MD_VLM_COST_THRESHOLD` | optional | Default VLM cost threshold. |
| `DOC2MD_VLM_CACHE_DIR` | optional | Override VLM cache directory. |
| `DOC2MD_NO_PROGRESS` | optional | Disable batch progress when set to `1`. |

In WSL, add keys to `~/.bashrc`:

```bash
export OPENROUTER_API_KEY="your_key"
```

Then reload the shell:

```bash
source ~/.bashrc
```
