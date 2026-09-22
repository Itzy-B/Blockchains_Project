"""Deterministic hashing for off-chain records."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any


def canonical_json(data: Mapping[str, Any]) -> str:
    """Return stable JSON so the same record always produces the same hash."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def record_hash(data: Mapping[str, Any]) -> str:
    """Return a bytes32 compatible SHA-256 hash prefixed with 0x."""
    digest = hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()
    return f"0x{digest}"


def hashable_identity(data: Mapping[str, Any]) -> dict[str, Any]:
    """Exclude storage metadata from the identity hash."""
    fields = ("name", "email", "student_id", "university", "programme", "owner_address")
    return {field: data[field] for field in fields}


def hashable_credential(data: Mapping[str, Any]) -> dict[str, Any]:
    """Exclude storage metadata from the credential hash."""
    fields = (
        "credential_id",
        "student_id",
        "university",
        "degree",
        "graduation_year",
        "classification",
        "issuer",
        "owner_address",
    )
    return {field: data[field] for field in fields}

