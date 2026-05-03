class Doc2MdError(Exception):
    """Base exception for doc2md failures."""


class UnsupportedFormat(Doc2MdError):
    """Raised when no converter is available for a detected format."""


class LockedDocument(Doc2MdError):
    """Raised when a document is encrypted or password protected."""


class ConversionFailed(Doc2MdError):
    """Raised when document conversion fails."""

