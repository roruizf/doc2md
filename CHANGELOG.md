# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to semantic versioning once public releases begin.

## [0.1.0] - 2026-05-08

### Added

#### Core

- Canonical `MarkdownDocument`, `Frontmatter`, `Page`, and `IndexEntry` models.
- Format detection and dispatcher routing.
- Shared conversion pipeline with validation before output writing.
- Public Python helper `doc2md.convert(...)` returning `ConvertResult.markdown`.
- Structured settings for image strategy, OCR, PDF passwords, and VLM options.

#### Converters

- Digital PDF conversion with Docling primary extraction and PyMuPDF fallback.
- Scanned PDF OCR through Docling or direct Tesseract.
- Mixed PDF handling for files with both digital and scanned pages.
- Password-protected PDF conversion when a valid password is supplied.
- DOCX conversion with heading, table, section, and image handling.
- ODT conversion through pandoc with media extraction.
- EPUB conversion with metadata, spine chapter ordering, and image extraction.
- HTML conversion through MarkItDown with BeautifulSoup/markdownify fallback.
- TXT conversion with encoding detection and heading inference.
- Standalone image OCR conversion.

#### Rendering

- YAML frontmatter rendering.
- Stable page and chapter anchors.
- Markdown sanitization.
- GitHub-flavored table rendering.
- End-of-document index grouped by pages, sections, tables, and figures.
- Output validation for required fields, anchors, and image references.

#### Images/VLM

- Deterministic extracted image naming under `images/`.
- `placeholder`, `omit`, and `vlm` image strategies.
- OpenRouter/OpenAI-compatible VLM image descriptions.
- Optional Anthropic VLM provider extra.
- VLM response caching under `~/.cache/doc2md/vlm/`.
- VLM cost estimation and threshold confirmation.
- Environment overrides for default VLM model and cost threshold.

#### CLI

- `doc2md` console script.
- Single-file conversion.
- Directory batch conversion.
- Recursive and flattened batch output modes.
- Progress display with opt-out.
- OCR language and engine flags.
- PDF password flag.
- VLM provider, model, and cost threshold flags.
- Verbose logging and version output.

#### Testing

- Unit tests for rendering, validation, image strategies, VLM behavior, and
  utilities.
- Converter tests for supported formats.
- Integration tests for full pipeline behavior.
- GitHub Actions CI across Python 3.10, 3.11, and 3.12.
- Coverage gate configured at 80 percent.

#### Docs

- README with install, usage, CLI, schema, environment, and troubleshooting
  sections.
- Architecture reference.
- Output schema reference.
- Performance notes and benchmark methodology.
- User manual, capabilities guide, AI integration guide, troubleshooting guide,
  contributing guide, security notes, changelog, environment example, and sample
  input/output examples.
