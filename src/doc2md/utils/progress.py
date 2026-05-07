import os
from collections.abc import Iterable, Iterator
from typing import TypeVar

from tqdm import tqdm

T = TypeVar("T")


class ProgressBar:
    def __init__(self, disabled: bool = False) -> None:
        self.disabled = disabled or os.environ.get("DOC2MD_NO_PROGRESS") == "1"

    def wrap(
        self,
        items: Iterable[T],
        total: int | None = None,
        description: str = "",
    ) -> Iterator[T]:
        yield from tqdm(items, total=total, desc=description, disable=self.disabled)
