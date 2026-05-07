from pathlib import Path

from typer.testing import CliRunner

from doc2md.cli import app
from doc2md.core import pipeline
from tests.conftest import FIXTURES


def test_cli_batch_non_recursive_converts_supported_top_level_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls: list[tuple[Path, Path]] = []

    def fake_run(input_path: Path, output_path: Path, _settings: object) -> None:
        calls.append((input_path, output_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(f"# {input_path.name}\n", encoding="utf-8")

    monkeypatch.setattr(pipeline, "run", fake_run)
    output_root = tmp_path / "out"

    result = CliRunner().invoke(
        app,
        [str(FIXTURES), "-o", str(output_root), "--no-progress"],
    )

    assert result.exit_code == 0, result.output
    assert "11 succeeded, 0 failed" in result.output
    assert len(calls) == 11
    assert (output_root / "sample.md").exists()
    assert (output_root / "sample_digital.md").exists()


def test_cli_batch_recursive_converts_nested_files(tmp_path: Path, monkeypatch) -> None:
    input_root = tmp_path / "input"
    nested = input_root / "nested"
    nested.mkdir(parents=True)
    (input_root / "top.txt").write_text("top", encoding="utf-8")
    (nested / "child.txt").write_text("child", encoding="utf-8")
    calls: list[Path] = []

    def fake_run(input_path: Path, output_path: Path, _settings: object) -> None:
        calls.append(input_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("ok", encoding="utf-8")

    monkeypatch.setattr(pipeline, "run", fake_run)
    output_root = tmp_path / "out"

    result = CliRunner().invoke(
        app,
        [str(input_root), "-o", str(output_root), "--recursive", "--no-progress"],
    )

    assert result.exit_code == 0, result.output
    assert input_root / "top.txt" in calls
    assert nested / "child.txt" in calls
    assert (output_root / "nested" / "child.md").exists()


def test_cli_batch_flatten_outputs_to_one_directory_without_name_collisions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    input_root = tmp_path / "input"
    (input_root / "a").mkdir(parents=True)
    (input_root / "b").mkdir(parents=True)
    (input_root / "a" / "sample.txt").write_text("a", encoding="utf-8")
    (input_root / "b" / "sample.txt").write_text("b", encoding="utf-8")

    def fake_run(_input_path: Path, output_path: Path, _settings: object) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("ok", encoding="utf-8")

    monkeypatch.setattr(pipeline, "run", fake_run)
    output_root = tmp_path / "out"

    result = CliRunner().invoke(
        app,
        [str(input_root), "-o", str(output_root), "--recursive", "--flatten", "--no-progress"],
    )

    assert result.exit_code == 0, result.output
    assert (output_root / "sample__a.md").exists()
    assert (output_root / "sample__b.md").exists()


def test_cli_batch_isolates_failed_file_and_exits_zero(tmp_path: Path, monkeypatch) -> None:
    input_root = tmp_path / "input"
    input_root.mkdir()
    (input_root / "good.txt").write_text("good", encoding="utf-8")
    (input_root / "bad.pdf").write_bytes(b"not a pdf")

    def fake_run(input_path: Path, output_path: Path, _settings: object) -> None:
        if input_path.name == "bad.pdf":
            raise RuntimeError("corrupt pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("ok", encoding="utf-8")

    monkeypatch.setattr(pipeline, "run", fake_run)
    output_root = tmp_path / "out"

    result = CliRunner().invoke(
        app,
        [str(input_root), "-o", str(output_root), "--no-progress"],
    )

    assert result.exit_code == 0, result.output
    assert "1 succeeded, 1 failed" in result.output
    assert "bad.pdf" in result.output
    assert (output_root / "good.md").exists()
