from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from flashpilot.adapters.native_pytorch import NativePyTorchAdapter
from flashpilot.agent.fixture_provider import FixtureContractProvider
from flashpilot.agent.service import build_contract_request, infer_checkpoint_contract
from flashpilot.contracts import (
    PersistenceContract,
    PersistenceContractValidationError,
    PersistenceItem,
    QualificationProfile,
    RecoveryExactness,
    RecoverySource,
    RequirementClass,
    canonical_contract_json,
    merge_with_deterministic_minimum,
    migrate_native_checkpoint_contract,
    native_minimum_persistence_contract,
    persistence_contract_sha256,
    validate_persistence_contract,
)
from flashpilot.contracts.schema import schema_documents


def _exact_contract() -> PersistenceContract:
    return native_minimum_persistence_contract(QualificationProfile.EXACT_TRAINING_RESUME)


def test_exact_native_contract_round_trip_and_hash_are_stable() -> None:
    contract = _exact_contract()
    serialized = canonical_contract_json(contract)
    restored = PersistenceContract.model_validate_json(serialized)

    assert restored == contract
    assert canonical_contract_json(restored) == serialized
    assert persistence_contract_sha256(restored) == persistence_contract_sha256(contract)
    assert len(persistence_contract_sha256(contract)) == 64


def test_canonical_contract_hash_ignores_input_item_order() -> None:
    contract = _exact_contract()
    reversed_contract = PersistenceContract(
        **{
            **contract.model_dump(),
            "items": tuple(reversed(contract.items)),
        }
    )

    assert reversed_contract.items == contract.items
    assert persistence_contract_sha256(reversed_contract) == persistence_contract_sha256(contract)


def test_unknown_classification_fails_closed() -> None:
    contract = _exact_contract()
    unknown = contract.items[0].model_copy(update={"requirement": RequirementClass.UNKNOWN})

    with pytest.raises(PersistenceContractValidationError, match="UNKNOWN state fails closed"):
        validate_persistence_contract(
            contract.model_copy(update={"items": (unknown, *contract.items[1:])})
        )


def test_required_state_without_source_fails_closed() -> None:
    contract = _exact_contract()
    contradictory = contract.items[0].model_copy(
        update={
            "recovery_source": RecoverySource.NONE,
            "exactness": RecoveryExactness.NON_EQUIVALENT,
        }
    )

    with pytest.raises(PersistenceContractValidationError, match="no recovery source"):
        validate_persistence_contract(
            contract.model_copy(update={"items": (contradictory, *contract.items[1:])})
        )


def test_immutable_reference_requires_identity_controls() -> None:
    contract = _exact_contract()
    base_index = next(
        index for index, item in enumerate(contract.items) if item.state_id == "base_model_identity"
    )
    missing_controls = contract.items[base_index].model_copy(update={"identity_controls": ()})
    items = list(contract.items)
    items[base_index] = missing_controls

    with pytest.raises(PersistenceContractValidationError, match="identity controls"):
        validate_persistence_contract(contract.model_copy(update={"items": tuple(items)}))


def test_exact_profile_rejects_tolerance_bounded_required_state() -> None:
    contract = _exact_contract()
    bounded = contract.items[0].model_copy(
        update={"exactness": RecoveryExactness.TOLERANCE_BOUNDED}
    )

    with pytest.raises(PersistenceContractValidationError, match="requires exact state"):
        validate_persistence_contract(
            contract.model_copy(update={"items": (bounded, *contract.items[1:])})
        )


def test_duplicate_state_ids_are_malformed() -> None:
    contract = _exact_contract()
    payload = contract.model_dump(mode="json")
    payload["items"].append(payload["items"][0])

    with pytest.raises(ValidationError, match="duplicate state IDs"):
        PersistenceContract.model_validate(payload)


def test_deterministic_minimum_overrides_omission_and_weaker_classification() -> None:
    minimum = _exact_contract()
    proposed_items = tuple(
        item.model_copy(
            update={
                "requirement": RequirementClass.OPTIONAL,
                "recovery_source": RecoverySource.NONE,
                "exactness": RecoveryExactness.NON_EQUIVALENT,
                "identity_controls": (),
                "evidence_ids": (),
            }
        )
        if item.state_id == "optimizer"
        else item
        for item in minimum.items
        if item.state_id != "torch_rng"
    )
    proposed = minimum.model_copy(update={"items": proposed_items})
    merged = merge_with_deterministic_minimum(proposed, minimum)
    merged_by_id = {item.state_id: item for item in merged.items}

    assert merged_by_id["optimizer"] == next(
        item for item in minimum.items if item.state_id == "optimizer"
    )
    assert merged_by_id["torch_rng"] == next(
        item for item in minimum.items if item.state_id == "torch_rng"
    )


def test_merge_rejects_state_outside_deterministic_inventory() -> None:
    minimum = _exact_contract()
    extra = PersistenceItem(
        state_id="framework.mystery_state",
        requirement=RequirementClass.OPTIONAL,
        recovery_source=RecoverySource.NONE,
        exactness=RecoveryExactness.NON_EQUIVALENT,
        reason="Unrecognized state must not be silently trusted.",
    )
    proposed = minimum.model_copy(update={"items": (*minimum.items, extra)})

    with pytest.raises(PersistenceContractValidationError, match="unknown state IDs"):
        merge_with_deterministic_minimum(proposed, minimum)


def test_merge_rejects_contradiction_instead_of_silently_repairing_it() -> None:
    minimum = _exact_contract()
    contradictory_items = tuple(
        item.model_copy(
            update={
                "recovery_source": RecoverySource.NONE,
                "exactness": RecoveryExactness.NON_EQUIVALENT,
            }
        )
        if item.state_id == "optimizer"
        else item
        for item in minimum.items
    )
    proposed = minimum.model_copy(update={"items": contradictory_items})

    with pytest.raises(PersistenceContractValidationError, match="no recovery source"):
        merge_with_deterministic_minimum(proposed, minimum)


def test_existing_accepted_native_checkpoint_contract_migrates() -> None:
    adapter = NativePyTorchAdapter()
    request = build_contract_request(
        adapter=adapter,
        user_objective="Lose no completed steps. Prioritize recovery correctness.",
        hard_rollback_limit_steps=0,
    )
    accepted = infer_checkpoint_contract(provider=FixtureContractProvider(), request=request)
    migrated = migrate_native_checkpoint_contract(accepted.contract)
    by_id = {item.state_id: item for item in migrated.items}

    assert migrated.qualification_profile is QualificationProfile.EXACT_TRAINING_RESUME
    assert migrated.max_rpo_steps == accepted.contract.rollback_limit_steps
    assert set(by_id) == {
        "adapter",
        "base_model_identity",
        "batch_position",
        "global_step",
        "numpy_rng",
        "optimizer",
        "python_rng",
        "scheduler",
        "torch_rng",
    }
    assert all(item.requirement is RequirementClass.REQUIRED for item in migrated.items)
    assert all(item.exactness is RecoveryExactness.EXACT for item in migrated.items)
    assert by_id["base_model_identity"].recovery_source is RecoverySource.IMMUTABLE_REFERENCE
    assert by_id["batch_position"].recovery_source is RecoverySource.DETERMINISTIC_RECOMPUTE


def test_model_only_profile_excludes_training_continuation_state() -> None:
    contract = native_minimum_persistence_contract(QualificationProfile.MODEL_ONLY_INFERENCE)
    by_id = {item.state_id: item for item in contract.items}

    assert by_id["adapter"].requirement is RequirementClass.REQUIRED
    assert by_id["base_model_identity"].requirement is RequirementClass.REQUIRED
    assert by_id["optimizer"].requirement is RequirementClass.EPHEMERAL
    assert by_id["optimizer"].recovery_source is RecoverySource.NONE
    assert by_id["optimizer"].exactness is RecoveryExactness.NON_EQUIVALENT


def test_checked_in_json_schemas_are_current() -> None:
    repository_root = Path(__file__).parents[2]
    for filename, expected in schema_documents().items():
        actual = json.loads((repository_root / "schemas" / filename).read_text(encoding="utf-8"))
        assert actual == expected
