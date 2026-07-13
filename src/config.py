import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

DEFAULT_N_QUESTIONS = 5

# Number of (question, answer) pairs bundled into a single judge call.
EVALUATION_BATCH_SIZE = 5

DEFAULT_MODEL = "gpt-4.1-2025-04-14"


@dataclass(frozen=True)
class ModelConfig:
    """Model name + sampling params for a single ChatLiteLLM instance."""

    model: str
    temperature: float | None = None
    top_p: float | None = None

    @classmethod
    def from_env(
        cls,
        prefix: str,
        *,
        default_model: str = DEFAULT_MODEL,
        default_temperature: float | None = None,
        default_top_p: float | None = None,
    ) -> "ModelConfig":
        """Build a config from `{prefix}_MODEL` / `_TEMPERATURE` / `_TOP_P` env vars."""
        temperature_raw = os.getenv(f"{prefix}_TEMPERATURE")
        top_p_raw = os.getenv(f"{prefix}_TOP_P")
        return cls(
            model=os.getenv(f"{prefix}_MODEL", default_model),
            temperature=float(temperature_raw) if temperature_raw else default_temperature,
            top_p=float(top_p_raw) if top_p_raw else default_top_p,
        )

    def to_kwargs(self) -> dict[str, str | float]:
        """Expand to the kwargs ChatLiteLLM expects, omitting unset sampling params."""
        kwargs: dict[str, str | float] = {"model": self.model}
        if self.temperature is not None:
            kwargs["temperature"] = self.temperature
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        return kwargs


SETTING_SELECTION_CONFIG = ModelConfig.from_env("SETTING_SELECTION")
QUESTION_GENERATION_CONFIG = ModelConfig.from_env("QUESTION_GENERATION")
RESPONSE_GENERATION_CONFIG = ModelConfig.from_env("RESPONSE_GENERATION")
RESPONSE_EVALUATION_EXAMPLE_CONFIG = ModelConfig.from_env("RESPONSE_EVALUATION_EXAMPLE")

# Judge calls are deterministic by default: temperature/top_p pinned to 0.
_judge_models_env = os.getenv("RESPONSE_EVALUATION_JUDGE_MODELS")
_JUDGE_MODEL_NAMES: list[str] = (
    [name.strip() for name in _judge_models_env.split(",") if name.strip()]
    if _judge_models_env
    else ["gpt-4.1-2025-04-14", "gpt-4o-2024-08-06"]
)
_JUDGE_TEMPERATURE = float(os.getenv("RESPONSE_EVALUATION_JUDGE_TEMPERATURE", "0"))
_JUDGE_TOP_P = float(os.getenv("RESPONSE_EVALUATION_JUDGE_TOP_P", "0"))

RESPONSE_EVALUATION_JUDGE_CONFIGS: list[ModelConfig] = [
    ModelConfig(model=name, temperature=_JUDGE_TEMPERATURE, top_p=_JUDGE_TOP_P)
    for name in _JUDGE_MODEL_NAMES
]
