import streamlit as st
import time 
from Utilities.setup import create_directory, HTML_Template

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

# Store names of processed files to avoid reprocessing
if "processed_file_names" not in st.session_state:
    st.session_state.processed_file_names = set()

# Store processed URLs to avoid reprocessing
if "processed_urls" not in st.session_state:
    st.session_state.processed_urls = set()

# Flag to indicate if processing is needed
if "needs_processing" not in st.session_state:
    st.session_state.needs_processing = False


# ------------- BACKEND FUNCTIONS -------------

def process_urls(urls_to_process):
    """Simulates processing added URLs (e.g., fetching, chunking, embedding)."""
    new_urls_processed = False
    processed_urls_this_run = set()
    if urls_to_process:
        for url in urls_to_process:
             if url not in st.session_state.processed_urls:
                st.write(f"Processing {url}...") # Simulate work
                time.sleep(1) # Simulate processing time
                st.session_state.processed_urls.add(url)
                processed_urls_this_run.add(url)
                new_urls_processed = True
        if new_urls_processed:
             st.toast(f"✅ Processed URLs: {len(processed_urls_this_run)} added", icon="🌐")
    return new_urls_processed


def get_rag_response(question, processed_files):
    """Simulates getting a RAG response based on processed files."""
    if not processed_files:
         return "⚠️ Please upload and process documents first.", []
    # In a real app, query vector store here
    time.sleep(1.5) # Simulate query time
    file_names = list(processed_files) # Use processed names
    response = f"Based on your documents ({', '.join(file_names)}), here's what I found for **'{question}'**:\n\n- Finding 1 from processed documents.\n- Finding 2 related to '{question}'."
    sources = [
        f"Document: {file_names[0]}, Context: Relevant snippet about '{question}'.",
        f"Document: {file_names[-1]}, Context: Another piece of info."
    ] if file_names else []
    return response, sources

def get_url_qa_response(question, processed_urls_list):
    """Simulates getting a response based on processed URLs."""
    if not processed_urls_list:
        return "⚠️ Please add and process URLs first.", []
    # In a real app, query vector store for URLs here
    time.sleep(1.5) # Simulate query time
    response = f"From the processed URLs ({', '.join(list(processed_urls_list)[:2])}...), I found this regarding **'{question}'**:\n\n- Point 1 derived from URL content.\n- Point 2 answering '{question}' based on URLs."
    sources = [
        f"URL: {list(processed_urls_list)[0]}, Context: Key information found on the page.",
        f"URL: {list(processed_urls_list)[-1]}, Context: Supporting details."
    ] if processed_urls_list else []
    return response, sources

def get_web_search_response(question):
    """Simulates getting a response from a web search."""
    # In a real app, call a search API (e.g., Google Search, Bing)
    time.sleep(1.5) # Simulate API call time
    response = f"Based on a web search for **'{question}'**:\n\n- Recent news/finding 1.\n- Common understanding/finding 2."
    sources = [
        f"Web Search Result 1: [Example Title 1](https://example.com/result1) - Snippet...",
        f"Web Search Result 2: [Example Title 2](https://example.com/result2) - Snippet..."
    ]
    # Here you would potentially add Google Search tool usage
    # print(Google Search([question]))
    return response, sources

def get_wiki_response(question):
    """Simulates getting a response from Wikipedia."""
    # In a real app, call the Wikipedia API
    time.sleep(1.5) # Simulate API call time
    response = f"According to Wikipedia regarding **'{question}'**:\n\n- Key fact 1 from Wikipedia.\n- Summary point 2 from Wikipedia."
    sources = [
        f"Wikipedia: [Page about {question}](https://en.wikipedia.org/wiki/...) - Section: Introduction",
        f"Wikipedia: [Page about {question}](https://en.wikipedia.org/wiki/...) - Section: Key Concepts"
    ]

    sources.append(f"Wikipedia: [Page about {question}](https://en.wikipedia.org/wiki/{question}) - Section: Additional Information")

    return response, sources

# ------------- SIDEBAR CONTROLS ------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🛠️ Configuration</div>", unsafe_allow_html=True)

    # --- Mode Selection ---
    selected_mode = st.radio(
        "Choose Interaction Mode:",
        options=["General Chatbot", "Chat with Documents (RAG)", "Chat with URLs", "Web Search", "Wikipedia Search"],
        key="mode_selection", # Use a distinct key
        on_change=lambda: st.session_state.update(mode=st.session_state.mode_selection) # Update main mode state on change
    )
    if st.session_state.mode != st.session_state.mode_selection:
         st.session_state.mode = st.session_state.mode_selection
         st.rerun()
    st.divider()

    # --- Conditional Controls Based on Mode ---
    files_uploaded_now = []
    if st.session_state.mode == "Chat with Documents (RAG)":
        st.markdown("📄 **Upload Documents**")
        files_uploaded_now = st.file_uploader(
            "Add files to chat with",
            accept_multiple_files=True,
            type=["pdf", "txt", "docx"],
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

        # Display uploaded file names (from session state list)
        if st.session_state.uploaded_files_list:
            st.markdown("**Uploaded Files:**")
            for i, file in enumerate(st.session_state.uploaded_files_list):
                col1, col2 = st.columns([5,1])
                with col1:
                    st.write(f"{i+1}. {file.name} ({file.size} bytes)")
                with col2:
                    if st.button("🗑️", key=f"del_file_{i}", help="Remove this file"):
                         # Remove from list and processed set
                         removed_file = st.session_state.uploaded_files_list.pop(i)
                         st.session_state.processed_file_names.discard(removed_file.name)
                         st.toast(f"Removed {removed_file.name}", icon="➖")
                         # If file uploader holds a reference, clear it (might be needed)
                         # st.session_state.file_uploader = [f for f in st.session_state.uploaded_files_list]
                         st.rerun()

            # Add a button to trigger processing
            if st.session_state.needs_processing or any(f.name not in st.session_state.processed_file_names for f in st.session_state.uploaded_files_list):
                 if st.button("⚙️ Process Uploaded Files"):
                     with st.spinner("Processing files..."):
                         process_files(st.session_state.uploaded_files_list)
                     st.session_state.needs_processing = False # Reset flag after processing
                     st.rerun() # Update UI to show processing is done
            elif st.session_state.uploaded_files_list:
                 st.success("✅ All uploaded files processed.")


    elif st.session_state.mode == "Chat with URLs":
        st.markdown("🌐 **Add URLs**")
        url_input = st.text_input("Enter a URL to chat with", key="url_input")
        add_url = st.button("➕ Add URL")

        urls_added_now = False
        if add_url and url_input:
            # Basic validation (optional: add more robust checks)
            if url_input.startswith("http://") or url_input.startswith("https://"):
                if url_input not in st.session_state.urls:
                    st.session_state.urls.append(url_input)
                    st.session_state.needs_processing = True # Flag for processing
                    urls_added_now = True
                    st.success("✅ URL added. Process below.")
                else:
                    st.warning("⚠️ URL already added")
            else:
                st.error("❌ Please enter a valid URL (starting with http:// or https://)")

        # Show added URLs
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

             # Add a button to trigger processing URLs
            if st.session_state.needs_processing or any(url not in st.session_state.processed_urls for url in st.session_state.urls):
                 if st.button("⚙️ Process Added URLs"):
                     with st.spinner("Processing URLs..."):
                         process_urls(st.session_state.urls)
                     st.session_state.needs_processing = False # Reset flag
                     st.rerun()
            elif st.session_state.urls:
                st.success("✅ All added URLs processed.")

        # Rerun if a URL was just added to update the display immediately
        if urls_added_now:
            st.rerun()


    st.divider()

    # --- Clear History Button ---
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.toast("Chat history cleared!", icon="🧹")
        st.rerun()

    # --- Clear Data Sources ---
    if st.button("🧹 Clear All Data Sources"):
        st.session_state.uploaded_files_list = []
        st.session_state.processed_file_names = set()
        st.session_state.urls = []
        st.session_state.processed_urls = set()
        st.session_state.needs_processing = False
        # Optionally clear the file uploader state if it persists
        if "file_uploader" in st.session_state:
             st.session_state.file_uploader = []
        st.toast("All documents and URLs cleared!", icon="💥")
        st.rerun()


# ------------- MAIN INTERFACE -------------
st.markdown("<h1 class='chat-title'>💬 WordSmith Chatbot</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='chat-subtitle'>Interacting via: <strong>{st.session_state.mode}</strong></p>", unsafe_allow_html=True)


# ------------- CHAT DISPLAY -------------
# Use a container for chat messages for better layout control potentially
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
                        <div class="source-box">
                           <strong>Source {j+1}:</strong><br/>
                           {source}
                        </div>
                        """, unsafe_allow_html=True)


# ------------- CHAT INPUT -------------

# Use st.chat_input for a more standard chat UI
user_question = st.chat_input("Ask anything...", key="user_input")

if user_question:
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": user_question})

    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.write(user_question)

    # Get assistant response based on mode
    response = "Sorry, something went wrong." # Default error
    sources = []
    mode = st.session_state.mode # Get current mode

    # Simulate thinking and call the appropriate backend function
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            if mode == "Chat with Documents (RAG)":
                # Ensure files are processed before attempting RAG
                if not st.session_state.processed_file_names and st.session_state.uploaded_files_list:
                     response = "⚠️ Please process the uploaded documents using the 'Process Uploaded Files' button in the sidebar before asking questions."
                     sources = []
                elif not st.session_state.uploaded_files_list:
                    response = "⚠️ Please upload documents in the sidebar to use RAG mode."
                    sources = []
                else:
                     response, sources = get_rag_response(user_question, st.session_state.processed_file_names)

            elif mode == "Chat with URLs":
                 # Ensure URLs are processed
                 if not st.session_state.processed_urls and st.session_state.urls:
                      response = "⚠️ Please process the added URLs using the 'Process Added URLs' button in the sidebar before asking questions."
                      sources = []
                 elif not st.session_state.urls:
                     response = "⚠️ Please add URLs in the sidebar to use URL chat mode."
                     sources = []
                 else:
                      response, sources = get_url_qa_response(user_question, st.session_state.processed_urls)

            elif mode == "Web Search":
                response, sources = get_web_search_response(user_question)

            elif mode == "Wikipedia Search":
                response, sources = get_wiki_response(user_question)

            else: # Fallback / General Chat (if you add such a mode)
                 response = f"Thinking generally about **'{user_question}'**:\n\n- Standard answer point 1.\n- Standard answer point 2."
                 sources = [] # No specific sources for general chat

        # Display assistant response
        st.write(response)
        # Display sources if available
        if sources:
            with st.expander("📚 Sources"):
                for j, source in enumerate(sources):
                   st.markdown(f"""
                   <div class="source-box">
                       <strong>Source {j+1}:</strong><br/>
                       {source}
                   </div>
                   """, unsafe_allow_html=True)


    # Add assistant response to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "sources": sources
    })

    