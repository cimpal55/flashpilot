"""Subprocess entry point for the included PyTorch Lightning workload."""

from __future__ import annotations

import argparse
from pathlib import Path

from flashpilot.adapters.lightning import PyTorchLightningAdapter
from flashpilot.lightning.callback import FlashPilotLightningCallback
from flashpilot.lightning.example import (
    FlashPilotLightningModule,
    configure_determinism,
    create_trainer,
    summarize_trainer,
    training_loader,
)
from flashpilot.lightning.models import LightningScenario
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.security.paths import PathSandbox


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FlashPilot local PyTorch Lightning worker")
    parser.add_argument(
        "--flashpilot-mode",
        choices=("control", "train-crash", "recover"),
        required=True,
    )
    parser.add_argument("--flashpilot-run-root", type=Path, required=True)
    parser.add_argument(
        "--flashpilot-scenario",
        choices=("complete", "weights-only"),
        required=True,
    )
    parser.add_argument("--flashpilot-checkpoint-step", type=int, required=True)
    parser.add_argument("--flashpilot-total-steps", type=int, required=True)
    parser.add_argument("--flashpilot-seed", type=int, required=True)
    parser.add_argument("--flashpilot-result-path", required=True)
    parser.add_argument("--flashpilot-checkpoint-path")
    return parser


def _run_control(args: argparse.Namespace, scenario: LightningScenario) -> None:
    run_root = PathSandbox.create(args.flashpilot_run_root).root
    configure_determinism(args.flashpilot_seed)
    model = FlashPilotLightningModule(seed=args.flashpilot_seed, scenario=scenario)
    trainer = create_trainer(
        root_dir=run_root / "control" / "trainer",
        max_steps=args.flashpilot_total_steps,
    )
    trainer.fit(model, train_dataloaders=training_loader(args.flashpilot_total_steps))
    summary = summarize_trainer(
        trainer,
        model,
        mode="control",
        scenario=scenario,
        checkpoint_step=0,
        semantic_global_step=args.flashpilot_total_steps,
        model_loaded_from_checkpoint=False,
        seed=args.flashpilot_seed,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=args.flashpilot_result_path,
        value=summary,
    )


def _run_crash_training(args: argparse.Namespace, scenario: LightningScenario) -> None:
    run_root = PathSandbox.create(args.flashpilot_run_root).root
    configure_determinism(args.flashpilot_seed)
    checkpoint_directory = (
        run_root / "crash" / "checkpoints" / f"checkpoint-{args.flashpilot_checkpoint_step}"
    )
    evidence_callback = FlashPilotLightningCallback(
        run_root=run_root,
        checkpoint_directory=checkpoint_directory,
        scenario=scenario,
        checkpoint_step=args.flashpilot_checkpoint_step,
        pause_for_parent_kill=True,
    )
    model = FlashPilotLightningModule(seed=args.flashpilot_seed, scenario=scenario)
    trainer = create_trainer(
        root_dir=run_root / "crash" / "trainer",
        max_steps=args.flashpilot_total_steps,
        callbacks=[evidence_callback],
    )
    trainer.fit(model, train_dataloaders=training_loader(args.flashpilot_total_steps))
    raise RuntimeError("crash worker was not terminated after checkpoint evidence")


def _run_recovery(args: argparse.Namespace, scenario: LightningScenario) -> None:
    if args.flashpilot_checkpoint_path is None:
        raise ValueError("recovery mode requires --flashpilot-checkpoint-path")
    run_root = PathSandbox.create(args.flashpilot_run_root).root
    checkpoint_directory = PathSandbox.create(run_root).resolve_relative(
        args.flashpilot_checkpoint_path,
        must_exist=True,
    )
    checkpoint_file = PyTorchLightningAdapter().checkpoint_file(checkpoint_directory)
    configure_determinism(args.flashpilot_seed)
    if scenario == "complete":
        model = FlashPilotLightningModule(seed=args.flashpilot_seed, scenario=scenario)
        trainer = create_trainer(
            root_dir=run_root / "recovery" / "trainer",
            max_steps=args.flashpilot_total_steps,
        )
        trainer.fit(
            model,
            train_dataloaders=training_loader(args.flashpilot_total_steps),
            ckpt_path=checkpoint_file,
        )
        semantic_global_step = int(trainer.global_step)
    else:
        model = FlashPilotLightningModule.load_from_checkpoint(
            checkpoint_file,
            seed=args.flashpilot_seed,
            scenario=scenario,
            semantic_offset=args.flashpilot_checkpoint_step,
        )
        remaining_steps = args.flashpilot_total_steps - args.flashpilot_checkpoint_step
        trainer = create_trainer(
            root_dir=run_root / "recovery" / "trainer",
            max_steps=remaining_steps,
        )
        trainer.fit(model, train_dataloaders=training_loader(remaining_steps))
        semantic_global_step = args.flashpilot_checkpoint_step + int(trainer.global_step)
    summary = summarize_trainer(
        trainer,
        model,
        mode="recover",
        scenario=scenario,
        checkpoint_step=args.flashpilot_checkpoint_step,
        semantic_global_step=semantic_global_step,
        model_loaded_from_checkpoint=True,
        seed=args.flashpilot_seed,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=args.flashpilot_result_path,
        value=summary,
    )


def main() -> None:
    args, forwarded = _parser().parse_known_args()
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]
    if any(argument.startswith("--flashpilot-") for argument in forwarded):
        raise ValueError("forwarded arguments cannot override FlashPilot control fields")
    scenario: LightningScenario = args.flashpilot_scenario
    if args.flashpilot_mode == "control":
        _run_control(args, scenario)
    elif args.flashpilot_mode == "train-crash":
        _run_crash_training(args, scenario)
    else:
        _run_recovery(args, scenario)


if __name__ == "__main__":
    main()
