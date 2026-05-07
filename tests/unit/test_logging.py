import logging

from doc2md.logging_setup import setup_logging


def test_setup_logging_suppresses_third_party_debug_by_default() -> None:
    setup_logging(verbose=False)

    assert logging.getLogger().level == logging.INFO
    assert logging.getLogger("docling").level == logging.WARNING
    assert logging.getLogger("httpx").level == logging.WARNING
    assert logging.getLogger("urllib3").level == logging.WARNING


def test_setup_logging_verbose_enables_debug() -> None:
    setup_logging(verbose=True)

    assert logging.getLogger().level == logging.DEBUG
    assert logging.getLogger("docling").level == logging.DEBUG
    assert logging.getLogger("httpx").level == logging.DEBUG
    assert logging.getLogger("urllib3").level == logging.DEBUG
