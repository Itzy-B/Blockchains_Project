"""Overview page."""

from __future__ import annotations

import streamlit as st

from .components import hero


def render(gateway, account: str, store) -> None:
    hero("Academic identity, under your control", "Register once. Share selectively. Revoke anytime.")
    registered = gateway.is_registered(account)
    credentials = gateway.credential_hashes(account) if registered else []
    consents = gateway.owner_consents(account) if registered else []
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Identity", "Registered" if registered else "Not registered")
    col2.metric("Credentials", len(credentials))
    col3.metric("Active consent", sum(item.active for item in consents))
    col4.metric("Rewards", f"{gateway.reward_balance(account):g} {gateway.reward_symbol()}")

    st.subheader("How the platform works")
    steps = st.columns(4)
    for column, number, title, detail in zip(
        steps,
        ("01", "02", "03", "04"),
        ("Create identity", "Add credential", "Grant consent", "Review audit"),
        (
            "Your personal record stays off chain; only its hash is registered.",
            "Register a verifiable hash of each academic credential.",
            "Choose the requester, credential, and access duration.",
            "Every granted or denied attempt becomes an immutable event.",
        ),
    ):
        with column:
            st.caption(number)
            st.markdown(f"**{title}**")
            st.write(detail)

    if not registered:
        st.info("Start on the Identity page using the active student wallet.")

