"""Requester access and immutable audit event page."""

from __future__ import annotations

import streamlit as st

from ..validation import is_bytes32, is_ethereum_address
from .components import error_message, format_time, hero, render_gas_cost, short_hash


def render(gateway, account: str, store) -> None:
    hero("Credential access", "Request access and inspect the immutable audit trail.")
    with st.form("access_data"):
        owner = st.text_input("Student / owner wallet", placeholder="0x…")
        credential_hash = st.text_input("Credential hash", placeholder="0x + 64 hexadecimal characters")
        submitted = st.form_submit_button("Attempt access", type="primary", width="stretch")
    if submitted:
        if not is_ethereum_address(owner):
            st.error("Enter a valid Ethereum owner address.")
            return
        if not is_bytes32(credential_hash):
            st.error("Enter a valid bytes32 credential hash (0x plus 64 hexadecimal characters).")
            return
        try:
            record = gateway.access_data(account, owner, credential_hash)
            if record.granted:
                st.success("ACCESS GRANTED — valid consent was found.")
            else:
                st.error("ACCESS DENIED — no active matching consent exists.")
            st.caption(f"Audit transaction: {short_hash(record.transaction_hash, 12)}")
            render_gas_cost(record.gas_cost)
        except Exception as exc:
            error_message(exc)

    st.subheader("Audit events")
    owner_filter = st.text_input("Filter by owner wallet (optional)", key="audit_filter")
    if owner_filter and not is_ethereum_address(owner_filter):
        st.warning("Enter a complete owner address to filter the audit log.")
        return
    try:
        records = gateway.access_records(owner_filter or None)
    except Exception as exc:
        error_message(exc)
        return
    if not records:
        st.info("No access attempts have been recorded.")
        return
    rows = [
        {
            "Result": "Granted" if row.granted else "Denied",
            "Owner": short_hash(row.owner, 8),
            "Requester": short_hash(row.requester, 8),
            "Credential": short_hash(row.credential_hash, 8),
            "Time": format_time(row.timestamp),
            "Transaction": short_hash(row.transaction_hash, 8),
            "Network fee (ETH)": (
                f"{row.gas_cost.total_fee_eth:.8f}" if row.gas_cost else "Demo mode"
            ),
        }
        for row in records
    ]
    st.dataframe(rows, width="stretch", hide_index=True)
