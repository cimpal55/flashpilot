"""Tiny offline CPU Trainer workload used by the documented HF adapter."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as functional
from torch.utils.data import Dataset
from transformers import PreTrainedConfig, PreTrainedModel, Trainer, TrainingArguments
from transformers import __version__ as transformers_version
from transformers.modeling_outputs import SequenceClassifierOutput
from transformers.trainer_callback import TrainerCallback
from transformers.trainer_utils import enable_full_determinism

from flashpilot.hf.models import HFRunSummary, HFScenario
from flashpilot.workload.state import state_digest

HF_VOCABULARY_SIZE = 41
HF_SEQUENCE_LENGTH = 8
HF_MODEL_WIDTH = 16
HF_LABEL_COUNT = 5
HF_BATCH_SIZE = 4
HF_TOTAL_STEPS = 8
HF_CHECKPOINT_STEP = 4
HF_SEED = 20260720


class FlashPilotHFConfig(PreTrainedConfig):
    model_type = "flashpilot-hf-tiny"

    def __init__(
        self,
        *,
        vocabulary_size: int = HF_VOCABULARY_SIZE,
        model_width: int = HF_MODEL_WIDTH,
        label_count: int = HF_LABEL_COUNT,
        dropout: float = 0.25,
        **kwargs,
    ) -> None:
        super().__init__(num_labels=label_count, **kwargs)
        self.vocabulary_size = vocabulary_size
        self.model_width = model_width
        self.label_count = label_count
        self.dropout = dropout


class FlashPilotTinyClassifier(PreTrainedModel):
    config_class = FlashPilotHFConfig
    base_model_prefix = "flashpilot"

    def __init__(self, config: FlashPilotHFConfig) -> None:
        super().__init__(config)
        self.embedding = nn.Embedding(config.vocabulary_size, config.model_width)
        self.projection = nn.Linear(config.model_width, config.model_width)
        self.dropout = nn.Dropout(config.dropout)
        self.classifier = nn.Linear(config.model_width, config.label_count)
        self.post_init()

    def forward(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor | None = None,
        **_: object,
    ) -> SequenceClassifierOutput:
        hidden = self.embedding(input_ids).mean(dim=1)
        hidden = torch.tanh(self.projection(hidden))
        logits = self.classifier(self.dropout(hidden))
        loss = functional.cross_entropy(logits, labels) if labels is not None else None
        return SequenceClassifierOutput(loss=loss, logits=logits)


class SyntheticClassificationDataset(Dataset[dict[str, torch.Tensor]]):
    """Index-derived synthetic samples with no external state or download."""

    def __init__(self, *, seed: int, start_index: int = 0, length: int = 32) -> None:
        self.seed = seed
        self.start_index = start_index
        self.length = length

    def __len__(self) -> int:
        return self.length

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        sample_index = self.start_index + index
        generator = torch.Generator(device="cpu")
        generator.manual_seed(self.seed + sample_index * 104_729)
        input_ids = torch.randint(
            0,
            HF_VOCABULARY_SIZE,
            (HF_SEQUENCE_LENGTH,),
            generator=generator,
            dtype=torch.long,
        )
        label = torch.tensor(int(input_ids.sum().item()) % HF_LABEL_COUNT, dtype=torch.long)
        return {"input_ids": input_ids, "labels": label}


def _parameter_iterator(model: nn.Module) -> Iterator[torch.Tensor]:
    for _, value in sorted(model.state_dict().items()):
        yield value.detach().cpu()


def create_hf_model(*, seed: int) -> FlashPilotTinyClassifier:
    torch.set_num_threads(1)
    enable_full_determinism(seed)
    return FlashPilotTinyClassifier(FlashPilotHFConfig())


def create_training_arguments(
    *,
    output_dir: Path,
    total_steps: int,
    checkpoint_step: int,
    seed: int,
    save_checkpoint: bool,
    save_only_model: bool,
    save_interval_steps: int | None = None,
) -> TrainingArguments:
    return TrainingArguments(
        output_dir=str(output_dir),
        per_device_train_batch_size=HF_BATCH_SIZE,
        max_steps=total_steps,
        learning_rate=0.01,
        lr_scheduler_type="linear",
        optim="adamw_torch",
        gradient_accumulation_steps=1,
        max_grad_norm=1.0,
        logging_strategy="steps",
        logging_steps=1,
        logging_first_step=True,
        disable_tqdm=True,
        report_to="none",
        save_strategy="steps" if save_checkpoint else "no",
        save_steps=save_interval_steps or checkpoint_step,
        save_total_limit=1,
        save_only_model=save_only_model,
        use_cpu=True,
        full_determinism=True,
        seed=seed,
        data_seed=seed,
        dataloader_num_workers=0,
        dataloader_pin_memory=False,
        dataloader_drop_last=True,
        remove_unused_columns=False,
        train_sampling_strategy="sequential",
    )


def create_trainer(
    *,
    model: FlashPilotTinyClassifier,
    output_dir: Path,
    total_steps: int,
    checkpoint_step: int,
    seed: int,
    save_checkpoint: bool,
    save_only_model: bool,
    save_interval_steps: int | None = None,
    callbacks: list[TrainerCallback] | None = None,
) -> Trainer:
    arguments = create_training_arguments(
        output_dir=output_dir,
        total_steps=total_steps,
        checkpoint_step=checkpoint_step,
        seed=seed,
        save_checkpoint=save_checkpoint,
        save_only_model=save_only_model,
        save_interval_steps=save_interval_steps,
    )
    return Trainer(
        model=model,
        args=arguments,
        train_dataset=SyntheticClassificationDataset(seed=seed),
        callbacks=callbacks,
    )


def fixed_evaluation_digest(model: FlashPilotTinyClassifier, *, seed: int) -> str:
    dataset = SyntheticClassificationDataset(seed=seed + 999_983, length=HF_BATCH_SIZE)
    input_ids = torch.stack([dataset[index]["input_ids"] for index in range(len(dataset))])
    model.eval()
    with torch.no_grad():
        logits = model(input_ids=input_ids).logits.detach().cpu()
    return state_digest(logits)


def summarize_trainer(
    trainer: Trainer,
    *,
    mode: str,
    scenario: HFScenario,
    checkpoint_step: int,
    model_loaded_from_checkpoint: bool,
    seed: int,
) -> HFRunSummary:
    if any(
        os.environ.get(name) != "1"
        for name in ("HF_DATASETS_OFFLINE", "HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE")
    ):
        raise RuntimeError("HF qualification worker requires all offline environment controls")
    if trainer.optimizer is None or trainer.lr_scheduler is None:
        raise RuntimeError("Trainer did not retain optimizer and scheduler evidence")
    losses = tuple(
        float(entry["loss"])
        for entry in trainer.state.log_history
        if "loss" in entry and "step" in entry
    )
    semantic_global_step = int(trainer.state.global_step)
    return HFRunSummary(
        mode=mode,
        scenario=scenario,
        worker_pid=os.getpid(),
        trainer_global_step=int(trainer.state.global_step),
        semantic_global_step=semantic_global_step,
        checkpoint_step=checkpoint_step,
        model_loaded_from_checkpoint=model_loaded_from_checkpoint,
        loss_history=losses,
        trainable_state_sha256=state_digest(tuple(_parameter_iterator(trainer.model))),
        evaluation_sha256=fixed_evaluation_digest(trainer.model, seed=seed),
        optimizer_sha256=state_digest(trainer.optimizer.state_dict()),
        scheduler_sha256=state_digest(trainer.lr_scheduler.state_dict()),
        transformers_version=transformers_version,
        torch_version=str(torch.__version__),
    )
