import logging
from pathlib import Path

import yaml

from doc2md.config import Settings
from doc2md.core.detector import detect_format
from doc2md.core.dispatcher import get_converter
from doc2md.core.document import Frontmatter, MarkdownDocument
from doc2md.core.validator import validate

LOGGER = logging.getLogger(__name__)


class _QuotedString(str):
    pass


class _FrontmatterDumper(yaml.SafeDumper):
    pass


def _quoted_string_representer(dumper: yaml.Dumper, data: _QuotedString) -> yaml.Node:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


_FrontmatterDumper.add_representer(_QuotedString, _quoted_string_representer)


def run(input_path: Path, output_path: Path, settings: Settings) -> None:
    detected_format = detect_format(input_path)
    converter = get_converter(detected_format)
    converter.settings = settings

    doc = converter.convert(input_path)
    result = validate(doc)
    for warning in result.warnings:
        LOGGER.warning(warning)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_document(doc), encoding="utf-8")


def _render_document(doc: MarkdownDocument) -> str:
    frontmatter_yaml = _frontmatter_yaml(doc.frontmatter)
    pages = "".join(
        f'<a id="{page.anchor_id}"></a>\n**[Page {page.number}]**\n\n{page.content}\n\n'
        for page in doc.pages
    )
    return f"---\n{frontmatter_yaml}---\n\n{pages}"


def _frontmatter_yaml(frontmatter: Frontmatter) -> str:
    data = frontmatter.model_dump()
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = _QuotedString(value)
    return yaml.dump(data, Dumper=_FrontmatterDumper, sort_keys=False)

