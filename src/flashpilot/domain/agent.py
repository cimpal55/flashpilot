"""Strict schemas for the two bounded GPT-5.6 roles."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from flashpilot.domain.capabilities import SaveRestoreSummary, StateName, WorkloadCapabilities
from flashpilot.domain.recovery import RecoveryEvidenceId, RecoveryGateCheckId

IntegrityControl = Literal[
    "manifest",
    "checksums",
    "completion_marker",
    "atomic_commit",
    "base_artifact_hash",
]
CorrectnessPriority = Literal["strict", "balanced"]
Confidence = Literal["low", "medium", "high"]
AgentRole = Literal["checkpoint-contract", "failure-analysis"]
ProviderName = Literal["openai", "fixture"]
LiveOrFixture = Literal["live", "fixture"]
ValidationStatus = Literal["accepted", "rejected"]
AgentResponseSource = Literal[
    "captured_live_response",
    "deterministic_local_fixture",
    "captured_live_response_replay",
]

RepairActionType = Literal[
    "persist_model_state",
    "persist_adapter_state",
    "persist_optimizer_state",
    "persist_scheduler_state",
    "persist_scaler_state",
    "persist_global_step",
    "persist_python_rng_state",
    "persist_numpy_rng_state",
    "persist_torch_rng_state",
    "persist_torch_cuda_rng_state",
    "persist_sampler_state",
    "add_base_model_hash",
    "add_manifest",
    "add_checksums",
    "use_atomic_checkpoint_commit",
    "restore_state_before_next_batch",
    "fallback_to_previous_valid_checkpoint",
    "quarantine_invalid_checkpoint",
    "change_checkpoint_interval",
    "change_retention_count",
    "change_supported_checkpoint_strategy",
]

NATIVE_PYTORCH_REPAIR_ACTIONS: tuple[RepairActionType, ...] = (
    "persist_optimizer_state",
    "persist_scheduler_state",
    "persist_python_rng_state",
    "persist_numpy_rng_state",
    "persist_torch_rng_state",
    "restore_state_before_next_batch",
)


class StrictAgentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ContractRequirement(StrictAgentModel):
    state: StateName
    required: bool
    reason: str = Field(min_length=1, max_length=500)


class CheckpointContract(StrictAgentModel):
    schema_version: Literal["checkpoint-contract-v1"] = "checkpoint-contract-v1"
    required_state: tuple[ContractRequirement, ...]
    required_integrity_controls: tuple[IntegrityControl, ...]
    restore_order_requirements: tuple[str, ...]
    rollback_limit_steps: int = Field(ge=0)
    correctness_priority: CorrectnessPriority
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]

    @model_validator(mode="after")
    def reject_duplicate_requirements(self) -> CheckpointContract:
        states = [requirement.state for requirement in self.required_state]
        if len(states) != len(set(states)):
            raise ValueError("checkpoint contract contains duplicate state requirements")
        controls = list(self.required_integrity_controls)
        if len(controls) != len(set(controls)):
            raise ValueError("checkpoint contract contains duplicate integrity controls")
        return self


class ContractInferenceRequest(StrictAgentModel):
    schema_version: Literal["contract-inference-request-v1"] = "contract-inference-request-v1"
    user_objective: str = Field(min_length=1, max_length=2_000)
    hard_rollback_limit_steps: int = Field(ge=0)
    workload_capabilities: WorkloadCapabilities
    save_restore_summary: SaveRestoreSummary
    integrity_protocol: tuple[IntegrityControl, ...]
    supported_state: tuple[StateName, ...]
    mandatory_gate_requirements: tuple[str, ...]


class ContractValidationResult(StrictAgentModel):
    schema_version: Literal["contract-validation-v1"] = "contract-validation-v1"
    contract: CheckpointContract
    added_integrity_controls: tuple[IntegrityControl, ...]
    unsupported_required_state: tuple[StateName, ...]
    warnings: tuple[str, ...]


class RepairAction(StrictAgentModel):
    action: RepairActionType
    reason: str = Field(min_length=1, max_length=500)
    evidence_ids: tuple[RecoveryEvidenceId, ...] = Field(default_factory=tuple)


class RepairPlan(StrictAgentModel):
    actions: tuple[RepairAction, ...]
    expected_gate_improvements: tuple[str, ...]
    risks: tuple[str, ...]
    assumptions: tuple[str, ...]


class FailureAnalysis(StrictAgentModel):
    schema_version: Literal["failure-analysis-v2"] = "failure-analysis-v2"
    root_cause_hypothesis: str = Field(min_length=1, max_length=2_000)
    affected_gate_checks: tuple[RecoveryGateCheckId, ...]
    confirming_evidence: tuple[RecoveryEvidenceId, ...]
    repair_plan: RepairPlan
    confidence: Confidence
    limitations: tuple[str, ...]


class RepairActionDecision(StrictAgentModel):
    action: RepairActionType
    disposition: Literal["accepted", "rejected", "unsupported"]
    reason: str = Field(min_length=1)
    evidence_ids: tuple[RecoveryEvidenceId, ...]


class RepairPlanValidationResult(StrictAgentModel):
    schema_version: Literal["repair-plan-validation-v1"] = "repair-plan-validation-v1"
    decisions: tuple[RepairActionDecision, ...]
    accepted_actions: tuple[RepairActionType, ...]
    rejected_actions: tuple[RepairActionType, ...]
    unsupported_actions: tuple[RepairActionType, ...]
    attempt_number: Literal[1] = 1
    execution_performed: Literal[False] = False

    @model_validator(mode="after")
    def validate_decision_summaries(self) -> RepairPlanValidationResult:
        expected = {
            "accepted": tuple(
                decision.action for decision in self.decisions if decision.disposition == "accepted"
            ),
            "rejected": tuple(
                decision.action for decision in self.decisions if decision.disposition == "rejected"
            ),
            "unsupported": tuple(
                decision.action
                for decision in self.decisions
                if decision.disposition == "unsupported"
            ),
        }
        if self.accepted_actions != expected["accepted"]:
            raise ValueError("accepted action summary does not match decisions")
        if self.rejected_actions != expected["rejected"]:
            raise ValueError("rejected action summary does not match decisions")
        if self.unsupported_actions != expected["unsupported"]:
            raise ValueError("unsupported action summary does not match decisions")
        return self


class ProviderResponseMetadata(StrictAgentModel):
    provider: ProviderName
    live_or_fixture: LiveOrFixture
    response_id: str | None
    fixture_provenance: Literal[
        "not_applicable",
        "deterministic_local_fixture",
        "live_gpt_5_6_capture",
    ]

    @model_validator(mode="after")
    def validate_provider_label(self) -> ProviderResponseMetadata:
        if self.provider == "openai":
            if self.live_or_fixture != "live" or self.fixture_provenance != "not_applicable":
                raise ValueError("OpenAI provider metadata must be labeled live")
            if self.response_id is None:
                raise ValueError("OpenAI provider metadata requires a response ID")
        elif (
            self.live_or_fixture != "fixture"
            or self.response_id is not None
            or self.fixture_provenance == "not_applicable"
        ):
            raise ValueError(
                "fixture provider metadata must be labeled fixture with explicit provenance "
                "and without response ID"
            )
        return self


class AgentCallMetadata(StrictAgentModel):
    schema_version: Literal["agent-call-metadata-v1"] = "agent-call-metadata-v1"
    provider: ProviderName
    model: Literal["gpt-5.6"] = "gpt-5.6"
    role: AgentRole
    prompt_version: Literal["v1", "v2"]
    output_schema_version: str = Field(min_length=1)
    live_or_fixture: LiveOrFixture
    source: AgentResponseSource
    fixture_provenance: Literal[
        "not_applicable",
        "deterministic_local_fixture",
        "live_gpt_5_6_capture",
    ]
    response_id: str | None
    timestamp: datetime
    request_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    store: Literal[False] = False
    validation_status: ValidationStatus = "accepted"

    @model_validator(mode="after")
    def validate_timestamp(self) -> AgentCallMetadata:
        if self.timestamp.tzinfo is None:
            raise ValueError("agent call timestamp must include a timezone")
        if self.provider == "openai":
            if self.live_or_fixture != "live" or self.fixture_provenance != "not_applicable":
                raise ValueError("OpenAI call metadata must be labeled live")
            if self.source != "captured_live_response" or self.response_id is None:
                raise ValueError(
                    "OpenAI call metadata requires captured-live provenance and a response ID"
                )
        elif (
            self.live_or_fixture != "fixture"
            or self.response_id is not None
            or self.fixture_provenance == "not_applicable"
        ):
            raise ValueError(
                "fixture call metadata must be labeled fixture with explicit provenance "
                "and without response ID"
            )
        elif (
            self.fixture_provenance == "deterministic_local_fixture"
            and self.source != "deterministic_local_fixture"
        ) or (
            self.fixture_provenance == "live_gpt_5_6_capture"
            and self.source != "captured_live_response_replay"
        ):
            raise ValueError("fixture call metadata source does not match its provenance")
        return self


class AgentValidationRejection(StrictAgentModel):
    schema_version: Literal["agent-validation-rejection-v1"] = "agent-validation-rejection-v1"
    validation_status: Literal["rejected"] = "rejected"
    validator: Literal["deterministic_guardrails"] = "deterministic_guardrails"
    error_type: Literal["GuardrailViolation"] = "GuardrailViolation"
    reason: str = Field(min_length=1, max_length=2_000)


class ContractProviderResult(StrictAgentModel):
    output: CheckpointContract
    provider_metadata: ProviderResponseMetadata


class FailureProviderResult(StrictAgentModel):
    output: FailureAnalysis
    provider_metadata: ProviderResponseMetadata


class RepairAttemptAdmission(StrictAgentModel):
    schema_version: Literal["repair-attempt-admission-v1"] = "repair-attempt-admission-v1"
    attempt_number: Literal[1] = 1
    admitted_at: datetime
    execution_performed: Literal[False] = False

    @model_validator(mode="after")
    def validate_admitted_at(self) -> RepairAttemptAdmission:
        if self.admitted_at.tzinfo is None:
            raise ValueError("repair attempt admission timestamp must include a timezone")
        return self
