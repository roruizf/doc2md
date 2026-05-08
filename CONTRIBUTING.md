# Contributing to doc2md

Thanks for helping improve doc2md. The project is CLI-first, test-driven, and
keeps converter behavior behind a shared Markdown schema.

## Development Setup

Clone the repository and install system dependencies:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng qpdf pandoc libmagic1 poppler-utils
```

Create a virtual environment and install dev dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

Optional Anthropic provider support:

```bash
python -m pip install -e ".[dev,anthropic]"
```

Verify the CLI:

```bash
doc2md --version
```

## Running Tests

Full local quality gate:

```bash
ruff check src/ tests/
mypy src/doc2md
pytest tests/
pytest --cov=src/doc2md --cov-report=term-missing
```

Focused test examples:

```bash
pytest tests/converters/test_html.py
pytest tests/integration/test_full_pipeline.py
```

PDF and Docling tests can be slower than lightweight converter tests because
they may trigger model loading and layout analysis.

## Code Style

- Use ruff for linting and import sorting.
- Use mypy for type checking.
- Keep public APIs typed.
- Prefer existing converter, renderer, and settings patterns.
- Add concise comments only where the code is not self-explanatory.

## Adding a New Converter

1. Add a converter module under `src/doc2md/converters/`.
2. Subclass or follow the `BaseConverter` interface.
3. Populate a `MarkdownDocument` with:
   - `Frontmatter`
   - `Page` entries with stable `anchor_id` values
   - `IndexEntry` entries when sections, tables, pages, or figures are known
4. Add format detection in `core/detector.py` if needed.
5. Route the format in `core/dispatcher.py`.
6. Let the shared pipeline handle rendering, image strategy application, and
   validation.
7. Add fixtures and tests under `tests/converters/` and `tests/integration/`.
8. Update README and relevant docs.

## Pull Request Process

1. Keep PRs focused on one behavior or documentation area.
2. Include tests for behavior changes.
3. Run ruff, mypy, and relevant pytest suites before opening the PR.
4. Document user-facing changes in `CHANGELOG.md`.
5. Explain any known limitations, slow tests, or skipped checks in the PR body.

## Reporting Bugs

Include:

- doc2md version
- Python version and OS
- command run
- input format
- traceback or error output
- whether system tools such as Tesseract, qpdf, pandoc, and libmagic are
  installed
