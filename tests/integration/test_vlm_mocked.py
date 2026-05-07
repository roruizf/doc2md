import hashlib
from pathlib import Path

import pytest

from doc2md.config import Settings
from doc2md.core import pipeline
from doc2md.images.vlm_pricing import ModelPricing
from tests.conftest import FIXTURES


class StatusError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__(str(status_code))
        self.status_code = status_code


class FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.choices = [FakeChoice(content)]


class FakeCompletions:
    def __init__(self, outcomes: list[object]) -> None:
        self.outcomes = outcomes
        self.calls = 0

    def create(self, **_kwargs: object) -> FakeResponse:
        outcome = self.outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        return FakeResponse(str(outcome))


class FakeOpenAIClient:
    def __init__(self, completions: FakeCompletions) -> None:
        self.chat = type("Chat", (), {"completions": completions})()


def _settings() -> Settings:
    return Settings(images_strategy="vlm", vlm_model="test/model", vlm_cost_threshold=1.0)


def _allow_pricing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pipeline,
        "fetch_model_pricing",
        lambda _model: ModelPricing(prompt=0.0, image=0.0),
    )


def _run_html(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, completions: FakeCompletions) -> str:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("DOC2MD_VLM_CACHE_DIR", str(tmp_path / "cache"))
    _allow_pricing(monkeypatch)

    import doc2md.images.vlm_client as vlm_client

    monkeypatch.setattr(
        vlm_client.openai,
        "OpenAI",
        lambda **_kwargs: FakeOpenAIClient(completions),
    )
    output = tmp_path / "out.md"
    pipeline.run(FIXTURES / "sample.html", output, _settings())
    return output.read_text(encoding="utf-8")


def test_vlm_mocked_openai_response_is_rendered(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    markdown = _run_html(tmp_path, monkeypatch, FakeCompletions(["A red square image."]))

    assert "A red square image." in markdown


def test_vlm_retries_429_then_succeeds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    completions = FakeCompletions([StatusError(429), StatusError(429), "Recovered alt text."])

    markdown = _run_html(tmp_path, monkeypatch, completions)

    assert "Recovered alt text." in markdown
    assert completions.calls == 3


def test_vlm_terminal_500_falls_back_to_placeholder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    completions = FakeCompletions([StatusError(500), StatusError(500), StatusError(500)])

    markdown = _run_html(tmp_path, monkeypatch, completions)

    assert "Page 1 image" in markdown
    assert "VLM description failed" in caplog.text


def test_vlm_cache_hit_skips_api_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    image_bytes = (FIXTURES / "sample_image.png").read_bytes()
    digest = hashlib.sha256(image_bytes).hexdigest()
    (cache_dir / f"{digest}.txt").write_text("Cached alt text.", encoding="utf-8")
    completions = FakeCompletions(["Should not be called"])

    markdown = _run_html(tmp_path, monkeypatch, completions)

    assert "Cached alt text." in markdown
    assert completions.calls == 0


def test_vlm_cost_over_threshold_noninteractive_uses_placeholder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("DOC2MD_VLM_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr(
        pipeline,
        "fetch_model_pricing",
        lambda _model: ModelPricing(prompt=0.0, image=2.0),
    )
    completions = FakeCompletions(["Should not be called"])

    import doc2md.images.vlm_client as vlm_client

    monkeypatch.setattr(
        vlm_client.openai,
        "OpenAI",
        lambda **_kwargs: FakeOpenAIClient(completions),
    )
    output = tmp_path / "out.md"

    pipeline.run(FIXTURES / "sample.html", output, _settings())

    assert "Page 1 image" in output.read_text(encoding="utf-8")
    assert completions.calls == 0
    assert "exceeds threshold" in caplog.text
