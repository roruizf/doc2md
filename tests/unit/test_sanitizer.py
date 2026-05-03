from doc2md.rendering.sanitizer import sanitize


def test_dash_normalization_outside_code() -> None:
    sanitized, counts = sanitize("A — B – C")

    assert sanitized == "A -- B - C"
    assert counts == {"—": 1, "–": 1}


def test_dashes_preserved_inside_backticks() -> None:
    sanitized, counts = sanitize("A `— –` B —")

    assert sanitized == "A `— –` B --"
    assert counts == {"—": 1}


def test_latex_preserved_inside_backticks() -> None:
    sanitized, counts = sanitize("Equation `$x — y$` and text —")

    assert sanitized == "Equation `$x — y$` and text --"
    assert counts == {"—": 1}


def test_smart_quote_replacement() -> None:
    sanitized, counts = sanitize("“Hello” ‘there’")

    assert sanitized == "\"Hello\" 'there'"
    assert counts == {"“": 1, "”": 1, "‘": 1, "’": 1}


def test_mixed_content_and_counts() -> None:
    sanitized, counts = sanitize("“A — B” ```–```")

    assert sanitized == '"A -- B" ```–```'
    assert counts == {"—": 1, "“": 1, "”": 1}

