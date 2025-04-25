import streamlit as st
import time
from Utilities.setup import create_directory, HTML_Template
from Agents.RAG import document_RAG
from Agents.URL import url_RAG
from Agents.Wiki import create_wiki_db
from Agents.chat_interface import chat_with_llm
from Utilities.Tools import chat_with_bot

create_directory()
st.set_page_config(page_title="WordSmith Chatbot", layout="wide", initial_sidebar_state="expanded")
st.markdown(HTML_Template, unsafe_allow_html=True)

# ------------- SESSION STATE INITIALIZATION -------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "mode" not in st.session_state:
    st.session_state.mode = "Chat with Documents (RAG)"
if "uploaded_files_list" not in st.session_state:
    st.session_state.uploaded_files_list = []
if "urls" not in st.session_state:
    st.session_state.urls = []
if "processed_file_names" not in st.session_state:
    st.session_state.processed_file_names = set()
if "processed_urls" not in st.session_state:
    st.session_state.processed_urls = set()
if "needs_processing" not in st.session_state:
    st.session_state.needs_processing = False
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None
if "wiki_topic" not in st.session_state:
    st.session_state.wiki_topic = ""

# ------------- SIDEBAR CONTROLS -------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🛠️ Configuration</div>", unsafe_allow_html=True)
    selected_mode = st.radio(
        "Choose Interaction Mode:",
        options=["General Chatbot", "Chat with Documents (RAG)", "Chat with URLs", "Wikipedia Search"],
        key="mode_selection",
        on_change=lambda: st.session_state.update(mode=st.session_state.mode_selection)
    )
    if st.session_state.mode != st.session_state.mode_selection:
        st.session_state.mode = st.session_state.mode_selection
        st.rerun()
    st.divider()
    files_uploaded_now = []
    if st.session_state.mode == "Chat with Documents (RAG)":
        st.markdown("📄 **Upload Documents**")
        files_uploaded_now = st.file_uploader(
            "Add files to chat with",
            accept_multiple_files=True,
            type=["pdf"],
            key="file_uploader"
        )
        if files_uploaded_now:
            current_file_ids = {f"{f.name}_{f.size}" for f in st.session_state.uploaded_files_list}
            new_files_added = False
            for file in files_uploaded_now:
                file_id = f"{file.name}_{file.size}"
                if file_id not in current_file_ids:
                    st.session_state.uploaded_files_list.append(file)
                    new_files_added = True
            if new_files_added:
                st.session_state.needs_processing = True
                st.success(f"✅ {len(files_uploaded_now)} file(s) ready. Process below.")
                st.rerun()
        if st.session_state.uploaded_files_list:
            st.markdown("**Uploaded Files:**")
            for i, file in enumerate(st.session_state.uploaded_files_list):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"{i+1}. {file.name} ({file.size} bytes)")
                with col2:
                    if st.button("🗑️", key=f"del_file_{i}", help="Remove this file"):
                        removed_file = st.session_state.uploaded_files_list.pop(i)
                        st.session_state.processed_file_names.discard(removed_file.name)
                        st.toast(f"Removed {removed_file.name}", icon="➖")
                        st.rerun()
            if st.session_state.needs_processing or any(f.name not in st.session_state.processed_file_names for f in st.session_state.uploaded_files_list):
                if st.button("⚙️ Process Uploaded Files"):
                    with st.spinner("Processing files and building vector DB..."):
                        # Save files to PDF/ directory
                        for file in st.session_state.uploaded_files_list:
                            file_path = f"PDF/{file.name}"
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            st.session_state.processed_file_names.add(file.name)
                        st.session_state.vector_db = document_RAG()
                    st.session_state.needs_processing = False
                    st.success("✅ PDF files processed and vector DB ready.")
                    st.rerun()
            elif st.session_state.uploaded_files_list:
                st.success("✅ All uploaded files processed.")
    elif st.session_state.mode == "Chat with URLs":
        st.markdown("🌐 **Add URLs**")
        url_input = st.text_input("Enter a URL to chat with", key="url_input")
        add_url = st.button("➕ Add URL")
        urls_added_now = False
        if add_url and url_input:
            if url_input.startswith("http://") or url_input.startswith("https://"):
                if url_input not in st.session_state.urls:
                    st.session_state.urls.append(url_input)
                    st.session_state.needs_processing = True
                    urls_added_now = True
                    st.success("✅ URL added. Process below.")
                else:
                    st.warning("⚠️ URL already added")
            else:
                st.error("❌ Please enter a valid URL (starting with http:// or https://)")
        if st.session_state.urls:
            st.markdown("**🔗 Added URLs:**")
            for i, url in enumerate(st.session_state.urls):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"{i + 1}. {url}")
                with col2:
                    if st.button("❌", key=f"del_url_{i}", help="Remove this URL"):
                        removed_url = st.session_state.urls.pop(i)
                        st.session_state.processed_urls.discard(removed_url)
                        st.toast(f"Removed {removed_url}", icon="➖")
                        st.rerun()
            if st.session_state.needs_processing or any(url not in st.session_state.processed_urls for url in st.session_state.urls):
                if st.button("⚙️ Process Added URLs"):
                    with st.spinner("Processing URLs and building vector DB..."):
                        # Only process the first URL for demo; extend as needed
                        url = st.session_state.urls[-1]
                        st.session_state.vector_db = url_RAG(url)
                        st.session_state.processed_urls.add(url)
                    st.session_state.needs_processing = False
                    st.success("✅ URLs processed and vector DB ready.")
                    st.rerun()
            elif st.session_state.urls:
                st.success("✅ All added URLs processed.")
        if urls_added_now:
            st.rerun()
    elif st.session_state.mode == "Wikipedia Search":
        st.markdown("📚 **Wikipedia Topic**")
        wiki_topic = st.text_input("Enter a Wikipedia topic to chat with", key="wiki_topic_input")
        if wiki_topic and wiki_topic != st.session_state.wiki_topic:
            st.session_state.wiki_topic = wiki_topic
            st.session_state.needs_processing = True
        if st.session_state.wiki_topic:
            if st.session_state.needs_processing:
                if st.button("⚙️ Process Wikipedia Topic"):
                    with st.spinner("Processing Wikipedia content and building vector DB..."):
                        st.session_state.vector_db = create_wiki_db(st.session_state.wiki_topic)
                    st.session_state.needs_processing = False
                    st.success("✅ Wikipedia topic processed and vector DB ready.")
                    st.rerun()
            else:
                st.success(f"✅ Wikipedia topic '{st.session_state.wiki_topic}' processed.")
    st.divider()
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.toast("Chat history cleared!", icon="🧹")
        st.rerun()
    if st.button("🧹 Clear All Data Sources"):
        st.session_state.uploaded_files_list = []
        st.session_state.processed_file_names = set()
        st.session_state.urls = []
        st.session_state.processed_urls = set()
        st.session_state.vector_db = None
        st.session_state.wiki_topic = ""
        st.session_state.needs_processing = False
        if "file_uploader" in st.session_state:
            st.session_state.file_uploader = []
        st.toast("All documents and URLs cleared!", icon="💥")
        st.rerun()

# ------------- MAIN INTERFACE -------------
st.markdown("<h1 class='chat-title'>💬 WordSmith Chatbot</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='chat-subtitle'>Interacting via: <strong>{st.session_state.mode}</strong></p>", unsafe_allow_html=True)

# ------------- CHAT DISPLAY -------------
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        st.info("Starting a new chat. Ask me anything!")
    for i, chat in enumerate(st.session_state.chat_history):
        role = chat["role"]
        avatar = "👤" if role == "user" else "🤖"
        with st.chat_message(role, avatar=avatar):
            st.write(chat["content"])
            if role == "assistant" and "sources" in chat and chat["sources"]:
                with st.expander("📚 Sources"):
                    for j, source in enumerate(chat["sources"]):
                        st.markdown(f"""
                        <div class=\"source-box\">
                           <strong>Source {j+1}:</strong><br/>
                           {source}
                        </div>
                        """, unsafe_allow_html=True)

# ------------- CHAT INPUT -------------
user_question = st.chat_input("Ask anything...", key="user_input")

if user_question:
    st.session_state.chat_history.append({"role": "user", "content": user_question})
    with st.chat_message("user", avatar="👤"):
        st.write(user_question)
    response = "Sorry, something went wrong."
    sources = []
    mode = st.session_state.mode
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            if mode == "Chat with Documents (RAG)":
                if not st.session_state.vector_db:
                    response = "⚠️ Please process the uploaded documents using the 'Process Uploaded Files' button in the sidebar before asking questions."
                else:
                    response, _ = chat_with_bot(user_question, [], st.session_state.vector_db)
            elif mode == "Chat with URLs":
                if not st.session_state.vector_db:
                    response = "⚠️ Please process the added URLs using the 'Process Added URLs' button in the sidebar before asking questions."
                else:
                    response, _ = chat_with_bot(user_question, [], st.session_state.vector_db)
            elif mode == "Wikipedia Search":
                if not st.session_state.vector_db:
                    response = "⚠️ Please process the Wikipedia topic using the 'Process Wikipedia Topic' button in the sidebar before asking questions."
                else:
                    response, _ = chat_with_bot(user_question, [], st.session_state.vector_db)
            else:
                response = chat_with_llm(user_question)
        st.write(response)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "sources": sources
    })
