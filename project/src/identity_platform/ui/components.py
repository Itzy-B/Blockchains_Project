"""Reusable presentation helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st

from ..models import GasCost, TransactionResult


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f6f7fb; }
        [data-testid="stSidebar"] { background: #111827; }
        [data-testid="stSidebar"] * { color: #f9fafb; }
        .hero {
            padding: 1.6rem 1.8rem; border-radius: 18px;
            background: linear-gradient(120deg, #172554, #312e81 55%, #5b21b6);
            color: white; margin-bottom: 1.2rem;
        }
        .hero h1 { margin: 0; font-size: 2rem; }
        .hero p { margin: .45rem 0 0; opacity: .82; }
        .hash { font-family: monospace; overflow-wrap: anywhere; font-size: .82rem; }
        div[data-testid="stMetric"] {
            background: white; border: 1px solid #e5e7eb; padding: 1rem;
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<section class="hero"><h1>{title}</h1><p>{subtitle}</p></section>',
        unsafe_allow_html=True,
    )


def render_sidebar_status(gateway: Any, mode: str) -> None:
    st.caption("CONNECTION")
    st.success("Demo mode" if mode == "demo" else "Blockchain connected")
    st.caption(gateway.network_name())


def transaction_success(result: TransactionResult) -> None:
    st.success(result.message or "Transaction confirmed")
    st.caption(f"Block {result.block_number} · {short_hash(result.transaction_hash, 12)}")
    render_gas_cost(result.gas_cost)


def render_gas_cost(gas_cost: GasCost | None) -> None:
    """Display the confirmed network fee when the action used a real chain."""
    if gas_cost is None:
        st.caption("Gas cost: unavailable in demo mode.")
        return
    st.caption(
        f"Gas used: {gas_cost.gas_used:,} · "
        f"Gas price: {gas_cost.effective_gas_price_gwei:.3f} gwei · "
        f"Network fee: {gas_cost.total_fee_eth:.8f} ETH"
    )
    st.caption(f"Exact fee: {gas_cost.total_fee_wei:,} wei")


def short_hash(value: str, size: int = 8) -> str:
    if len(value) <= size * 2:
        return value
    return f"{value[:size]}…{value[-size:]}"


def format_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%d %b %Y, %H:%M UTC")


def error_message(exc: Exception) -> None:
    message = str(exc)
    # Web3 exceptions can be extremely long; keep the actionable part visible.
    st.error(message[:600] if message else exc.__class__.__name__)
