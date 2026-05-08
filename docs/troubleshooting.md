# Troubleshooting

This guide covers the most common setup and conversion issues.

## Tesseract Not Found on PATH

Symptom:

```text
tesseract not found
```

Fix on Ubuntu/WSL:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
```

Install additional language packs as needed:

```bash
sudo apt-get install -y tesseract-ocr-spa tesseract-ocr-fra
```

Then retry with an explicit language:

```bash
doc2md scanned.pdf -o scanned.md --ocr-lang eng
```

## Docling Downloads Models on First Run

Docling may download models the first time a PDF conversion path needs them.
This is expected behavior. Depending on platform and dependency resolution, the
initial setup can require roughly 1-2 GB for model and PyTorch-related cache
data.

Typical cache location:

```text
~/.cache/docling/
```

The download should happen once per environment/cache. Later conversions reuse
the cached files.

## PDF Conversion Fails or Produces Little Output

First enable verbose logs:

```bash
doc2md report.pdf -o report.md --verbose
```

If the PDF is scanned or layout analysis is struggling, try direct OCR:

```bash
doc2md report.pdf -o report.md --ocr-engine=direct --ocr-lang eng --verbose
```

If the file is encrypted, pass `--password`.

## OPENROUTER_API_KEY Not Found

`--images=vlm` with the OpenRouter provider requires `OPENROUTER_API_KEY`.

Set it for the current WSL shell:

```bash
export OPENROUTER_API_KEY="your_key"
```

Persist it in WSL:

```bash
echo 'export OPENROUTER_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

For local development, copy `.env.example` to `.env` and fill it in. Shells do
not load `.env` automatically; source it or use your preferred dotenv tooling.

```bash
set -a
source .env
set +a
```

## Locked PDF Not Unlocking

If a locked PDF fails, check these cases:

- The password may be wrong.
- The PDF may use permissions or DRM that qpdf cannot bypass.
- The file may be damaged.

doc2md can use a valid password to decrypt a PDF for conversion. It does not
bypass DRM or remove access controls without credentials.

## Large PDFs Are Slow

Digital PDF conversion is dominated by Docling/PyTorch layout analysis. Scanned
PDF conversion is dominated by OCR. Large scanned PDFs can take minutes or more
depending on page count, resolution, and CPU.

See [performance.md](./performance.md) for the current performance notes and
release benchmark plan.

For faster scanned-PDF troubleshooting, try:

```bash
doc2md large-scanned.pdf -o large-scanned.md --ocr-engine=direct --ocr-lang eng
```

## libmagic Not Found

Symptom:

```text
ImportError: failed to find libmagic
```

Fix on Ubuntu/WSL:

```bash
sudo apt-get update
sudo apt-get install -y libmagic1
```

Then reinstall doc2md if needed:

```bash
python -m pip install -e ".[dev]"
```
