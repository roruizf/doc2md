import logging
import re
from datetime import datetime
from pathlib import Path

import chardet
from langdetect import LangDetectException, detect

from doc2md.config import Settings
from doc2md.core.base_converter import BaseConverter
from doc2md.core.document import Frontmatter, IndexEntry, MarkdownDocument, Page

LOGGER = logging.getLogger(__name__)


class TxtConverter(BaseConverter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()

    def convert(self, input_path: Path) -> MarkdownDocument:
        text = _read_text(input_path)
        markdown = _infer_sections(text)
        page = Page(number=1, anchor_id="page-1", content=markdown.strip())
        language = _detect_language(page.content)
        return MarkdownDocument(
            frontmatter=_frontmatter(input_path, language, self.settings),
            pages=[page],
            index_entries=_index_entries(page),
        )


def _read_text(input_path: Path) -> str:
    raw = input_path.read_bytes()
    detected = chardet.detect(raw)
    encoding = str(detected.get("encoding") or "utf-8")
    confidence = float(detected.get("confidence") or 0.0)
    if confidence < 0.7:
        LOGGER.warning(
            "Low confidence text encoding detection for %s; using UTF-8 replacement",
            input_path,
        )
        return raw.decode("utf-8", errors="replace")
    return raw.decode(encoding, errors="replace")


def _infer_sections(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        next_line = lines[index + 1].strip() if index + 1 < len(lines) else ""
        if _is_underline(next_line, "="):
            output.append(f"# {line.strip()}")
            index += 2
            continue
        if _is_underline(next_line, "-"):
            output.append(f"## {line.strip()}")
            index += 2
            continue
        stripped = line.strip()
        if _is_all_caps_heading(stripped) and not _is_numbered_line(line):
            output.append(f"## {stripped}")
        else:
            output.append(line)
        index += 1
    return "\n".join(output)


def _is_underline(line: str, character: str) -> bool:
    return len(line) >= 3 and set(line) == {character}


def _is_all_caps_heading(line: str) -> bool:
    return len(line) >= 3 and any(char.isalpha() for char in line) and line == line.upper()


def _is_numbered_line(line: str) -> bool:
    return re.match(r"^\d+(?:\.\d+)*\.\s+", line) is not None


def _detect_language(text: str) -> str | None:
    try:
        return detect(text)
    except LangDetectException:
        return None


def _frontmatter(input_path: Path, language: str | None, settings: Settings) -> Frontmatter:
    return Frontmatter(
        schema_version="1.0",
        title=input_path.stem,
        source_file=input_path.name,
        format="txt",
        page_count=None,
        date_converted=datetime.now().astimezone().isoformat(),
        document_type="txt",
        language=language,
        ocr_applied=False,
        images_strategy=settings.images_strategy,
        converter_version=settings.converter_version,
    )


def _index_entries(page: Page) -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    for line in page.content.splitlines():
        if line.startswith("#"):
            entries.append(
                IndexEntry(kind="section", label=line.lstrip("#").strip(), anchor_id=page.anchor_id)
            )
    return entries
