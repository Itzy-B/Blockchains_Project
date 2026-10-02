"""Shared domain models used by both demo and Web3 gateways."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
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
class GasCost:
    """The actual network fee paid by a mined transaction.

    `total_fee_wei` is calculated from the receipt, so it represents the
    confirmed fee rather than a pre transaction estimate.
    """

    gas_used: int
    effective_gas_price_wei: int
    total_fee_wei: int

    @property
    def total_fee_eth(self) -> Decimal:
        return Decimal(self.total_fee_wei) / Decimal(10**18)

    @property
    def effective_gas_price_gwei(self) -> Decimal:
        return Decimal(self.effective_gas_price_wei) / Decimal(10**9)


@dataclass(frozen=True)
class AccessRecord:
    owner: str
    requester: str
    credential_hash: str
    timestamp: int
    granted: bool
    transaction_hash: str
    gas_cost: GasCost | None = None


@dataclass(frozen=True)
class TransactionResult:
    transaction_hash: str
    block_number: int
    message: str = ""
    gas_cost: GasCost | None = None
