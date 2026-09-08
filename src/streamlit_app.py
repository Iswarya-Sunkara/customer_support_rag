import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_DIR))

from src.dynamic_rag import DynamicRAGEngine

# Page Configuration
st.set_page_config(
    page_title="Universal Doc Q&A Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Glassmorphic UI)
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
    }
    
    /* Header Gradient */
    .main-title {
        background: linear-gradient(135deg, #06B6D4 0%, #8B5CF6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    /* Cards & Containers */
    div[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1F2937;
    }
    
    .doc-card {
        background: rgba(31, 41, 55, 0.6);
        border: 1px solid rgba(75, 85, 99, 0.4);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
        backdrop-filter: blur(8px);
    }
    
    .citation-card {
        background: rgba(17, 24, 39, 0.8);
        border-left: 3px solid #06B6D4;
        border-radius: 6px;
        padding: 10px 14px;
        margin-top: 8px;
        font-size: 0.9rem;
        color: #D1D5DB;
    }

    .badge-cyan {
        background-color: rgba(6, 182, 212, 0.2);
        color: #38BDF8;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Chat Messages */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = DynamicRAGEngine()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! Upload any document in the sidebar (PDF, DOCX, CSV, Excel, TXT, Code, Images, Binaries) and ask me any question about it!", "citations": []}
    ]

# Sidebar — Document Upload & Status
with st.sidebar:
    st.markdown("### 📁 Document Manager")
    st.caption("Upload files without extension restrictions")

    uploaded_files = st.file_uploader(
        "Choose file(s)",
        type=None,  # Accepts ALL file extensions!
        accept_multiple_files=True,
        help="Upload PDF, DOCX, CSV, Excel, TXT, MD, Code, Images, or raw binary files."
    )

    if uploaded_files:
        for ufile in uploaded_files:
            # Check if already processed
            already_indexed = ufile.name in st.session_state.rag_engine.indexed_documents
            if not already_indexed:
                with st.spinner(f"Ingesting & indexing `{ufile.name}`..."):
                    file_bytes = ufile.read()
                    res = st.session_state.rag_engine.add_document(ufile.name, file_bytes)
                    if res["status"] == "success":
                        st.toast(f"✅ `{ufile.name}` indexed ({res['chunks_added']} chunks)", icon="🎉")

    # Document Corpus Metrics
    docs_summary = st.session_state.rag_engine.get_documents_summary()
    st.markdown("---")
    
    # ALWAYS VISIBLE: Ranked Failure Taxonomy Table in Sidebar!
    with st.expander("📊 Ranked Failure Taxonomy Table (Week 5)", expanded=True):
        st.markdown("""
        | Failure Mode Name | Count | Freq % |
        |---|:---:|:---:|
        | **Quotes superseded billing grace period** | 6 | **30.0%** |
        | **Confuses decline code 51 with timeout** | 5 | **25.0%** |
        | **Omits 2FA backup recovery step** | 4 | **20.0%** |
        | **Omits Cardholder Name format rule** | 3 | **15.0%** |
        | **Hallucinates refund SLA on ticket** | 2 | **10.0%** |
        """)
        st.caption("Top Fix Target: Mode #1 (30.0% frequency)")

    st.markdown("---")
    st.markdown("#### 📊 Active Knowledge Base")
    
    if docs_summary:
        col1, col2 = st.columns(2)
        col1.metric("Documents", len(docs_summary))
        col2.metric("Total Chunks", st.session_state.rag_engine.total_chunks)

        st.markdown("**Uploaded Files:**")
        for d in docs_summary:
            st.markdown(
                f"""
                <div class="doc-card">
                    <strong>📄 {d['filename']}</strong> <span class="badge-cyan">{d['extension'].upper()}</span><br/>
                    <small style="color:#9CA3AF;">{d['chunks_count']} chunks | {round(d['size_bytes']/1024, 1)} KB</small>
                </div>
                """,
                unsafe_allow_html=True
            )

        if st.button("🗑️ Clear All Documents", use_container_width=True):
            st.session_state.rag_engine.clear_documents()
            st.session_state.messages = [
                {"role": "assistant", "content": "Knowledge base cleared. Upload a document to start again!", "citations": []}
            ]
            st.rerun()
    else:
        st.info("No documents uploaded yet. Drop any file above!")

# Main Layout with Tabs
tab1, tab2 = st.tabs(["💬 Customer Support Chatbot", "📊 Week 5 Error Taxonomy & 10 Framed Questions"])

with tab2:
    st.markdown("### 📊 Week 5 Practical — Ranked Failure Taxonomy Table")
    st.caption("Domain: Customer Support Tickets | Seeded Random Sample: SEED = 42 | 20 Traces Analyzed")
    
    st.markdown("""
    | Failure Mode Name | Count | Freq % | Severity | Example Trace ID |
    |---|:---:|:---:|---|:---:|
    | **Quotes superseded billing grace period window** | 6 | 30.0% | Embarrasses client | `tr_0026` |
    | **Confuses card decline error code 51 with system timeout** | 5 | 25.0% | Annoys user | `tr_0031` |
    | **Omits primary authentication fallback step for 2FA recovery** | 4 | 20.0% | Embarrasses client | `tr_0033` |
    | **Omits mandatory field formatting rule for special characters in Cardholder Name** | 3 | 15.0% | Annoys user | `tr_0090` |
    | **Hallucinates guaranteed SLA refund window on unanswerable billing ticket** | 2 | 10.0% | Embarrasses client | `tr_0096` |
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 10 Framed Failure-Inducing Questions")
    st.info("Click any question below to test it live in the Chatbot tab and inspect the failure mode output.")

    framed_test_questions = [
        {"id": "FQ01", "q": "If my automatic subscription payment fails on day 1, when is the next retry attempt made and how long is the grace period?", "mode": "Quotes superseded billing grace period window"},
        {"id": "FQ02", "q": "What should I do if I get credit card error code 51 - Decline when paying my invoice?", "mode": "Confuses card decline error code 51 with system timeout"},
        {"id": "FQ03", "q": "How long does Google account recovery take if I lost my security key and have no backup second step?", "mode": "Omits primary authentication fallback step for 2FA recovery"},
        {"id": "FQ04", "q": "What format requirements apply to the Cardholder name and Postal Code fields when resubmitting a failed card?", "mode": "Omits mandatory field formatting rule for special characters in Cardholder Name"},
        {"id": "FQ05", "q": "What is the exact SLA guaranteed refund window in business days for annual plan chargebacks?", "mode": "Hallucinates guaranteed SLA refund window on unanswerable billing ticket"},
        {"id": "FQ06", "q": "How many times and over how many days will Cloudflare retry a failed recurring subscription renewal payment?", "mode": "Quotes superseded billing grace period window"},
        {"id": "FQ07", "q": "How should I resolve credit card error code 14 - Card No. Error when saving my payment details?", "mode": "Confuses card decline error code 51 with system timeout"},
        {"id": "FQ08", "q": "What does Zendesk payment error code 430357 - Lost or Stolen Card mean and how do I fix it?", "mode": "Confuses card decline error code 51 with system timeout"},
        {"id": "FQ09", "q": "What steps must I follow if I lost my security key and need to regain access to my account immediately?", "mode": "Omits primary authentication fallback step for 2FA recovery"},
        {"id": "FQ10", "q": "Can I use accented characters or hyphenated names in the Cardholder Name field when updating my billing info?", "mode": "Omits mandatory field formatting rule for special characters in Cardholder Name"}
    ]

    for item in framed_test_questions:
        with st.expander(f"📌 [{item['id']}] {item['q']}"):
            st.markdown(f"**Mapped Error Taxonomy Failure Mode:** `{item['mode']}`")

with tab1:
    st.info("💡 **Looking for the Ranked Failure Taxonomy Table?** Check the **left Sidebar** under `📊 Ranked Failure Taxonomy Table` or click the **`📊 Week 5 Error Taxonomy & 10 Framed Questions`** tab at the top!")
    
    # Langfuse Status Indicator
    st.success("🟢 **Langfuse Telemetry Active:** Automatically streaming all query traces live to `https://us.cloud.langfuse.com`")
    
    st.markdown('<div class="main-title">🤖 Universal Support RAG Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Week 5 Error Analysis & Customer Support Ticket Q&A Engine</div>', unsafe_allow_html=True)



    # 10 Framed Question Quick Selection Buttons
    st.markdown("#### 🎯 Quick Test — 10 Framed Failure Questions:")
    
    selected_framed_question = None
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("1️⃣ FQ01: Subscription Retry Schedule", use_container_width=True):
            selected_framed_question = "If my automatic subscription payment fails on day 1, when is the next retry attempt made and how long is the grace period?"
        if st.button("2️⃣ FQ02: Card Decline Error Code 51", use_container_width=True):
            selected_framed_question = "What should I do if I get credit card error code 51 - Decline when paying my invoice?"
        if st.button("3️⃣ FQ03: Google 2FA Security Key Lost", use_container_width=True):
            selected_framed_question = "How long does Google account recovery take if I lost my security key and have no backup second step?"
        if st.button("4️⃣ FQ04: Cardholder Name Special Chars", use_container_width=True):
            selected_framed_question = "What format requirements apply to the Cardholder name and Postal Code fields when resubmitting a failed card?"
        if st.button("5️⃣ FQ05: Annual Plan Chargeback SLA", use_container_width=True):
            selected_framed_question = "What is the exact SLA guaranteed refund window in business days for annual plan chargebacks?"

    with col_b:
        if st.button("6️⃣ FQ06: Cloudflare Subscription Retries", use_container_width=True):
            selected_framed_question = "How many times and over how many days will Cloudflare retry a failed recurring subscription renewal payment?"
        if st.button("7️⃣ FQ07: Payment Error Code 14", use_container_width=True):
            selected_framed_question = "How should I resolve credit card error code 14 - Card No. Error when saving my payment details?"
        if st.button("8️⃣ FQ08: Lost/Stolen Card Code 430357", use_container_width=True):
            selected_framed_question = "What does Zendesk payment error code 430357 - Lost or Stolen Card mean and how do I fix it?"
        if st.button("9️⃣ FQ09: Emergency 2FA Account Access", use_container_width=True):
            selected_framed_question = "What steps must I follow if I lost my security key and need to regain access to my account immediately?"
        if st.button("🔟 FQ10: Accented Cardholder Names", use_container_width=True):
            selected_framed_question = "Can I use accented characters or hyphenated names in the Cardholder Name field when updating my billing info?"

    st.markdown("---")

    if selected_framed_question:
        st.session_state.messages.append({"role": "user", "content": selected_framed_question})
        with st.spinner("Executing query through Week 5 RAG Engine..."):
            rag_res = st.session_state.rag_engine.query(selected_framed_question)
            st.session_state.messages.append({
                "role": "assistant",
                "content": rag_res["answer"],
                "citations": rag_res["citations"]
            })
        st.rerun()

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("citations"):
                with st.expander("📌 View Source Citations & Document Snippets"):
                    for cit in msg["citations"]:
                        st.markdown(
                            f"""
                            <div class="citation-card">
                                <strong>📄 File:</strong> {cit['filename']} | <strong>ID:</strong> <code>{cit['chunk_id']}</code> | <strong>Relevance:</strong> <span style="color:#38BDF8;">{cit['similarity_score']}</span><br/>
                                <em style="color:#9CA3AF;">"{cit['snippet']}"</em>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    # Chat Input Box
    user_query = st.chat_input("Ask any question or click a Framed Question button above...")

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Searching document context..."):
                rag_res = st.session_state.rag_engine.query(user_query)
                st.markdown(rag_res["answer"])

                if rag_res["citations"]:
                    with st.expander("📌 View Source Citations & Document Snippets"):
                        for cit in rag_res["citations"]:
                            st.markdown(
                                f"""
                                <div class="citation-card">
                                    <strong>📄 File:</strong> {cit['filename']} | <strong>ID:</strong> <code>{cit['chunk_id']}</code> | <strong>Relevance:</strong> <span style="color:#38BDF8;">{cit['similarity_score']}</span><br/>
                                    <em style="color:#9CA3AF;">"{cit['snippet']}"</em>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": rag_res["answer"],
                    "citations": rag_res["citations"]
                })

