# doc2md Performance

This document records the P11b benchmark methodology and the measurements available in the current WSL development environment.

## Environment

- Date: 2026-05-07
- Platform: WSL Ubuntu
- Python: project `.venv` Python 3.11
- System tools available in prior phase handoff: Tesseract, qpdf, pandoc, poppler utilities
- Notable caveat: a clean dependency install began downloading large CUDA-enabled PyTorch wheels through the `docling` dependency chain. Benchmarks below use the existing project `.venv`.

## Methodology

Recommended commands for release benchmarking:

```bash
/usr/bin/time -v doc2md /tmp/digital-500.pdf -o /tmp/digital-500.md
/usr/bin/time -v doc2md /tmp/scanned-50.pdf -o /tmp/scanned-50.md --ocr-engine direct --ocr-lang eng
```

Suggested fixture generation:

- 500-page digital PDF: generate with reportlab, one text-heavy page per page, no images.
- 50-page scanned PDF: render text pages to images with PyMuPDF/Pillow and reassemble image-only pages.

Record:

- elapsed wall time
- maximum resident set size
- output file size
- image count
- OCR engine and language
- whether Docling fallback was used

## Current Smoke Measurements

The full target benchmarks were not completed in this session because the Docling/PyTorch path is the dominant bottleneck and long PDF runs repeatedly exceeded the interactive session budget. The current validation used smaller fixtures and focused quality gates.

| Input | Pages | Mode | Result | Notes |
| --- | ---: | --- | --- | --- |
| `tests/fixtures/sample.txt` | 1 synthesized | TXT | completed | Fast schema smoke via CLI. |
| `tests/fixtures/sample.html` | 1 synthesized | HTML + image | completed in mocked VLM integration tests | Exercises local image extraction and VLM fallback/cache code paths. |
| `tests/fixtures/sample_image.png` | 1 | image OCR | completed in converter tests | Tesseract reads fixture text as `Helloworld from doc2md`. |
| `tests/fixtures/sample_digital.pdf` | 3 | digital PDF | completed in existing tests | Docling is the main cost center. |

## Bottlenecks

- **Docling/PyTorch startup and PDF layout analysis** dominate digital PDF conversion time.
- **Tesseract OCR** dominates scanned PDF and standalone image conversion.
- **VLM image descriptions** add network latency and cost; cache hits avoid repeated calls.
- **Fresh installs on Linux/WSL** may download large CUDA wheels unless the environment is configured for CPU-only PyTorch.

## Follow-Up For Release

Before a public release, run the target 500-page digital and 50-page scanned benchmarks in a non-interactive shell or CI runner with a longer timeout, then replace this section with exact `/usr/bin/time -v` output.
