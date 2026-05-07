from pathlib import Path

from doc2md.utils.fs import iter_input_files, mirror_output_path


def test_iter_input_files_skips_hidden_files_and_images_directory(tmp_path: Path) -> None:
    (tmp_path / "visible.txt").write_text("hello", encoding="utf-8")
    (tmp_path / ".hidden.txt").write_text("secret", encoding="utf-8")
    image_dir = tmp_path / "images"
    image_dir.mkdir()
    (image_dir / "skip.png").write_bytes(b"png")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "child.txt").write_text("child", encoding="utf-8")

    non_recursive = list(iter_input_files(tmp_path, recursive=False))
    recursive = list(iter_input_files(tmp_path, recursive=True))

    assert non_recursive == [tmp_path / "visible.txt"]
    assert tmp_path / "nested" / "child.txt" in recursive
    assert tmp_path / ".hidden.txt" not in recursive
    assert image_dir / "skip.png" not in recursive


def test_mirror_output_path_preserves_relative_tree(tmp_path: Path) -> None:
    input_root = tmp_path / "input"
    input_file = input_root / "nested" / "sample.html"
    output_root = tmp_path / "output"

    output_path = mirror_output_path(input_root, input_file, output_root, flatten=False)

    assert output_path == output_root / "nested" / "sample.md"


def test_mirror_output_path_flatten_disambiguates_same_name_files(tmp_path: Path) -> None:
    input_root = tmp_path / "input"
    output_root = tmp_path / "output"
    first = mirror_output_path(input_root, input_root / "a" / "sample.txt", output_root, True)
    second = mirror_output_path(input_root, input_root / "b" / "sample.txt", output_root, True)

    assert first == output_root / "sample__a.md"
    assert second == output_root / "sample__b.md"
    assert first != second
