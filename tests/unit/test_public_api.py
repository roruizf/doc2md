from pathlib import Path

from doc2md import ConvertResult, convert


def test_convert_returns_markdown_result(tmp_path: Path) -> None:
    output_path = tmp_path / "sample.md"

    result = convert(
        Path("tests/fixtures/sample.txt"),
        output_path=output_path,
        images_strategy="placeholder",
    )

    assert isinstance(result, ConvertResult)
    assert result.input_path == Path("tests/fixtures/sample.txt")
    assert result.output_path == output_path
    assert result.markdown.startswith("---")
    assert output_path.read_text(encoding="utf-8") == result.markdown
