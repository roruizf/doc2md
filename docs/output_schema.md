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
images_strategy: placeholder | vlm | omit
converter_version: string
```

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
