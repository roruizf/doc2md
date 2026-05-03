from pathlib import Path

import pytest

from doc2md.rendering.images_strategy import ImageMeta, apply_strategy


def image_meta() -> ImageMeta:
    return ImageMeta(
        figure_number=1,
        description="Projected revenue growth chart",
        output_path=Path("images/fig1_page3.png"),
        page_number=3,
    )


def test_placeholder_format() -> None:
    assert apply_strategy("placeholder", image_meta()) == (
        "![Figure 1 - Projected revenue growth chart](images/fig1_page3.png)"
    )


def test_omit_format() -> None:
    assert apply_strategy("omit", image_meta()) == "[IMAGE OMITTED: Figure 1]"


def test_vlm_raises_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        apply_strategy("vlm", image_meta())

