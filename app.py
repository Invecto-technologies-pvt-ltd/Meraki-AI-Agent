# app.py

import streamlit as st
from meraki_agent import run_meraki_agent, format_result
from meraki_tools import (
    get_organizations,
    get_networks_for_org,
    create_network,
    update_network,
    create_ssid,
    update_ssid
)

# Page config
st.set_page_config(page_title="📡 Meraki AI Assistant", layout="wide")

# Initialize session state for chat history display
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Sidebar: Organization & Network ----------
st.sidebar.header("Organization & Network Selection")
orgs = get_organizations()
org_names = [o["name"] for o in orgs]
selected_org = st.sidebar.selectbox("Organization", org_names)
st.session_state.selected_org_id = next(o["id"] for o in orgs if o["name"] == selected_org)

if st.session_state.selected_org_id:
    nets = get_networks_for_org(st.session_state.selected_org_id)
    net_names = [n["name"] for n in nets]
    selected_net = st.sidebar.selectbox("Network", net_names)
    st.session_state.selected_network_id = next(n["id"] for n in nets if n["name"] == selected_net)

# ---------- Sidebar: Network Management ----------
st.sidebar.header("Network Management")
if st.session_state.selected_org_id:
    # Create Network
    new_net_name = st.sidebar.text_input("New Network Name", key="new_net_name")
    new_net_type = st.sidebar.selectbox(
        "Network Type", ["wireless", "appliance", "switch", "camera"], key="new_net_type"
    )
    if st.sidebar.button("Create Network", key="create_net_btn"):
        net = create_network(
            st.session_state.selected_org_id,
            new_net_name,
            new_net_type
        )
        st.sidebar.success(
            f"Created network: {net.get('name')} (ID: {net.get('id')})"
        )

    # SSID Management
    st.sidebar.subheader("SSID Management")
    if st.session_state.get("selected_network_id"):
        ssid_num = st.sidebar.number_input(
            "SSID Number", min_value=0, max_value=14, value=0, key="ssid_num"
        )
        ssid_name = st.sidebar.text_input("SSID Name", key="ssid_name")
        ssid_enabled = st.sidebar.checkbox("Enabled", value=True, key="ssid_enabled")
        ssid_auth = st.sidebar.selectbox(
            "Auth Mode", ["open", "wpa", "wpa2-enterprise"], key="ssid_auth"
        )
        if st.sidebar.button("Create SSID", key="create_ssid_btn"):
            ssid = create_ssid(
                st.session_state.selected_network_id,
                ssid_num,
                ssid_name,
                ssid_enabled,
                authMode=ssid_auth
            )
            st.sidebar.success(
                f"Created SSID: {ssid.get('name')} (#{ssid.get('number')})"
            )
        # Update SSID
        upd_num = st.sidebar.number_input(
            "Update SSID Number", min_value=0, max_value=14, value=0, key="upd_ssid_num"
        )
        upd_name = st.sidebar.text_input("New SSID Name", key="upd_ssid_name")
        upd_en = st.sidebar.checkbox("Enabled", value=True, key="upd_ssid_enabled")
        if st.sidebar.button("Update SSID", key="update_ssid_btn"):
            upd = update_ssid(
                st.session_state.selected_network_id,
                upd_num,
                name=upd_name,
                enabled=upd_en
            )
            st.sidebar.success(
                f"Updated SSID: {upd.get('name')} (#{upd.get('number')})"
            )
    else:
        st.sidebar.info("Select a network above to manage SSIDs.")

# ---------- Main: Stateless Chatbot ----------
st.markdown("---")
st.header("Chat with Assistant")

# Display previous chat history
for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)

# Chat input
user_input = st.chat_input("Ask something about your Meraki network...")
if user_input:
    # Append user message for display
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"): st.markdown(user_input)

    # Get assistant response without memory context
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                resp = run_meraki_agent(user_input)
                formatted = format_result(resp)
                st.markdown(formatted)
                st.session_state.chat_history.append(("assistant", formatted))
            except Exception as e:
                st.markdown(f"❌ Error: {e}")

