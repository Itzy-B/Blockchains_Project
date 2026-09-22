"""Academic credential registration page."""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from ..hashing import hashable_credential, record_hash
from ..models import CredentialRecord, utc_now_iso
from .components import error_message, hero, short_hash, transaction_success


def render(gateway, account: str, store) -> None:
    hero("Academic credentials", "The complete credential stays off chain; its fingerprint is immutable.")
    if not gateway.is_registered(account):
        st.warning("Register this wallet on the Identity page first.")
        return

    with st.expander("Add a credential", expanded=True):
        with st.form("credential_form"):
            col1, col2 = st.columns(2)
            credential_id = col1.text_input("Credential ID", placeholder="DEG-2026-001")
            student_id = col2.text_input("Student ID", placeholder="S-10001")
            university = col1.text_input("University", placeholder="Example University")
            degree = col2.text_input("Degree", placeholder="BSc Computer Science")
            current_year = datetime.now(timezone.utc).year
            graduation_year = col1.number_input(
                "Graduation year", min_value=1950, max_value=current_year + 10, value=current_year
            )
            classification = col2.text_input("Grade / classification", placeholder="First Class")
            issuer = st.text_input("Credential issuer", placeholder="Registrar's Office")
            submitted = st.form_submit_button("Register credential", type="primary", width="stretch")

        if submitted:
            if not all(
                value.strip()
                for value in (credential_id, student_id, university, degree, classification, issuer)
            ):
                st.error("Complete every field.")
            else:
                record = CredentialRecord(
                    credential_id=credential_id.strip(),
                    student_id=student_id.strip(),
                    university=university.strip(),
                    degree=degree.strip(),
                    graduation_year=int(graduation_year),
                    classification=classification.strip(),
                    issuer=issuer.strip(),
                    owner_address=account,
                    created_at=utc_now_iso(),
                )
                data = record.to_dict()
                credential_hash = record_hash(hashable_credential(data))
                try:
                    result = gateway.add_credential(account, credential_hash)
                    store.save_credential(account, data, credential_hash)
                    transaction_success(result)
                    st.rerun()
                except Exception as exc:
                    error_message(exc)

    st.subheader("Registered credentials")
    on_chain = set(gateway.credential_hashes(account))
    local_records = store.list_credentials(account)
    if not on_chain:
        st.info("No credentials registered yet.")
        return
    local_by_hash = {item["credential_hash"]: item["record"] for item in local_records}
    for index, credential_hash in enumerate(on_chain, start=1):
        record = local_by_hash.get(credential_hash)
        title = record["degree"] if record else f"Credential {index}"
        with st.expander(f"{title} · {short_hash(credential_hash)}"):
            st.code(credential_hash)
            if record:
                st.json(record)
            else:
                st.caption("The off-chain record is not stored on this computer.")
