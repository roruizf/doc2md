from dataclasses import dataclass
from pathlib import Path
from tempfile import mkdtemp
from typing import Literal

from doc2md.config import Settings
from doc2md.core import pipeline

__version__ = "0.1.0"


@dataclass(frozen=True)
class ConvertResult:
    input_path: Path
    output_path: Path
    markdown: str


def convert(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    images_strategy: Literal["placeholder", "omit", "vlm"] = "placeholder",
    ocr_lang: str | None = None,
    ocr_engine: Literal["docling", "direct"] = "docling",
    password: str | None = None,
    vlm_provider: Literal["openrouter", "openai", "anthropic"] = "openrouter",
    vlm_model: str | None = None,
    vlm_cost_threshold: float = 1.0,
) -> ConvertResult:
    source = Path(input_path)
    target = Path(output_path) if output_path is not None else _temporary_output_path(source)
    settings = Settings(
        images_strategy=images_strategy,
        ocr_lang=ocr_lang,
        ocr_engine=ocr_engine,
        password=password,
        vlm_provider=vlm_provider,
        vlm_model=vlm_model,
        vlm_cost_threshold=vlm_cost_threshold,
    )
    pipeline.run(source, target, settings)
    return ConvertResult(
        input_path=source,
        output_path=target,
        markdown=target.read_text(encoding="utf-8"),
    )


def _temporary_output_path(input_path: Path) -> Path:
    return Path(mkdtemp(prefix="doc2md-")) / f"{input_path.stem}.md"


__all__ = ["ConvertResult", "__version__", "convert"]
