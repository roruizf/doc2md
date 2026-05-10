# doc2md Capabilities

This page describes what doc2md is designed to do, what it does not guarantee,
and where users should expect tradeoffs.

## What doc2md Can Do

### PDF

- Convert digital PDFs with selectable text to Markdown.
- Use Docling for layout-aware digital PDF extraction.
- Fall back to PyMuPDF raw extraction when Docling fails.
- Classify PDFs as digital, scanned, mixed, or locked.
- OCR scanned PDFs with Docling OCR or direct Tesseract.
- Emit structured OCR quality metrics in frontmatter for scanned, mixed, and
  standalone image OCR outputs.
- Combine digital extraction and OCR for mixed PDFs.
- Unlock password-protected PDFs when the correct password is supplied.
- Extract PDF images into `images/` and reference them from Markdown.

### DOCX

- Convert headings, paragraphs, and tables.
- Extract embedded images from `word/media/`.
- Synthesize page anchors by section when section breaks are available.
- Fall back to `python-docx` for deterministic conversion behavior.

### ODT

- Convert ODT files through pandoc.
- Extract ODT media through pandoc's media extraction path.
- Normalize images into doc2md naming conventions.

### EPUB

- Read EPUB metadata such as title and language.
- Convert spine-ordered chapter documents into Markdown.
- Emit one anchor per chapter.
- Extract EPUB images and associate them with the chapter that references them
  when possible.

### HTML

- Convert HTML to Markdown through MarkItDown with a BeautifulSoup/markdownify
  fallback.
- Extract local images referenced by the HTML file.

### TXT

- Detect text encoding with chardet.
- Convert plain text into schema-compliant Markdown.
- Infer simple headings from all-caps or underlined text.

### Standalone Images

- OCR standalone images with Tesseract.
- Emit OCR confidence, text density, suspicious-character, language fallback,
  and degraded-condition metadata in frontmatter.
- Copy the source image as a figure.
- Emit `document_type: "scanned-image"`.

### Batch and Images

- Convert single files or directories.
- Walk directories recursively with `--recursive`.
- Flatten outputs with `--flatten`.
- Use configurable image strategies: `placeholder`, `omit`, or `vlm`.
- Generate VLM image descriptions through OpenRouter, OpenAI, or Anthropic.

## What doc2md Does NOT Guarantee

- Perfect layout fidelity. Markdown is a structured text target, not a visual
  clone of the original document.
- Perfect OCR. Low-resolution scans, handwriting, skewed pages, and unusual
  fonts can degrade output.
- Exact pagination in HTML, TXT, DOCX, ODT, or EPUB. These formats do not always
  have stable page boundaries, so doc2md may synthesize anchors by section,
  chapter, or document.
- DRM bypass. doc2md can use a provided PDF password; it does not bypass DRM or
  remove access controls without valid credentials.
- Fast processing on large scanned PDFs. OCR and layout analysis are expensive.
- Zero cost when VLM is active. Provider APIs may bill for image descriptions.

## Strengths

- Broad format coverage across PDFs, office documents, ebooks, HTML, text, and
  standalone images.
- Unified Markdown output with stable frontmatter and anchors.
- Configurable image strategies for lightweight, image-free, or AI-described
  outputs.
- OCR support for scanned PDFs and standalone images.
- Structured OCR quality metadata that lets external systems score reliability
  by reading frontmatter only.
- Locked PDF support when the password is available.
- CLI-first workflow that works well in shell scripts and batch jobs.
- Tested conversion paths and GitHub Actions CI.

## Known Limitations

- Docling and PyTorch are heavy dependencies. Fresh installs can download large
  wheels on Linux/WSL, especially when pip resolves CUDA-enabled packages.
- Docling may download models on first run. Expect a one-time cache population.
- VLM mode requires network access, provider credentials, and may incur cost.
- Complex tables can degrade, especially with merged cells, nested tables, or
  unusual PDF layouts.
- Docling OCR paths may not expose per-word confidence to doc2md; in that case
  `ocr_confidence_mean` is `null` and `ocr_degraded_conditions` includes
  `ocr_confidence_unavailable`.
- Full large-document benchmark data still needs to be collected in a long-lived
  runner before a public performance claim.

## Performance Reference

See [performance.md](./performance.md) for methodology, current smoke
measurements, bottlenecks, and the release benchmark plan.
