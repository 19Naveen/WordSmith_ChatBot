import streamlit as st

# ------------- PAGE CONFIG & CSS -------------
st.set_page_config(page_title="RAG Chatbot", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .source-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
        border-left: 3px solid #4c78a8;
    }
    .chat-title {
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .chat-subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .sidebar-title {
        font-weight: bold;
        font-size: 1.3rem;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ------------- SESSION STATE -------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mode" not in st.session_state:
    st.session_state.mode = "RAG"
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "urls" not in st.session_state:
    st.session_state.urls = []

# ------------- SIDEBAR CONTROLS -------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🛠️ Chatbot Configuration</div>", unsafe_allow_html=True)

    # Mode selection
    st.session_state.mode = st.radio("Mode", ["RAG", "URL-QA", "Chatbot"])

    st.divider()

    # RAG mode
    if st.session_state.mode == "RAG":
        st.markdown("📄 **Upload Documents**")
        uploaded_files = st.file_uploader(
            "Drag & drop files or browse",
            accept_multiple_files=True,
            type=["pdf", "txt", "docx"]
        )
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

    # URL-QA mode
    elif st.session_state.mode == "URL-QA":
        st.markdown("🌐 **Add URLs**")
        url_input = st.text_input("Enter a URL and click 'Add'")
        add_url = st.button("➕ Add URL")

        if add_url and url_input:
            if url_input not in st.session_state.urls:
                st.session_state.urls.append(url_input)
                st.success("✅ URL added")
            else:
                st.warning("⚠️ URL already added")

        # Show added URLs
        if st.session_state.urls:
            st.markdown("**🗂️ Your URLs:**")
            for i, url in enumerate(st.session_state.urls):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"{i + 1}. {url}")
                with col2:
                    if st.button("❌", key=f"del_{i}"):
                        st.session_state.urls.pop(i)
                        st.rerun()

    st.divider()

    # Clear history
    if st.button("🧹 Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# ------------- MAIN INTERFACE -------------
st.markdown("<h1 class='chat-title'>🤖 RAG Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<p class='chat-subtitle'>Ask questions and get cited answers</p>", unsafe_allow_html=True)

# Display mode indicator
mode_labels = {"RAG": "📚 Document Q&A", "URL-QA": "🔗 Website Q&A", "Chatbot": "💬 General Chat"}
st.info(f"Current mode: {mode_labels[st.session_state.mode]}")

# ------------- CHAT DISPLAY -------------
chat_container = st.container()
with chat_container:
    for i, chat in enumerate(st.session_state.chat_history):
        if chat["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.write(chat["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(chat["content"])

                # Show sources in expandable view
                if "sources" in chat and chat["sources"]:
                    with st.expander("📚 View Source Documents"):
                        for j, source in enumerate(chat["sources"]):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Source {j+1}:</strong><br/>
                                {source}
                            </div>
                            """, unsafe_allow_html=True)

# ------------- CHAT INPUT -------------
user_question = st.chat_input("Ask a question...")

if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})

    # Simulated backend logic (replace with your actual RAG pipeline)
    if st.session_state.mode == "RAG":
        if not st.session_state.uploaded_files:
            response = "⚠️ Please upload documents in the sidebar first."
            sources = []
        else:
            file_names = [f.name for f in st.session_state.uploaded_files]
            response = f"Based on your documents, here's what I found for **'{user_question}'**:\n\n- ML architectures play a role\n- Practical use cases and datasets cited\n- New research directions emerging"
            sources = [
                f"File: {file_names[0]}, Page 12 - Evidence of neural net depth impact.",
                f"File: {file_names[0]}, Page 23 - Transformer models dominate this use case."
            ]

    elif st.session_state.mode == "URL-QA":
        if not st.session_state.urls:
            response = "⚠️ Please add URLs in the sidebar first."
            sources = []
        else:
            response = f"From your URL(s), I found this regarding **'{user_question}'**:\n\n- Technology began in 2019\n- 3 implementations in production\n- Advances continue rapidly"
            sources = [
                f"URL: {st.session_state.urls[0]} - See 'Intro': early use cases.",
                f"URL: {st.session_state.urls[0]} - See 'Architecture': deep insights."
            ]

    else:
        response = f"Here's what I know about **'{user_question}'**:\n\n- Tied to core AI ideas\n- Applies to multiple industries\n- Latest models simplify deployment"
        sources = []

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "sources": sources
    })

    st.rerun()
