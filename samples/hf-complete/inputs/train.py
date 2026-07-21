"""Subprocess entry point for the included offline HF Trainer example."""

from __future__ import annotations

import argparse
import signal
from pathlib import Path

from flashpilot.hf.callback import FlashPilotTrainerCallback
from flashpilot.hf.example import create_hf_model, create_trainer, summarize_trainer
from flashpilot.hf.models import HFScenario
from flashpilot.orchestration.artifacts import write_json_artifact
from flashpilot.preemption.callback import FlashPilotPreemptionCallback, PreemptionSignalState
from flashpilot.security.paths import PathSandbox


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FlashPilot local HF Trainer worker")
    parser.add_argument(
        "--flashpilot-mode",
        choices=("control", "train-crash", "preempt", "recover"),
        required=True,
    )
    parser.add_argument("--flashpilot-run-root", type=Path, required=True)
    parser.add_argument(
        "--flashpilot-scenario",
        choices=("complete", "model-only"),
        required=True,
    )
    parser.add_argument("--flashpilot-checkpoint-step", type=int, required=True)
    parser.add_argument("--flashpilot-total-steps", type=int, required=True)
    parser.add_argument("--flashpilot-seed", type=int, required=True)
    parser.add_argument("--flashpilot-result-path", required=True)
    parser.add_argument("--flashpilot-checkpoint-path")
    parser.add_argument("--flashpilot-grace-period-seconds", type=int)
    return parser


def _run_control(args: argparse.Namespace, scenario: HFScenario) -> None:
    run_root = PathSandbox.create(args.flashpilot_run_root).root
    model = create_hf_model(seed=args.flashpilot_seed)
    trainer = create_trainer(
        model=model,
        output_dir=run_root / "control" / "trainer",
        total_steps=args.flashpilot_total_steps,
        checkpoint_step=args.flashpilot_checkpoint_step,
        seed=args.flashpilot_seed,
        save_checkpoint=False,
        save_only_model=False,
    )
    trainer.train()
    summary = summarize_trainer(
        trainer,
        mode="control",
        scenario=scenario,
        checkpoint_step=0,
        model_loaded_from_checkpoint=False,
        seed=args.flashpilot_seed,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=args.flashpilot_result_path,
        value=summary,
    )


def _run_crash_training(args: argparse.Namespace, scenario: HFScenario) -> None:
    run_root = PathSandbox.create(args.flashpilot_run_root).root
    model = create_hf_model(seed=args.flashpilot_seed)
    callback = FlashPilotTrainerCallback(
        run_root=run_root,
        scenario=scenario,
        checkpoint_step=args.flashpilot_checkpoint_step,
        pause_for_parent_kill=True,
    )
    trainer = create_trainer(
        model=model,
        output_dir=run_root / "crash" / "checkpoints",
        total_steps=args.flashpilot_total_steps,
        checkpoint_step=args.flashpilot_checkpoint_step,
        seed=args.flashpilot_seed,
        save_checkpoint=True,
        save_only_model=scenario == "model-only",
        callbacks=[callback],
    )
    trainer.train()
    raise RuntimeError("crash worker was not terminated after checkpoint evidence")


def _run_recovery(args: argparse.Namespace, scenario: HFScenario) -> None:
    if args.flashpilot_checkpoint_path is None:
        raise ValueError("recovery mode requires --flashpilot-checkpoint-path")
    run_root = PathSandbox.create(args.flashpilot_run_root).root
    checkpoint = PathSandbox.create(run_root).resolve_relative(
        args.flashpilot_checkpoint_path,
        must_exist=True,
    )
    model = create_hf_model(seed=args.flashpilot_seed)
    trainer = create_trainer(
        model=model,
        output_dir=run_root / "recovery" / "trainer",
        total_steps=args.flashpilot_total_steps,
        checkpoint_step=args.flashpilot_checkpoint_step,
        seed=args.flashpilot_seed,
        save_checkpoint=False,
        save_only_model=False,
    )
    trainer.train(resume_from_checkpoint=str(checkpoint))
    summary = summarize_trainer(
        trainer,
        mode="recover",
        scenario=scenario,
        checkpoint_step=args.flashpilot_checkpoint_step,
        model_loaded_from_checkpoint=True,
        seed=args.flashpilot_seed,
    )
    write_json_artifact(
        run_root=run_root,
        relative_path=args.flashpilot_result_path,
        value=summary,
    )


def _run_preemption_training(args: argparse.Namespace, scenario: HFScenario) -> None:
    if scenario != "complete":
        raise ValueError("preemption certification requires the complete checkpoint scenario")
    if args.flashpilot_grace_period_seconds is None:
        raise ValueError("preemption mode requires --flashpilot-grace-period-seconds")
    if args.flashpilot_grace_period_seconds < 1:
        raise ValueError("preemption grace period must be positive")
    run_root = PathSandbox.create(args.flashpilot_run_root).root
    signal_state = PreemptionSignalState()

    def receive_sigterm(signum: int, frame: object) -> None:
        del frame
        if signum != signal.SIGTERM:
            raise RuntimeError("preemption worker received an unexpected signal")
        signal_state.record_sigterm()

    previous_handler = signal.signal(signal.SIGTERM, receive_sigterm)
    try:
        model = create_hf_model(seed=args.flashpilot_seed)
        callback = FlashPilotPreemptionCallback(
            run_root=run_root,
            checkpoint_step=args.flashpilot_checkpoint_step,
            grace_period_seconds=args.flashpilot_grace_period_seconds,
            signal_state=signal_state,
        )
        trainer = create_trainer(
            model=model,
            output_dir=run_root / "preemption" / "checkpoints",
            total_steps=args.flashpilot_total_steps,
            checkpoint_step=args.flashpilot_checkpoint_step,
            seed=args.flashpilot_seed,
            save_checkpoint=True,
            save_only_model=False,
            save_interval_steps=args.flashpilot_total_steps + 1,
            callbacks=[callback],
        )
        trainer.train()
        if trainer.state.global_step != args.flashpilot_checkpoint_step:
            raise RuntimeError("preemption worker did not stop at its checkpoint boundary")
        if signal_state.received_at is None:
            raise RuntimeError("preemption worker exited without receiving SIGTERM")
    finally:
        signal.signal(signal.SIGTERM, previous_handler)


def main() -> None:
    args, forwarded = _parser().parse_known_args()
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]
    if any(argument.startswith("--flashpilot-") for argument in forwarded):
        raise ValueError("forwarded arguments cannot override FlashPilot control fields")
    scenario: HFScenario = args.flashpilot_scenario
    if args.flashpilot_mode == "control":
        _run_control(args, scenario)
    elif args.flashpilot_mode == "train-crash":
        _run_crash_training(args, scenario)
    elif args.flashpilot_mode == "preempt":
        _run_preemption_training(args, scenario)
    else:
        _run_recovery(args, scenario)


if __name__ == "__main__":
    main()
