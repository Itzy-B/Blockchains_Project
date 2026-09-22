"""Consent granting and revocation page."""

from __future__ import annotations

import streamlit as st

from ..validation import is_ethereum_address
from .components import error_message, format_time, hero, short_hash, transaction_success


def render(gateway, account: str, store) -> None:
    hero("Consent control", "Share one credential with one requester for a limited time.")
    if not gateway.is_registered(account):
        st.warning("Only a registered identity can grant consent.")
        return

    hashes = gateway.credential_hashes(account)
    if not hashes:
        st.info("Add a credential before granting consent.")
    else:
        with st.form("grant_consent"):
            requester = st.text_input("Requester wallet address", placeholder="0x…")
            credential_hash = st.selectbox(
                "Credential", hashes, format_func=lambda value: short_hash(value, 12)
            )
            duration = st.slider("Duration (days)", min_value=1, max_value=365, value=30)
            submitted = st.form_submit_button("Grant consent", type="primary", width="stretch")
        if submitted:
            if not is_ethereum_address(requester):
                st.error("Enter a valid Ethereum requester address.")
            elif requester.lower() == account.lower():
                st.error("The requester must be a different wallet.")
            else:
                try:
                    result = gateway.grant_consent(account, requester, credential_hash, duration)
                    transaction_success(result)
                    st.rerun()
                except Exception as exc:
                    error_message(exc)

    st.subheader("Consent history")
    consents = list(reversed(gateway.owner_consents(account)))
    if not consents:
        st.info("No consent records yet.")
        return
    for item in consents:
        col1, col2, col3, col4 = st.columns([0.7, 2, 1.4, 1])
        col1.markdown(f"**#{item.consent_id}**")
        col2.write(short_hash(item.requester, 10))
        status = "Active" if item.active else ("Revoked" if item.revoked else "Expired")
        col3.write(f"{status} · {format_time(item.expiry_time)}")
        if item.active and col4.button("Revoke", key=f"revoke_{item.consent_id}", width="stretch"):
            try:
                result = gateway.revoke_consent(account, item.consent_id)
                transaction_success(result)
                st.rerun()
            except Exception as exc:
                error_message(exc)
        st.caption(f"Credential {short_hash(item.credential_hash, 12)}")
        st.divider()
