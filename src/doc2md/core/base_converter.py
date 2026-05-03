from abc import ABC, abstractmethod
from pathlib import Path

from doc2md.config import Settings
from doc2md.core.document import MarkdownDocument


class BaseConverter(ABC):
    settings: Settings

    @abstractmethod
    def convert(self, input_path: Path) -> MarkdownDocument:
        raise NotImplementedError
