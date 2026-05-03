from doc2md.rendering.table_renderer import render_table


def test_simple_gfm_table() -> None:
    table = render_table(["Quarter", "Revenue"], [["Q1", "12.4"], ["Q2", "14.1"]])

    assert table == (
        "| Quarter | Revenue |\n"
        "| --- | --- |\n"
        "| Q1 | 12.4 |\n"
        "| Q2 | 14.1 |"
    )


def test_table_with_pipes_in_cells_escapes_pipe() -> None:
    table = render_table(["Name"], [["A | B"]])

    assert r"A \| B" in table


def test_table_with_newlines_falls_back_to_code_block() -> None:
    table = render_table(["Name"], [["A\nB"]])

    assert "> Note: complex table preserved as raw text" in table
    assert "```" in table


def test_empty_table_returns_empty_string() -> None:
    assert render_table([], []) == ""


def test_single_column_table() -> None:
    table = render_table(["Only"], [["One"], ["Two"]])

    assert table == "| Only |\n| --- |\n| One |\n| Two |"

