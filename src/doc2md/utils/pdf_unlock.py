import shutil
import subprocess
import tempfile
from pathlib import Path

import fitz

from doc2md.core.exceptions import LockedDocument


def is_encrypted(path: Path) -> bool:
    with fitz.open(path) as doc:
        return bool(doc.is_encrypted)


def try_decrypt(path: Path, password: str | None) -> Path:
    if not is_encrypted(path):
        return path

    if password:
        decrypted_path = _temp_pdf_path()
        with fitz.open(path) as doc:
            if doc.authenticate(password):
                doc.save(decrypted_path)
                return decrypted_path
        decrypted_path.unlink(missing_ok=True)

    decrypted_path = _temp_pdf_path()
    result = subprocess.run(
        ["qpdf", "--decrypt", "--password=", str(path), str(decrypted_path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return decrypted_path

    decrypted_path.unlink(missing_ok=True)
    raise LockedDocument(
        f"Cannot decrypt {path}: provide --password or document is DRM-protected"
    )


def cleanup_temp_pdf(path: Path) -> None:
    parent = path.parent
    path.unlink(missing_ok=True)
    if parent.name.startswith("doc2md-unlocked-"):
        shutil.rmtree(parent, ignore_errors=True)


def _temp_pdf_path() -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="doc2md-unlocked-"))
    return temp_dir / "decrypted.pdf"

