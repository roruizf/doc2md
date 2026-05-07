from pathlib import Path

from doc2md.config import Settings
from doc2md.images.vlm_client import VlmError
from doc2md.rendering import images_strategy
from doc2md.rendering.images_strategy import ImageMeta, apply_strategy


def image_meta() -> ImageMeta:
    return ImageMeta(
        figure_number=1,
        description="Projected revenue growth chart",
        output_path=Path("images/fig1_page3.png"),
        page_number=3,
        image_path=Path("/tmp/fig1_page3.png"),
    )


def test_placeholder_format() -> None:
    assert apply_strategy("placeholder", image_meta()) == (
        "![Figure 1 - Projected revenue growth chart](images/fig1_page3.png)"
    )


def test_omit_format() -> None:
    assert apply_strategy("omit", image_meta()) == "[IMAGE OMITTED: Figure 1]"


def test_vlm_strategy_invokes_vlm_client(monkeypatch) -> None:
    class FakeVlmClient:
        def __init__(self, provider: str, model: str) -> None:
            self.provider = provider
            self.model = model

        def describe_image(self, image_path: Path) -> str:
            assert image_path == Path("/tmp/fig1_page3.png")
            return "Projected revenue chart trending upward."

    monkeypatch.setattr(images_strategy, "VlmClient", FakeVlmClient)

    assert apply_strategy("vlm", image_meta(), Settings(images_strategy="vlm")) == (
        "![Figure 1 - Projected revenue chart trending upward.](images/fig1_page3.png)"
    )


def test_vlm_strategy_falls_back_to_placeholder_on_error(monkeypatch) -> None:
    class FailingVlmClient:
        def __init__(self, provider: str, model: str) -> None:
            pass

        def describe_image(self, image_path: Path) -> str:
            raise VlmError("boom")

    monkeypatch.setattr(images_strategy, "VlmClient", FailingVlmClient)

    assert apply_strategy("vlm", image_meta(), Settings(images_strategy="vlm")) == (
        "![Figure 1 - Projected revenue growth chart](images/fig1_page3.png)"
    )
