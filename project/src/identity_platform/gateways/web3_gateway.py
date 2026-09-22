"""Web3.py implementation of the UI gateway for a local Hardhat node."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from web3 import Web3

from ..config import Settings
from ..models import AccessRecord, ConsentRecord, TransactionResult


class Web3Gateway:
    def __init__(self, settings: Settings) -> None:
        self.web3 = Web3(Web3.HTTPProvider(settings.provider_url))
        if not self.web3.is_connected():
            raise ConnectionError(f"No Ethereum node responded at {settings.provider_url}")
        self.identity = self._contract(
            settings.addresses.digital_identity, settings.abi_directory / "DigitalIdentity.json"
        )
        self.consent = self._contract(
            settings.addresses.consent_manager, settings.abi_directory / "ConsentManager.json"
        )
        self.sharing = self._contract(
            settings.addresses.data_sharing, settings.abi_directory / "DataSharing.json"
        )
        self.token = self._contract(
            settings.addresses.reward_token, settings.abi_directory / "RewardToken.json"
        )

    def _contract(self, address: str, abi_path: Path) -> Any:
        if not address:
            raise ValueError(f"Missing contract address for {abi_path.stem} in .env")
        abi = json.loads(abi_path.read_text(encoding="utf-8"))
        return self.web3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)

    def accounts(self) -> list[str]:
        return list(self.web3.eth.accounts)

    def account_label(self, account: str) -> str:
        return f"{account[:6]}…{account[-4:]}"

    def network_name(self) -> str:
        return f"Chain {self.web3.eth.chain_id}"

    def is_registered(self, account: str) -> bool:
        return bool(self.identity.functions.isRegistered(self._address(account)).call())

    def identity_hash(self, account: str) -> str | None:
        identity_hash, registered = self.identity.functions.getIdentity(self._address(account)).call()
        return Web3.to_hex(identity_hash) if registered else None

    def register_identity(self, account: str, identity_hash: str) -> TransactionResult:
        return self._send(self.identity.functions.registerUser(identity_hash), account)

    def add_credential(self, account: str, credential_hash: str) -> TransactionResult:
        return self._send(self.identity.functions.addCredential(credential_hash), account)

    def credential_hashes(self, account: str) -> list[str]:
        values = self.identity.functions.getCredentialHashes(self._address(account)).call()
        return [Web3.to_hex(value) for value in values]

    def grant_consent(
        self, owner: str, requester: str, credential_hash: str, duration_days: int
    ) -> TransactionResult:
        return self._send(
            self.consent.functions.grantConsent(
                self._address(requester), credential_hash, duration_days
            ),
            owner,
        )

    def owner_consents(self, owner: str) -> list[ConsentRecord]:
        ids = self.consent.functions.getOwnerConsentIds(self._address(owner)).call()
        values: list[ConsentRecord] = []
        for consent_id in ids:
            row = self.consent.functions.getConsent(consent_id).call()
            values.append(
                ConsentRecord(
                    consent_id=int(consent_id),
                    owner=row[0],
                    requester=row[1],
                    credential_hash=Web3.to_hex(row[2]),
                    start_time=int(row[3]),
                    expiry_time=int(row[4]),
                    revoked=bool(row[5]),
                )
            )
        return values

    def revoke_consent(self, owner: str, consent_id: int) -> TransactionResult:
        return self._send(self.consent.functions.revokeConsent(consent_id), owner)

    def access_data(self, requester: str, owner: str, credential_hash: str) -> AccessRecord:
        receipt = self._receipt(
            self.sharing.functions.accessData(self._address(owner), credential_hash), requester
        )
        events = self.sharing.events.AccessAttempt().process_receipt(receipt)
        if not events:
            raise RuntimeError("DataSharing did not emit the required AccessAttempt event.")
        args = events[-1]["args"]
        return AccessRecord(
            owner=args["owner"],
            requester=args["requester"],
            credential_hash=Web3.to_hex(args["credentialHash"]),
            timestamp=int(args["timestamp"]),
            granted=bool(args["granted"]),
            transaction_hash=Web3.to_hex(receipt.transactionHash),
        )

    def access_records(self, owner: str | None = None) -> list[AccessRecord]:
        argument_filters = {"owner": self._address(owner)} if owner else None
        events = self.sharing.events.AccessAttempt().get_logs(
            from_block=0, to_block="latest", argument_filters=argument_filters
        )
        return [
            AccessRecord(
                owner=event["args"]["owner"],
                requester=event["args"]["requester"],
                credential_hash=Web3.to_hex(event["args"]["credentialHash"]),
                timestamp=int(event["args"]["timestamp"]),
                granted=bool(event["args"]["granted"]),
                transaction_hash=Web3.to_hex(event["transactionHash"]),
            )
            for event in reversed(events)
        ]

    def reward_balance(self, account: str) -> float:
        raw = self.token.functions.balanceOf(self._address(account)).call()
        decimals = self.token.functions.decimals().call()
        return raw / (10**decimals)

    def reward_symbol(self) -> str:
        return str(self.token.functions.symbol().call())

    def _send(self, function: Any, sender: str) -> TransactionResult:
        receipt = self._receipt(function, sender)
        if receipt.status != 1:
            raise RuntimeError("Transaction was mined but failed.")
        return TransactionResult(
            transaction_hash=Web3.to_hex(receipt.transactionHash),
            block_number=int(receipt.blockNumber),
        )

    def _receipt(self, function: Any, sender: str) -> Any:
        tx_hash = function.transact({"from": self._address(sender)})
        return self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

    @staticmethod
    def _address(value: str) -> str:
        return Web3.to_checksum_address(value)
