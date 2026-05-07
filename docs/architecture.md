# doc2md Architecture

```text
CLI
 |
 |-- detect input type
 |-- dispatch converter
 |-- convert into MarkdownDocument
 |-- extract/copy images
 |-- render Markdown
 |-- validate frontmatter, anchors, image paths
 '-- write output
```

## Main Components

- `doc2md.cli`: Typer command line interface for single-file and batch conversion.
- `doc2md.core.detector`: extension and MIME-based format detection.
- `doc2md.core.dispatcher`: maps detected formats to converters.
- `doc2md.core.pipeline`: orchestration for conversion, image extraction, rendering, validation, and cleanup.
- `doc2md.converters`: format-specific conversion into the shared `MarkdownDocument` model.
- `doc2md.rendering`: frontmatter, page anchors, image strategy, index, sanitization, and final Markdown assembly.
- `doc2md.images`: image extraction, naming, VLM pricing, and VLM image descriptions.
- `doc2md.ocr`: direct Tesseract OCR helpers.
- `doc2md.utils`: filesystem traversal, output path mapping, PDF unlock helpers, and progress display.

## Data Flow

Converters do not write Markdown files directly. They return a `MarkdownDocument` with frontmatter, pages, and index entries. The shared pipeline extracts images into an `images/` directory next to the output, calls the renderer, validates the rendered Markdown, and writes the final file.

Batch mode repeats this single-file pipeline per input file. Failures are isolated per file and reported in the end-of-batch summary.
