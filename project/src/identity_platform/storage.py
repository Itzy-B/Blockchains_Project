"""Simple local off chain JSON storage.

This is intentionally replaceable with IPFS or a database later. No plaintext
record is written to the blockchain; only the deterministic record hash is used
by the gateways.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SAFE_COMPONENT = re.compile(r"[^a-zA-Z0-9_-]")


class JsonRecordStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    @staticmethod
    def _safe(value: str) -> str:
        return SAFE_COMPONENT.sub("_", value.lower())

    def save_identity(self, owner: str, data: dict[str, Any], identity_hash: str) -> Path:
        path = self.root / "identities" / f"{self._safe(owner)}.json"
        payload = {"identity_hash": identity_hash, "record": data}
        return self._write(path, payload)

    def load_identity(self, owner: str) -> dict[str, Any] | None:
        path = self.root / "identities" / f"{self._safe(owner)}.json"
        return self._read(path)

    def save_credential(self, owner: str, data: dict[str, Any], credential_hash: str) -> Path:
        path = (
            self.root
            / "credentials"
            / self._safe(owner)
            / f"{self._safe(credential_hash)}.json"
        )
        payload = {"credential_hash": credential_hash, "record": data}
        return self._write(path, payload)

    def list_credentials(self, owner: str) -> list[dict[str, Any]]:
        directory = self.root / "credentials" / self._safe(owner)
        if not directory.exists():
            return []
        return [value for path in sorted(directory.glob("*.json")) if (value := self._read(path))]

    @staticmethod
    def _write(path: Path, payload: dict[str, Any]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    @staticmethod
    def _read(path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

