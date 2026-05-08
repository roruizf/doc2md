# AI Integration Guide

doc2md output is designed to work well as AI agent context and as a retrieval
layer for RAG systems. The key features are stable anchors, frontmatter, and a
Document Index.

## Page Anchors for Cross-References

Every page-like unit starts with a stable anchor:

```markdown
<a id="page-50"></a>
**[Page 50]**
```

If a user asks an LLM to "see page 50, Table 3", the application can map that
request to `#page-50`, retrieve the chunk beginning at that anchor, and inspect
nearby table text. The same pattern works for citations, review comments, and
agent tool calls.

Recommended cross-reference behavior:

1. Detect references such as "page 50", "p. 50", or "Table 3".
2. Resolve the page reference to `#page-50`.
3. Retrieve that page chunk plus a small window before and after it.
4. Ask the model to answer with the anchor included in its citation.

## Document Index as a Map

When available, doc2md appends:

```markdown
## Document Index

### Pages
- [Page 1](#page-1)

### Sections
- [Executive Summary](#page-1)

### Tables
- [Table 1](#page-2)
```

Give the index to an LLM before the full body when the document is long. The
index helps the model form a map of the document and decide which pages or
sections to inspect first.

## Python Usage as a Library

The CLI is the primary interface, but doc2md also exposes a small Python helper:

```python
from pathlib import Path

from doc2md import convert

result = convert(Path("report.pdf"), images_strategy="placeholder")

# result.markdown is ready to pass as context.
markdown_context = result.markdown
```

To control where the Markdown and `images/` directory are written:

```python
from pathlib import Path

from doc2md import convert

result = convert(
    Path("report.pdf"),
    output_path=Path("build/report.md"),
    images_strategy="placeholder",
)
```

## Passing Output to OpenRouter

This example sends converted Markdown as system context through the OpenAI SDK
configured for OpenRouter:

```python
import os
from pathlib import Path

from openai import OpenAI

from doc2md import convert

result = convert(Path("report.pdf"), images_strategy="placeholder")

client = OpenAI(
    api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1",
)

response = client.chat.completions.create(
    model="openai/gpt-4.1-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "You answer questions using this converted document. "
                "Cite page anchors such as #page-12 when relevant.\n\n"
                f"{result.markdown}"
            ),
        },
        {
            "role": "user",
            "content": "Summarize the financial highlights and cite pages.",
        },
    ],
)

print(response.choices[0].message.content)
```

## Chunking Strategy

Chunk by page anchor boundaries whenever possible. This preserves references and
keeps chunks aligned with user-visible citations.

Recommended process:

1. Split on lines matching `<a id="page-N"></a>`.
2. Keep the page anchor and `**[Page N]**` marker at the start of each chunk.
3. For very short pages, merge adjacent pages until a target token range is
   reached.
4. For very long pages, split by headings inside the page while preserving the
   original page anchor in chunk metadata.
5. Store metadata such as `source_file`, `page_anchor`, `page_number`,
   `document_type`, and `date_converted`.

Example chunk metadata:

```json
{
  "source_file": "report.pdf",
  "page_anchor": "page-50",
  "page_number": 50,
  "document_type": "digital"
}
```
