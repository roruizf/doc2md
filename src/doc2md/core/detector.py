from pathlib import Path

import magic

SUPPORTED_FORMATS = {"pdf", "docx", "odt", "epub", "html", "txt", "image"}

EXTENSION_FORMATS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".odt": "odt",
    ".epub": "epub",
    ".html": "html",
    ".htm": "html",
    ".txt": "txt",
    ".text": "txt",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tif": "image",
    ".tiff": "image",
    ".bmp": "image",
    ".webp": "image",
}


def detect_format(path: Path) -> str:
    extension = path.suffix.lower()
    if extension in EXTENSION_FORMATS:
        return EXTENSION_FORMATS[extension]
    if extension:
        return "unsupported"

    mime = magic.from_file(str(path), mime=True)
    if mime == "application/pdf":
        return "pdf"
    if mime in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/zip",
    }:
        return "docx"
    if mime == "application/vnd.oasis.opendocument.text":
        return "odt"
    if mime == "application/epub+zip":
        return "epub"
    if mime in {"text/html", "application/xhtml+xml"}:
        return "html"
    if mime.startswith("text/"):
        return "txt"
    if mime.startswith("image/"):
        return "image"
    return "unsupported"

