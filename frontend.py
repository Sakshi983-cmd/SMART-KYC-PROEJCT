import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="GrackerKYC AI Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE = st.secrets.get("API_BASE", "http://127.0.0.1:8000/api/v1")

def make_request(endpoint, method="GET", data=None):
    try:
        url = f"{API_BASE}/{endpoint}"
        response = requests.get(url) if method == "GET" else requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Backend returned status {response.status_code} for '{endpoint}'")
            return None
    except requests.exceptions.ConnectionError:
        st.error(f"🔴 Could not connect to backend at {API_BASE}. Is it running?")
        return None

def main():
    st.markdown('<h1 class="main-header">GrackerKYC AI Platform</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enterprise-Grade KYC Verification with AI & Blockchain</p>', unsafe_allow_html=True)

    test = make_request("verifications")
    if test is None:
        st.warning("Backend API not running. Start with: python backend.py")
        return

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Verify KYC", "📊 Dashboard", "⛓️ Blockchain", "📈 Analytics"])

    with tab1:
        st.header("AI-Powered KYC Verification")
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.form("kyc_form"):
                st.subheader("User Information")
                name = st.text_input("Full Name *")
                email = st.text_input("Email Address *")
                st.subheader("Document Details")
                doc_type = st.selectbox("Document Type *", ["Passport", "National ID", "Driver's License", "Aadhaar Card", "PAN Card"])
                doc_text = st.text_area("Document Information *", height=200)

                if st.form_submit_button("🚀 Start AI Verification"):
                    if all([name, email, doc_text]):
                        with st.spinner("AI is analyzing document..."):
                            result = make_request("verify", "POST", {
                                "name": name, "email": email,
                                "document_text": doc_text, "document_type": doc_type
                            })
                            if result is None:
                                st.error("❌ No response from backend.")
                            elif not result.get("success"):
                                st.error(f"Verification failed: {result.get('message', 'Unknown error')}")
                            else:
                                st.session_state.last_result = result
                                st.success("✅ Verification Complete!")
                    else:
                        st.warning("Please fill all fields")

        with col2:
            if 'last_result' in st.session_state:
                result = st.session_state.last_result
                ai_data = result.get("ai_analysis") or {}
                status = result.get("status", "UNKNOWN")
                status_color = "approved" if status == "APPROVED" else "review" if status == "UNDER_REVIEW" else "rejected"
                st.markdown(f'<div class="metric-card {status_color}">', unsafe_allow_html=True)
                st.metric("Verification Status", status, f"{result.get('confidence_score', 0)}% Confidence")
                st.markdown('</div>', unsafe_allow_html=True)

                st.subheader("🤖 AI Analysis Results")
                extraction = ai_data.get("extraction") or {}
                validation = ai_data.get("validation") or {}
                risk_analysis = ai_data.get("risk_analysis") or {}

                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Extracted Data:**")
                    st.write(f"Name: {extraction.get('full_name', 'N/A')}")
                    st.write(f"DOB: {extraction.get('dob', 'N/A')}")
                    st.write(f"Doc No: {extraction.get('doc_number', 'N/A')}")
                with col_b:
                    st.write("**Validation:**")
                    st.write(f"Name Match: {validation.get('name_match', 'N/A')}")
                    st.write(f"Expiry: {validation.get('expiry_status', 'N/A')}")
                    st.write(f"Risk: {risk_analysis.get('risk_level', 'N/A')}")

                st.subheader("⛓️ Blockchain Verification")
                st.markdown('<div class="blockchain-animation">'
                            '<div class="block"></div><div class="block"></div>'
                            '<div class="block"></div><div class="block"></div>'
                            '</div>', unsafe_allow_html=True)
                st.write(f"Block Hash: `{result.get('blockchain_hash', '')[:30]}...`")
                st.write(f"Block Index: #{result.get('blockchain_index', 0)}")
            else:
                st.info("No recent verification found.")

    with tab2:
        st.header("Verifications Dashboard")
        verifications = make_request("verifications")
        if verifications:
            df = pd.DataFrame(verifications.get("verifications", []))
            if not df.empty:
                st.dataframe(df[['name', 'email', 'status', 'timestamp', 'ai_confidence']])
                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Approved", len(df[df['status'] == 'APPROVED']))
                with col2: st.metric("Under Review", len(df[df['status'] == 'UNDER_REVIEW']))
                with col3: st.metric("Rejected", len(df[df['status'] == 'REJECTED']))
                with col4: st.metric("Total", len(df))

    with tab3:
        st.header("Blockchain Explorer")
        blockchain_data = make_request("blockchain")
        if blockchain_data:
            st.write(f"Blockchain Length: {blockchain_data.get('length', 0)}")
            for block in blockchain_data.get('blockchain', [])[-10:]:
                with st.expander(f"Block #{block['index']} - {block['hash'][:20]}..."):
                    st.json(block)

    with tab4:
        st.header("AI Analytics")
        verifications = make_request("verifications")
        if verifications:
            df = pd.DataFrame(verifications.get("verifications", []))
            if not df.empty and 'ai_confidence' in df.columns:
                fig = px.histogram(df, x='ai_confidence', title='AI Confidence Distribution')
                st.plotly_chart(fig)
                status_counts = df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, title='Verification Status Distribution')
                st.plotly_chart(fig)
            else:
                st.info("No data available for analytics.")

if __name__ == "__main__":
    main()
