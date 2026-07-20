"""Canonical serialization and identity for persistence contracts."""

from __future__ import annotations

import hashlib
import json

from flashpilot.contracts.models import PersistenceContract


def canonical_contract_json(contract: PersistenceContract) -> str:
    """Return stable UTF-8 JSON with no presentation whitespace."""

    return json.dumps(
        contract.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def persistence_contract_sha256(contract: PersistenceContract) -> str:
    """Hash the canonical contract representation."""

    return hashlib.sha256(canonical_contract_json(contract).encode("utf-8")).hexdigest()
