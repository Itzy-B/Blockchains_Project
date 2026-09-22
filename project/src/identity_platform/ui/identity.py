"""Student identity registration page."""

from __future__ import annotations

import streamlit as st

from ..hashing import hashable_identity, record_hash
from ..models import IdentityRecord, utc_now_iso
from .components import error_message, hero, short_hash, transaction_success


def render(gateway, account: str, store) -> None:
    hero("Digital identity", "Personal details remain in local off chain storage.")
    if gateway.is_registered(account):
        st.success("This wallet has a registered identity.")
        identity_hash = gateway.identity_hash(account)
        st.markdown(f"**On-chain identity hash**  \n`{identity_hash}`")
        local = store.load_identity(account)
        if local:
            with st.expander("View off chain identity record"):
                st.json(local["record"])
        else:
            st.warning("The identity is on-chain, but its local off chain record is unavailable here.")
        return

    st.subheader("Register a student")
    with st.form("identity_form"):
        left, right = st.columns(2)
        name = left.text_input("Full name", placeholder="Alice Student")
        email = right.text_input("Email", placeholder="alice@example.edu")
        student_id = left.text_input("Student ID", placeholder="S-10001")
        university = right.text_input("University", placeholder="Example University")
        programme = st.text_input("Degree / programme", placeholder="BSc Computer Science")
        accepted = st.checkbox("I understand that only a hash is written on-chain.")
        submitted = st.form_submit_button("Register identity", type="primary", width="stretch")

    if submitted:
        if not all(value.strip() for value in (name, email, student_id, university, programme)):
            st.error("Complete every field.")
            return
        if not accepted:
            st.error("Confirm the storage notice before registering.")
            return
        record = IdentityRecord(
            name=name.strip(),
            email=email.strip(),
            student_id=student_id.strip(),
            university=university.strip(),
            programme=programme.strip(),
            owner_address=account,
            created_at=utc_now_iso(),
        )
        data = record.to_dict()
        identity_hash = record_hash(hashable_identity(data))
        try:
            result = gateway.register_identity(account, identity_hash)
            store.save_identity(account, data, identity_hash)
            transaction_success(result)
            st.caption(f"Identity hash: {short_hash(identity_hash, 14)}")
            st.rerun()
        except Exception as exc:
            error_message(exc)
