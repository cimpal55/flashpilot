"""Bounded workload profiles for CI and the eventual product demo."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkloadProfile:
    name: str
    global_seed: int
    steps: int
    batch_size: int
    sequence_length: int
    vocabulary_size: int
    model_width: int
    attention_heads: int
    transformer_layers: int
    adapter_width: int
    dropout: float
    learning_rate: float

    def __post_init__(self) -> None:
        if self.steps <= 0 or self.batch_size <= 0 or self.sequence_length <= 0:
            raise ValueError("steps, batch_size, and sequence_length must be positive")
        if self.model_width % self.attention_heads != 0:
            raise ValueError("model_width must be divisible by attention_heads")
        if not 0.0 < self.dropout < 1.0:
            raise ValueError("dropout must be nonzero and less than one")
        if self.learning_rate <= 0.0:
            raise ValueError("learning_rate must be positive")


CI_PROFILE = WorkloadProfile(
    name="ci",
    global_seed=20_260_716,
    steps=8,
    batch_size=4,
    sequence_length=8,
    vocabulary_size=32,
    model_width=16,
    attention_heads=2,
    transformer_layers=1,
    adapter_width=4,
    dropout=0.2,
    learning_rate=0.01,
)

DEMO_PROFILE = WorkloadProfile(
    name="demo",
    global_seed=20_260_716,
    steps=24,
    batch_size=8,
    sequence_length=12,
    vocabulary_size=64,
    model_width=32,
    attention_heads=4,
    transformer_layers=2,
    adapter_width=8,
    dropout=0.2,
    learning_rate=0.005,
)

_PROFILES = {profile.name: profile for profile in (CI_PROFILE, DEMO_PROFILE)}


def get_profile(name: str) -> WorkloadProfile:
    """Return a known, immutable workload profile."""

    try:
        return _PROFILES[name]
    except KeyError as error:
        supported = ", ".join(sorted(_PROFILES))
        raise ValueError(f"unknown profile {name!r}; expected one of: {supported}") from error
