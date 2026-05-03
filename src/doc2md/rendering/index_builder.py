from collections.abc import Iterable

from doc2md.core.document import IndexEntry, MarkdownDocument

SECTION_TITLES = {
    "page": "Pages",
    "section": "Sections",
    "table": "Tables",
    "figure": "Figures",
}


def build_index(doc: MarkdownDocument) -> str:
    sections: list[str] = []
    for kind in ("page", "section", "table", "figure"):
        entries = [entry for entry in doc.index_entries if entry.kind == kind]
        if entries:
            sections.append(_render_section(SECTION_TITLES[kind], entries))

    if not sections:
        return ""
    return "## Document Index\n\n" + "\n\n".join(sections)


def _render_section(title: str, entries: Iterable[IndexEntry]) -> str:
    lines = [f"### {title}"]
    for entry in entries:
        lines.append(f"- [{entry.label}](#{entry.anchor_id})")
    return "\n".join(lines)

