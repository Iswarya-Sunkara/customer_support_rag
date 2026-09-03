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

# Main Chat View
st.markdown('<div class="main-title">🤖 Universal Document Q&A Chatbot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Upload any document format and get instant grounded answers with exact citations.</div>', unsafe_allow_html=True)

# Example Prompt Chips
if docs_summary and len(st.session_state.messages) <= 1:
    st.markdown("**Quick Action Prompts:**")
    prompt_cols = st.columns(3)
    
    if prompt_cols[0].button("💡 Summarize the document"):
        selected_prompt = "Summarize the key information in the uploaded document."
    elif prompt_cols[1].button("🔍 Extract key figures & facts"):
        selected_prompt = "Extract the key figures, dates, and important facts from the document."
    elif prompt_cols[2].button("❓ Find main action items"):
        selected_prompt = "What are the main findings, policies, or action items mentioned?"
    else:
        selected_prompt = None

    if selected_prompt:
        st.session_state.messages.append({"role": "user", "content": selected_prompt})
        with st.spinner("Analyzing document content..."):
            rag_res = st.session_state.rag_engine.query(selected_prompt)
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
user_query = st.chat_input("Ask any question about your uploaded document(s)...")

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
