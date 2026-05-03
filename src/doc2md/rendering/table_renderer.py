def render_table(headers: list[str], rows: list[list[str]]) -> str:
    if not headers:
        return ""

    table_rows = [headers, *rows]
    if _is_complex_table(table_rows):
        raw = "\n".join(" | ".join(row) for row in table_rows)
        return f"> Note: complex table preserved as raw text\n\n```\n{raw}\n```"

    escaped_headers = [_escape_cell(cell) for cell in headers]
    lines = [
        "| " + " | ".join(escaped_headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        normalized_row = _normalize_row(row, len(headers))
        lines.append("| " + " | ".join(_escape_cell(cell) for cell in normalized_row) + " |")
    return "\n".join(lines)


def _is_complex_table(rows: list[list[str]]) -> bool:
    return any(_is_complex_cell(cell) for row in rows for cell in row)


def _is_complex_cell(cell: str) -> bool:
    lowered = cell.lower()
    return "\n" in cell or "rowspan" in lowered or "colspan" in lowered or "[merged]" in lowered


def _escape_cell(cell: str) -> str:
    return cell.replace("|", r"\|").strip()


def _normalize_row(row: list[str], width: int) -> list[str]:
    if len(row) >= width:
        return row[:width]
    return [*row, *([""] * (width - len(row)))]

