import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import ask, pre_visit_brief, churn_risk_check

st.set_page_config(page_title="Sales Intelligence Agent", layout="wide")
st.title("Sales Intelligence Agent")

@st.cache_resource
def initialize_rag():
    from rag.ingest import ingest
    ingest()

initialize_rag()

tab1, tab2, tab3 = st.tabs(["Ask Agent", "Pre-Visit Brief", "Churn Risk"])

with tab1:
    cust_cd = st.text_input("Customer Code", placeholder="e.g. CT0000000050", key="ask_cust_cd")
    query   = st.text_area("Your Question", placeholder="e.g. What is this customer's credit status?")
    if st.button("Ask"):
        if cust_cd and query:
            with st.spinner("Thinking..."):
                result = ask(cust_cd=cust_cd, query=query)
                st.markdown(result)
        else:
            st.warning("Enter both a customer code and a question.")

with tab2:
    cust_cd_brief = st.text_input("Customer Code", placeholder="e.g. CT0000000050", key="brief_cust_cd")
    if st.button("Generate Brief"):
        if cust_cd_brief:
            with st.spinner("Generating brief..."):
                result = pre_visit_brief(cust_cd=cust_cd_brief)
                st.markdown(result)
        else:
            st.warning("Enter a customer code.")

with tab3:
    cust_cd_churn = st.text_input("Customer Code", placeholder="e.g. CT0000000001", key="churn_cust_cd")
    if st.button("Check Risk"):
        if cust_cd_churn:
            with st.spinner("Checking churn risk..."):
                result = churn_risk_check(cust_cd=cust_cd_churn)
                st.markdown(result)
        else:
            st.warning("Enter a customer code.")