import pytest

from doc2md.images import vlm_pricing
from doc2md.images.vlm_pricing import ModelPricing, estimate_cost, fetch_model_pricing


def test_fetch_model_pricing_parses_openrouter_response(monkeypatch) -> None:
    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict[str, object]:
            return {
                "data": [
                    {"id": "other", "pricing": {"prompt": "0.1", "image": "0.2"}},
                    {"id": "target", "pricing": {"prompt": "0.01", "image": "0.03"}},
                ]
            }

    monkeypatch.setattr(vlm_pricing.httpx, "get", lambda *_args, **_kwargs: FakeResponse())

    pricing = fetch_model_pricing("target")

    assert pricing == ModelPricing(prompt=0.01, image=0.03)


def test_estimate_cost_multiplies_per_image_cost() -> None:
    assert estimate_cost(3, ModelPricing(prompt=0.01, image=0.04)) == pytest.approx(0.15)
