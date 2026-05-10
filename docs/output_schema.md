# doc2md Output Schema

doc2md writes Markdown with YAML frontmatter followed by page anchors and page content.

## Frontmatter

```yaml
schema_version: "1.0"
title: string
source_file: string
format: pdf | docx | odt | epub | html | txt | image
page_count: int | null
date_converted: ISO 8601 string
document_type: digital | scanned | mixed | scanned-image | html | txt | epub | docx | odt
language: string | null
ocr_applied: bool
ocr_confidence_mean: float | null
ocr_confidence_min: float | null
ocr_low_confidence_pages: int | null
ocr_text_chars: int | null
ocr_text_chars_per_page: float | null
ocr_suspicious_char_ratio: float | null
ocr_language_requested: string | null
ocr_language_used: string | null
ocr_language_fallback_used: bool | null
ocr_degraded_conditions: list[string] | null
images_strategy: placeholder | vlm | omit
converter_version: string
```

OCR quality fields are optional and nullable. They are populated when
`ocr_applied: true`, especially for direct Tesseract OCR paths. For digital
documents, these fields are `null`.

| Field | Meaning |
| --- | --- |
| `ocr_confidence_mean` | Mean Tesseract confidence, 0-100, across recognized words/pages when available. |
| `ocr_confidence_min` | Lowest Tesseract confidence observed when available. |
| `ocr_low_confidence_pages` | Count of OCRed pages below the internal low-confidence threshold. |
| `ocr_text_chars` | Total extracted OCR text characters. |
| `ocr_text_chars_per_page` | Average extracted OCR text characters per page-like unit. |
| `ocr_suspicious_char_ratio` | Ratio of unusual replacement/control characters to non-space characters. |
| `ocr_language_requested` | Tesseract language requested by the user or auto resolver. |
| `ocr_language_used` | Language actually used by Tesseract after any fallback. |
| `ocr_language_fallback_used` | Whether OCR had to retry with a fallback language. |
| `ocr_degraded_conditions` | Machine-readable degradation labels such as `low_text_density`, `low_mean_confidence`, `ocr_confidence_unavailable`, or `ocr_language_fallback_used`. |

## Page Anchors

Every page starts with:

```markdown
<a id="page-N"></a>
**[Page N]**
```

## Images

Extracted images are written relative to the Markdown output:

```text
images/fig1_page3.png
```

With `--images placeholder`, images render as:

```markdown
![Figure 1 - Page 3 image](images/fig1_page3.png)
```

With `--images omit`, image files are not extracted for converters that support omission.

With `--images vlm`, doc2md asks the configured VLM provider for concise alt text and falls back to the placeholder description on API failure or denied cost.

## Index

When entries are available, doc2md appends a document index grouped by pages, sections, tables, and figures.
