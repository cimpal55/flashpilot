import json

from flashpilot.workload.control import run_control


def test_repeated_uninterrupted_controls_match_exactly(tmp_path) -> None:
    first = run_control("ci")
    output_path = tmp_path / "control-summary.json"
    second = run_control("ci", output_path=output_path)

    assert first == second
    assert first.final_global_step == 8
    assert first.environment.device == "cpu"
    assert first.environment.deterministic_algorithms is True
    assert first.environment.torch_threads == 1
    assert first.trainable_state.parameter_count > 0
    assert first.evaluation.sha256
    assert first.optimizer.optimizer_type == "AdamW"
    assert first.optimizer.state_entries > 0
    assert first.scheduler.scheduler_type == "LinearLR"
    assert first.scheduler.last_epoch == first.final_global_step
    assert json.loads(output_path.read_text(encoding="utf-8")) == json.loads(second.to_json())
