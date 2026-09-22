"""In-memory gateway used for UI development and demonstrations."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field

from ..models import AccessRecord, ConsentRecord, TransactionResult


DEMO_ACCOUNTS = {
    "0x1111111111111111111111111111111111111111": "Alice · Student",
    "0x2222222222222222222222222222222222222222": "Bob · Employer",
    "0x3333333333333333333333333333333333333333": "Charlie · University",
}


@dataclass
class DemoState:
    identities: dict[str, str] = field(default_factory=dict)
    credentials: dict[str, list[str]] = field(default_factory=dict)
    consents: list[ConsentRecord] = field(default_factory=list)
    access_log: list[AccessRecord] = field(default_factory=list)
    rewards: dict[str, float] = field(default_factory=dict)
    block_number: int = 1

    @classmethod
    def seeded(cls) -> "DemoState":
        return cls()


class DemoGateway:
    def __init__(self, state: DemoState) -> None:
        self.state = state

    def accounts(self) -> list[str]:
        return list(DEMO_ACCOUNTS)

    def account_label(self, account: str) -> str:
        return f"{DEMO_ACCOUNTS.get(account, 'Account')} · {account[:6]}…{account[-4:]}"

    def network_name(self) -> str:
        return "Demo network"

    def is_registered(self, account: str) -> bool:
        return account in self.state.identities

    def identity_hash(self, account: str) -> str | None:
        return self.state.identities.get(account)

    def register_identity(self, account: str, identity_hash: str) -> TransactionResult:
        if self.is_registered(account):
            raise ValueError("This wallet is already registered.")
        self.state.identities[account] = identity_hash
        self.state.credentials[account] = []
        return self._transaction("Identity registered")

    def add_credential(self, account: str, credential_hash: str) -> TransactionResult:
        if not self.is_registered(account):
            raise ValueError("Register an identity before adding a credential.")
        values = self.state.credentials.setdefault(account, [])
        if credential_hash in values:
            raise ValueError("This credential hash is already registered.")
        values.append(credential_hash)
        return self._transaction("Credential registered")

    def credential_hashes(self, account: str) -> list[str]:
        return list(self.state.credentials.get(account, []))

    def grant_consent(
        self, owner: str, requester: str, credential_hash: str, duration_days: int
    ) -> TransactionResult:
        if not 1 <= duration_days <= 365:
            raise ValueError("Consent duration must be between 1 and 365 days.")
        if credential_hash not in self.state.credentials.get(owner, []):
            raise ValueError("The credential is not registered to this owner.")
        now = int(time.time())
        consent = ConsentRecord(
            consent_id=len(self.state.consents),
            owner=owner,
            requester=requester,
            credential_hash=credential_hash,
            start_time=now,
            expiry_time=now + duration_days * 86_400,
            revoked=False,
        )
        self.state.consents.append(consent)
        self.state.rewards[owner] = self.state.rewards.get(owner, 0) + 10
        return self._transaction(f"Consent #{consent.consent_id} granted")

    def owner_consents(self, owner: str) -> list[ConsentRecord]:
        return [item for item in self.state.consents if item.owner == owner]

    def revoke_consent(self, owner: str, consent_id: int) -> TransactionResult:
        if not 0 <= consent_id < len(self.state.consents):
            raise ValueError("Consent does not exist.")
        consent = self.state.consents[consent_id]
        if consent.owner != owner:
            raise PermissionError("Only the consent owner can revoke it.")
        if consent.revoked:
            raise ValueError("Consent is already revoked.")
        self.state.consents[consent_id] = ConsentRecord(**{**consent.__dict__, "revoked": True})
        return self._transaction(f"Consent #{consent_id} revoked")

    def access_data(self, requester: str, owner: str, credential_hash: str) -> AccessRecord:
        granted = any(
            consent.owner == owner
            and consent.requester == requester
            and consent.credential_hash == credential_hash
            and consent.active
            for consent in self.state.consents
        )
        tx = self._transaction("Access granted" if granted else "Access denied")
        record = AccessRecord(
            owner=owner,
            requester=requester,
            credential_hash=credential_hash,
            timestamp=int(time.time()),
            granted=granted,
            transaction_hash=tx.transaction_hash,
        )
        self.state.access_log.append(record)
        return record

    def access_records(self, owner: str | None = None) -> list[AccessRecord]:
        records = self.state.access_log
        if owner:
            records = [record for record in records if record.owner == owner]
        return list(reversed(records))

    def reward_balance(self, account: str) -> float:
        return self.state.rewards.get(account, 0)

    def reward_symbol(self) -> str:
        return "ACCESS"

    def _transaction(self, message: str) -> TransactionResult:
        self.state.block_number += 1
        seed = f"{self.state.block_number}:{message}:{time.time_ns()}".encode()
        tx_hash = "0x" + hashlib.sha256(seed).hexdigest()
        return TransactionResult(tx_hash, self.state.block_number, message)

