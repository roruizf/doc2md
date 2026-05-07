import base64
import hashlib
import os
from pathlib import Path
from typing import Any

import openai
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

PROMPT = (
    "Describe this image as concise alt-text (one sentence). "
    "If it contains a chart or table, summarize the data shown."
)


class VlmError(Exception):
    pass


def _is_retryable_error(exc: BaseException) -> bool:
    status_code = getattr(exc, "status_code", None)
    return status_code == 429 or (isinstance(status_code, int) and status_code >= 500)


class VlmClient:
    def __init__(self, provider: str, model: str, api_key: str | None = None) -> None:
        self.provider = provider
        self.model = model
        self.api_key = api_key or _api_key(provider)
        self._client: Any | None = None

    def describe_image(self, image_path: Path) -> str:
        image_bytes = image_path.read_bytes()
        cache_path = _cache_path(image_bytes)
        if cache_path.exists():
            return cache_path.read_text(encoding="utf-8")

        try:
            description = self._describe_image_uncached(image_bytes, image_path)
        except Exception as exc:
            raise VlmError(
                f"VLM image description failed for {image_path}: {exc}. "
                "Next step: check API credentials, provider, model, or retry later."
            ) from exc

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(description, encoding="utf-8")
        return description

    @retry(
        retry=retry_if_exception(_is_retryable_error),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    def _describe_image_uncached(self, image_bytes: bytes, image_path: Path) -> str:
        if self.provider == "anthropic":
            return self._describe_with_anthropic(image_bytes, image_path)

        client = self._openai_client()
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": _data_url(image_bytes, image_path)},
                        },
                    ],
                }
            ],
            timeout=30,
        )
        return _response_text(response)

    def _openai_client(self) -> Any:
        if self._client is not None:
            return self._client
        base_url = (
            "https://openrouter.ai/api/v1"
            if self.provider == "openrouter"
            else None
        )
        self._client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
        return self._client

    def _describe_with_anthropic(self, image_bytes: bytes, image_path: Path) -> str:
        try:
            import anthropic
        except ImportError as exc:
            raise VlmError(
                f"Anthropic provider requested for {image_path}, but the SDK is missing. "
                "Next step: install doc2md[anthropic]."
            ) from exc

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=256,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": _media_type(image_path),
                                "data": base64.b64encode(image_bytes).decode("ascii"),
                            },
                        },
                    ],
                }
            ],
        )
        return str(response.content[0].text).strip()


def _api_key(provider: str) -> str:
    env_var = {
        "openrouter": "OPENROUTER_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
    }[provider]
    value = os.environ.get(env_var)
    if not value:
        raise VlmError(
            f"{env_var} is required for VLM image descriptions. "
            f"Next step: export {env_var}=<token> or use a different --vlm-provider."
        )
    return value


def _cache_path(image_bytes: bytes) -> Path:
    digest = hashlib.sha256(image_bytes).hexdigest()
    cache_root = Path(
        os.environ.get("DOC2MD_VLM_CACHE_DIR", "~/.cache/doc2md/vlm")
    ).expanduser()
    return cache_root / f"{digest}.txt"


def _data_url(image_bytes: bytes, image_path: Path) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{_media_type(image_path)};base64,{encoded}"


def _media_type(image_path: Path) -> str:
    ext = image_path.suffix.lower().lstrip(".")
    if ext in {"jpg", "jpeg"}:
        return "image/jpeg"
    if ext == "webp":
        return "image/webp"
    return "image/png"


def _response_text(response: Any) -> str:
    message = response.choices[0].message
    content = getattr(message, "content", "")
    return str(content).strip()
