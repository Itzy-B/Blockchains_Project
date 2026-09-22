"""Reward token page."""

from __future__ import annotations

import streamlit as st

from .components import hero


def render(gateway, account: str, store) -> None:
    hero("Consent rewards", "Tokens recognize consent without transferring data ownership.")
    balance = gateway.reward_balance(account)
    symbol = gateway.reward_symbol()
    left, right = st.columns([1, 2])
    left.metric("Current balance", f"{balance:g} {symbol}")
    with right:
        st.markdown("**What the token means**")
        st.write(
            "A student receives a reward when granting consent. The token does not sell the "
            "credential, grant permanent access, or change who owns the academic record."
        )
    st.info("Access always depends on an active, unexpired, non-revoked consent record.")

