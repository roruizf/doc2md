import logging
import sys
from dataclasses import dataclass

import httpx

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelPricing:
    prompt: float
    image: float


def fetch_model_pricing(model_id: str) -> ModelPricing:
    response = httpx.get("https://openrouter.ai/api/v1/models", timeout=10)
    response.raise_for_status()
    for model in response.json().get("data", []):
        if model.get("id") == model_id:
            pricing = model.get("pricing", {})
            return ModelPricing(
                prompt=float(pricing.get("prompt", 0.0)),
                image=float(pricing.get("image", 0.0)),
            )
    raise ValueError(
        f"Model pricing not found for model {model_id}. "
        "Next step: choose a model listed by OpenRouter or pass --vlm-model explicitly."
    )


def estimate_cost(num_images: int, pricing: ModelPricing) -> float:
    return num_images * (pricing.image + pricing.prompt)


def confirm_cost(estimated_cost: float, threshold: float) -> bool:
    if estimated_cost <= threshold:
        return True
    if not sys.stdin.isatty():
        LOGGER.error(
            "Estimated VLM cost $%.2f exceeds threshold $%.2f before processing image paths; "
            "Next step: increase --vlm-cost-threshold, run interactively, "
            "or use --images placeholder.",
            estimated_cost,
            threshold,
        )
        return False

    answer = input(
        f"Estimated VLM cost is ${estimated_cost:.2f}, above ${threshold:.2f}. Continue? [y/N] "
    )
    return answer.strip().lower() in {"y", "yes"}
