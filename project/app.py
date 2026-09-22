"""Streamlit entry point for the academic identity platform."""

from __future__ import annotations

import streamlit as st

from src.identity_platform.config import Settings
from src.identity_platform.gateways.demo import DemoGateway, DemoState
from src.identity_platform.gateways.web3_gateway import Web3Gateway
from src.identity_platform.storage import JsonRecordStore
from src.identity_platform.ui import access, consent, credentials, dashboard, identity, rewards
from src.identity_platform.ui.components import apply_theme, render_sidebar_status


st.set_page_config(
    page_title="Credence | Academic Identity",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()

settings = Settings.from_env()
store = JsonRecordStore(settings.data_directory)

if settings.mode == "demo":
    if "demo_state" not in st.session_state:
        st.session_state.demo_state = DemoState.seeded()
    gateway = DemoGateway(st.session_state.demo_state)
else:
    try:
        gateway = Web3Gateway(settings)
    except Exception as exc:  # Keep the UI available when a node is not running.
        st.error(f"Could not connect to the blockchain: {exc}")
        st.info("Set APP_MODE=demo in .env to use the interface without Hardhat.")
        st.stop()

with st.sidebar:
    st.markdown("# CREDENCE")
    st.caption("Student-owned academic credentials")
    st.divider()
    accounts = gateway.accounts()
    if not accounts:
        st.error("No Ethereum accounts are available.")
        st.stop()
    selected_account = st.selectbox(
        "Active wallet",
        accounts,
        format_func=lambda value: gateway.account_label(value),
    )
    page = st.radio(
        "Navigation",
        ["Overview", "Identity", "Credentials", "Consent", "Access & audit", "Rewards"],
        label_visibility="collapsed",
    )
    st.divider()
    render_sidebar_status(gateway, settings.mode)

pages = {
    "Overview": dashboard.render,
    "Identity": identity.render,
    "Credentials": credentials.render,
    "Consent": consent.render,
    "Access & audit": access.render,
    "Rewards": rewards.render,
}
pages[page](gateway=gateway, account=selected_account, store=store)

