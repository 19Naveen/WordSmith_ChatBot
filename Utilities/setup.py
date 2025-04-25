import os
PDF_PATH = 'PDF'
CHROMA_PATH = 'Chroma'

def create_directory():
    """
    Create a directory for storing PDF files and Vector. If the directory already exists, remove all files in it.
    """
    if os.path.exists(PDF_PATH):
        for file in os.listdir(PDF_PATH):
            Path = os.path.join(PDF_PATH, file)
            os.remove(Path)
        print("Directory Files has been removed successfully")

    if not os.path.exists(PDF_PATH):
        os.mkdir(PDF_PATH)

    if os.path.exists(CHROMA_PATH):
        for file in os.listdir(CHROMA_PATH):
            Path = os.path.join(CHROMA_PATH, file)
            os.remove(CHROMA_PATH)
        print("Directory Files has been removed successfully")

    if not os.path.exists(CHROMA_PATH):
        os.mkdir(CHROMA_PATH)

def process_files(uploaded_files):
    """Simulates processing uploaded files (e.g., chunking, embedding)."""

    def upload_file(file):
    if file is None:
        return "No file provided"
    file_path = os.path.join(PDF_PATH, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

    processed_names = set()
    new_files_processed = False
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.processed_file_names:
                st.write(f"Processing {file.name}...")
                time.sleep(1)
                st.session_state.processed_file_names.add(file.name)
                processed_names.add(file.name)
                new_files_processed = True
        if new_files_processed:
            st.toast(f"✅ Processed files: {', '.join(processed_names)}", icon="📄")
    return new_files_processed



HTML_Template = """
<style>
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
    }
    .chat-title {
        text-align: center;
        color: #2a9df4; /* Example color */
    }
    .chat-subtitle {
        text-align: center;
        color: #555;
        margin-bottom: 2rem;
    }
    .source-box {
        border: 1px solid #e6e6e6;
        padding: 5px;
        padding-bottom:5px;
        border-radius: 5px;
        background-color: grey;
        margin-bottom: 5px;
        font-size: 0.9em;
        color: black;
        white-space: pre-wrap; /* Preserve whitespace and wrap */
        word-wrap: break-word; /* Break long words */
    }
    .stChatInputContainer > div {
        background-color: #f0f2f6; /* Input container background */
    }
    .st-emotion-cache-usj992 { /* Target the main block container */
        border-top: 2px solid #e0e0e0; /* Add a top border to the main content area */
        padding-top: 2rem;
    }
    .st-emotion-cache-1c7y2kd { /* Target Send button specifically if needed */
       /* Add specific styles */
    }
    .sidebar-title {
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* Adjust chat message styling */
    [data-testid="chatAvatarIcon-user"] { /* User avatar */
        background-color: #cceeff; /* Light blue background */
        color: #0056b3; /* Dark blue icon */
    }
    [data-testid="chatAvatarIcon-assistant"] { /* Assistant avatar */
       background-color: #e8e8e8; /* Light gray background */
       color: #333; /* Dark gray icon */
    }

</style>
"""