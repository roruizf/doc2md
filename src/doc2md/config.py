from typing import Literal

from pydantic import BaseModel


class Settings(BaseModel):
    images_strategy: Literal["placeholder", "vlm", "omit"] = "placeholder"
    converter_version: str = "0.1.0"
    ocr_lang: str | None = None
    ocr_engine: Literal["docling", "direct"] = "docling"
