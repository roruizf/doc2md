from collections.abc import Iterator
from pathlib import Path

from doc2md.core.detector import EXTENSION_FORMATS, SUPPORTED_FORMATS, detect_format


def iter_input_files(path: Path, recursive: bool) -> Iterator[Path]:
    if path.is_file():
        if _is_supported_file(path):
            yield path
        return

    paths = path.rglob("*") if recursive else path.iterdir()
    for candidate in sorted(paths):
        if _should_skip(candidate, path):
            continue
        if candidate.is_file() and _is_supported_file(candidate):
            yield candidate


def mirror_output_path(
    input_root: Path,
    input_file: Path,
    output_root: Path,
    flatten: bool,
) -> Path:
    if input_root.is_file():
        return output_root

    relative_path = input_file.relative_to(input_root)
    if not flatten:
        return (output_root / relative_path).with_suffix(".md")

    parent_slug = _slug(relative_path.parent.as_posix())
    filename = (
        f"{input_file.stem}.md"
        if not parent_slug
        else f"{input_file.stem}__{parent_slug}.md"
    )
    return output_root / filename


def _is_supported_file(path: Path) -> bool:
    if path.name.startswith("."):
        return False
    if path.suffix.lower() in EXTENSION_FORMATS:
        return True
    return detect_format(path) in SUPPORTED_FORMATS


def _should_skip(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    return any(part.startswith(".") or part == "images" for part in relative_parts)


def _slug(value: str) -> str:
    if value in {"", "."}:
        return ""
    return (
        value.replace("/", "__")
        .replace("\\", "__")
        .replace(" ", "_")
        .replace(".", "_")
    )
