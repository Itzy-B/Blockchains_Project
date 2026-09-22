"""Validation shared by UI forms and demo-mode behavior."""

from __future__ import annotations

import re


ADDRESS_PATTERN = re.compile(r"^0x[a-fA-F0-9]{40}$")
BYTES32_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")


def is_ethereum_address(value: str) -> bool:
    return bool(ADDRESS_PATTERN.fullmatch(value.strip()))


def is_bytes32(value: str) -> bool:
    return bool(BYTES32_PATTERN.fullmatch(value.strip()))

