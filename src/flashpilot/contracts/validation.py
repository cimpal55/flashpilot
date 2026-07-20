"""Fail-closed validation and deterministic minimum merging."""

from __future__ import annotations

from collections.abc import Iterable

from flashpilot.contracts.models import (
    PersistenceContract,
    PersistenceItem,
    QualificationProfile,
    RecoveryExactness,
    RecoverySource,
    RequirementClass,
)


class PersistenceContractValidationError(ValueError):
    """A contract cannot safely support its declared qualification profile."""


def _item_errors(item: PersistenceItem, profile: QualificationProfile) -> list[str]:
    errors: list[str] = []
    if item.requirement is RequirementClass.UNKNOWN:
        errors.append(f"{item.state_id}: UNKNOWN state fails closed")
    if item.requirement is RequirementClass.REQUIRED:
        if item.recovery_source is RecoverySource.NONE:
            errors.append(f"{item.state_id}: required state has no recovery source")
        if not item.evidence_ids:
            errors.append(f"{item.state_id}: required state has no evidence IDs")
        if item.exactness is RecoveryExactness.NON_EQUIVALENT:
            errors.append(f"{item.state_id}: required state cannot be non-equivalent")
        if (
            profile
            in {
                QualificationProfile.EXACT_TRAINING_RESUME,
                QualificationProfile.PREEMPTION_SAFE_TRAINING,
            }
            and item.exactness is not RecoveryExactness.EXACT
        ):
            errors.append(f"{item.state_id}: exact training continuation requires exact state")
    if item.requirement is RequirementClass.EPHEMERAL and (
        item.recovery_source is not RecoverySource.NONE
        or item.exactness is not RecoveryExactness.NON_EQUIVALENT
    ):
        errors.append(f"{item.state_id}: ephemeral state must use none/non-equivalent")
    if item.recovery_source is RecoverySource.NONE and (
        item.exactness is not RecoveryExactness.NON_EQUIVALENT
    ):
        errors.append(f"{item.state_id}: a none source cannot claim recovery equivalence")
    if (
        item.recovery_source
        in {
            RecoverySource.IMMUTABLE_REFERENCE,
            RecoverySource.EXTERNAL_DURABLE_SOURCE,
            RecoverySource.DETERMINISTIC_RECOMPUTE,
        }
        and not item.identity_controls
    ):
        errors.append(f"{item.state_id}: recovery source requires identity controls")
    return errors


def validate_persistence_contract(
    contract: PersistenceContract,
    *,
    known_state_ids: Iterable[str] | None = None,
) -> PersistenceContract:
    """Validate the deterministic safety minimum and return the unchanged contract."""

    errors: list[str] = []
    known = set(known_state_ids) if known_state_ids is not None else None
    for item in contract.items:
        if known is not None and item.state_id not in known:
            errors.append(f"{item.state_id}: state is not in the deterministic inventory")
        errors.extend(_item_errors(item, contract.qualification_profile))
    if errors:
        raise PersistenceContractValidationError("; ".join(errors))
    return contract


def _minimum_wins(proposed: PersistenceItem, minimum: PersistenceItem) -> bool:
    if minimum.requirement is RequirementClass.REQUIRED and (
        proposed.requirement is not RequirementClass.REQUIRED
        or proposed.recovery_source is not minimum.recovery_source
        or proposed.exactness is not minimum.exactness
        or not set(minimum.identity_controls).issubset(proposed.identity_controls)
        or not set(minimum.evidence_ids).issubset(proposed.evidence_ids)
    ):
        return True
    if minimum.requirement is RequirementClass.OPTIONAL and proposed.requirement in {
        RequirementClass.EPHEMERAL,
        RequirementClass.UNKNOWN,
    }:
        return True
    return False


def merge_with_deterministic_minimum(
    proposed: PersistenceContract,
    minimum: PersistenceContract,
) -> PersistenceContract:
    """Merge a proposal without allowing it to weaken or extend the local inventory."""

    validate_persistence_contract(minimum)
    if (
        proposed.qualification_profile is not minimum.qualification_profile
        or proposed.framework != minimum.framework
        or proposed.adapter != minimum.adapter
        or proposed.max_rpo_steps > minimum.max_rpo_steps
    ):
        raise PersistenceContractValidationError(
            "proposal context or RPO conflicts with the deterministic minimum"
        )
    minimum_by_id = {item.state_id: item for item in minimum.items}
    proposed_by_id = {item.state_id: item for item in proposed.items}
    unexpected = sorted(set(proposed_by_id) - set(minimum_by_id))
    if unexpected:
        raise PersistenceContractValidationError(
            f"proposal contains unknown state IDs: {', '.join(unexpected)}"
        )
    validate_persistence_contract(proposed, known_state_ids=minimum_by_id)

    merged_items = []
    for minimum_item in minimum.items:
        proposed_item = proposed_by_id.get(minimum_item.state_id)
        if proposed_item is None or _minimum_wins(proposed_item, minimum_item):
            merged_items.append(minimum_item)
        else:
            merged_items.append(proposed_item)
    merged = PersistenceContract(
        qualification_profile=minimum.qualification_profile,
        framework=minimum.framework,
        adapter=minimum.adapter,
        max_rpo_steps=minimum.max_rpo_steps,
        items=tuple(merged_items),
        assumptions=tuple(sorted(set(minimum.assumptions) | set(proposed.assumptions))),
        warnings=tuple(sorted(set(minimum.warnings) | set(proposed.warnings))),
    )
    return validate_persistence_contract(merged, known_state_ids=minimum_by_id)
