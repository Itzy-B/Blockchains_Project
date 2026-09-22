"""Shared domain models used by both demo and Web3 gateways."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class IdentityRecord:
    name: str
    email: str
    student_id: str
    university: str
    programme: str
    owner_address: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CredentialRecord:
    credential_id: str
    student_id: str
    university: str
    degree: str
    graduation_year: int
    classification: str
    issuer: str
    owner_address: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConsentRecord:
    consent_id: int
    owner: str
    requester: str
    credential_hash: str
    start_time: int
    expiry_time: int
    revoked: bool

    @property
    def active(self) -> bool:
        now = int(datetime.now(timezone.utc).timestamp())
        return not self.revoked and now < self.expiry_time


@dataclass(frozen=True)
class AccessRecord:
    owner: str
    requester: str
    credential_hash: str
    timestamp: int
    granted: bool
    transaction_hash: str


@dataclass(frozen=True)
class TransactionResult:
    transaction_hash: str
    block_number: int
    message: str = ""

