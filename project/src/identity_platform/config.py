"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ContractAddresses:
    digital_identity: str = ""
    consent_manager: str = ""
    data_sharing: str = ""
    reward_token: str = ""


@dataclass(frozen=True)
class Settings:
    mode: str
    provider_url: str
    addresses: ContractAddresses
    abi_directory: Path
    data_directory: Path

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv(PROJECT_ROOT / ".env")
        mode = os.getenv("APP_MODE", "demo").strip().lower()
        if mode not in {"demo", "web3"}:
            raise ValueError("APP_MODE must be either 'demo' or 'web3'.")
        return cls(
            mode=mode,
            provider_url=os.getenv("WEB3_PROVIDER_URL", "http://127.0.0.1:8545"),
            addresses=ContractAddresses(
                digital_identity=os.getenv("DIGITAL_IDENTITY_ADDRESS", ""),
                consent_manager=os.getenv("CONSENT_MANAGER_ADDRESS", ""),
                data_sharing=os.getenv("DATA_SHARING_ADDRESS", ""),
                reward_token=os.getenv("REWARD_TOKEN_ADDRESS", ""),
            ),
            abi_directory=PROJECT_ROOT / "abi",
            data_directory=PROJECT_ROOT / "data",
        )

