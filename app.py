import os
import sys
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mocks'))
from make_mocks import generate_mock_inbox
from processor import process_batch, update_local_db, finalize_and_route, get_all_records

st.set_page_config(page_title="Factory AI Dashboard", layout="wide")
st.title("Factory Ops AI: Batch Router")

tab1, tab2 = st.tabs(["Queue: Scan & Verify", "Audit: Migration Tracking"])

if 'scan_results' not in st.session_state:
    st.session_state.scan_results = []

def inbox_has_docs():
    if not os.path.exists("scanner_inbox"):
        return False
    return any(f.endswith(('.pdf', '.png', '.jpg')) for f in os.listdir("scanner_inbox"))

with tab1:
    if st.button("Scan Scanner_Inbox"):
        if not inbox_has_docs():
            with st.spinner("Inbox empty — generating mock documents..."):
                generate_mock_inbox()
        st.session_state.scan_results = process_batch("scanner_inbox")

    for i, item in enumerate(list(st.session_state.scan_results)):
        file_id = item['file_name'].replace(".", "_")
        with st.expander(f"Document: {item['file_name']}", expanded=True):
            doc_col, form_col = st.columns([1, 1])

            with doc_col:
                if item.get('image'):
                    st.image(item['image'], caption="Scanned Document", use_container_width=True)

            with form_col:
                p_no = st.text_input("Part Number", value=item['part_no'], key=f"p_{file_id}")
                c_id = st.text_input("Cert ID", value=item['cert_id'], key=f"c_{file_id}")
                status = st.selectbox("Quality", ["COMPLIANT", "NON-COMPLIANT"],
                                      index=0 if item['status'] == "COMPLIANT" else 1, key=f"s_{file_id}")

                if st.button("Approve & Migrate to Jira", key=f"btn_{file_id}"):
                    jira_key = update_local_db({"part_no": p_no, "cert_id": c_id, "status": status, "file_name": item['file_name']})
                    finalize_and_route({"part_no": p_no, "cert_id": c_id, "file_name": item['file_name']})
                    st.success(f"Successfully migrated to Jira: {jira_key}")
                    st.session_state.scan_results.pop(i)
                    st.rerun()

with tab2:
    if st.button("Refresh Auditor"):
        df = get_all_records()
        if not df.empty:
            st.dataframe(df, use_container_width=True)
