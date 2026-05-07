import logging

THIRD_PARTY_LOGGERS = ("docling", "httpx", "urllib3")


def setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s", force=True)
    third_party_level = logging.DEBUG if verbose else logging.WARNING
    for logger_name in THIRD_PARTY_LOGGERS:
        logging.getLogger(logger_name).setLevel(third_party_level)
