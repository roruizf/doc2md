# doc2md

[![CI](https://github.com/roruizf/doc2md/actions/workflows/ci.yml/badge.svg)](https://github.com/roruizf/doc2md/actions/workflows/ci.yml)
[![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/roruizf/doc2md/main/pyproject.toml)](https://github.com/roruizf/doc2md/blob/main/pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/release/roruizf/doc2md)](https://github.com/roruizf/doc2md/releases)

doc2md converts PDFs, DOCX, ODT, EPUB, HTML, TXT, and standalone images into schema-compliant Markdown with YAML frontmatter, page anchors, extracted images, optional OCR, batch conversion, and optional VLM-generated image alt text.

## Quick Install On WSL

```bash
bash scripts/install_wsl.sh
```

The installer adds system tools used by the converters: Tesseract, qpdf, pandoc, libmagic, and poppler utilities. It then installs doc2md with `pipx` when available, otherwise with `pip install --user`.

## Manual Install

```bash
pipx install .
```

or:

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
```

Optional Anthropic VLM support:

```bash
python -m pip install ".[anthropic]"
```

## Usage

Single file:

```bash
doc2md tests/fixtures/sample_digital.pdf -o /tmp/sample.md
doc2md tests/fixtures/sample.docx -o /tmp/sample.md
doc2md tests/fixtures/sample.odt -o /tmp/sample.md
doc2md tests/fixtures/sample.epub -o /tmp/sample.md
doc2md tests/fixtures/sample.html -o /tmp/sample.md
doc2md tests/fixtures/sample.txt -o /tmp/sample.md
doc2md tests/fixtures/sample_image.png -o /tmp/sample.md --ocr-lang eng
```

Batch conversion:

```bash
doc2md tests/fixtures/ -o /tmp/doc2md-out --recursive
doc2md tests/fixtures/ -o /tmp/doc2md-flat --recursive --flatten
```

Images:

```bash
doc2md report.pdf -o out.md --images placeholder
doc2md report.pdf -o out.md --images omit
OPENROUTER_API_KEY=... doc2md report.pdf -o out.md --images vlm
```

Example output fragment:

```markdown
---
schema_version: "1.0"
title: "sample_digital"
source_file: "sample_digital.pdf"
format: "pdf"
page_count: 3
document_type: "digital"
language: "en"
ocr_applied: false
images_strategy: "placeholder"
converter_version: "0.1.0"
---

<a id="page-1"></a>
**[Page 1]**

# Sample Digital PDF
```

## CLI Reference

| Flag | Default | Description |
| --- | --- | --- |
| `INPUT_PATH` | required | File or directory to convert. |
| `--output`, `-o` | required | Output Markdown file for single-file input, or output directory for batch input. |
| `--images` | `placeholder` | Image handling: `placeholder`, `omit`, or `vlm`. |
| `--ocr-lang` | auto/`None` | Tesseract language code, for example `eng` or `fra`. |
| `--ocr-engine` | `docling` | OCR engine for scanned PDFs: `docling` or `direct`. |
| `--password` | `None` | Password for encrypted PDFs. |
| `--vlm-provider` | `openrouter` | VLM provider: `openrouter`, `openai`, or `anthropic`. |
| `--vlm-model` | auto | Model ID. Defaults to DeepSeek VL models depending on document type. |
| `--vlm-cost-threshold` | `1.0` | Prompt/deny threshold for estimated VLM cost. |
| `--recursive`, `-r` | off | Recurse into directories during batch conversion. |
| `--flatten` | off | Write all batch outputs into one directory with disambiguated names. |
| `--no-progress` | off | Disable tqdm progress output in batch mode. |
| `--verbose` | off | Enable verbose logging. |
| `--version` | off | Print the package version. |

## Output Schema

Every output starts with YAML frontmatter:

```yaml
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
```

Page anchors use this fixed form:

```markdown
<a id="page-1"></a>
**[Page 1]**
```

## Environment Variables

| Variable | Used For |
| --- | --- |
| `OPENROUTER_API_KEY` | OpenRouter VLM image descriptions. |
| `OPENAI_API_KEY` | OpenAI provider VLM image descriptions. |
| `ANTHROPIC_API_KEY` | Anthropic provider VLM image descriptions. |
| `DOC2MD_VLM_CACHE_DIR` | Override VLM cache directory. |
| `DOC2MD_NO_PROGRESS=1` | Disable batch progress output. |

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `pandoc binary not found` | Install `pandoc` with `sudo apt-get install pandoc`. |
| `python -m venv` fails with `ensurepip` | Install `python3-venv` or use `uv venv` on WSL. |
| Fresh install downloads CUDA packages | `docling` depends on PyTorch; on some Linux setups pip resolves large CUDA wheels. Use a CPU-only PyTorch index before installing if disk or bandwidth is limited. |
| `tesseract not found` or empty OCR | Install `tesseract-ocr` and language packs such as `tesseract-ocr-eng`. |
| Locked PDF fails | Pass `--password PASSWORD`. |
| `libmagic` errors | Install `libmagic1` on Ubuntu/WSL. |
| VLM cost denied | Increase `--vlm-cost-threshold` or run interactively to approve. |
| VLM auth error | Set `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY`. |
| Batch stops showing progress in CI | Use `--no-progress` or `DOC2MD_NO_PROGRESS=1`. |
