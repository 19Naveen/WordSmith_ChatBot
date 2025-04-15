import os
import shutil
import streamlit as st
from RAG import word_smith
from RAG import retrieve_info


PDF_PATH = 'PDF'

if os.path.exists(PDF_PATH):
    for file in os.listdir(PDF_PATH):
        Path = os.path.join(PDF_PATH, file)
        os.remove(Path)
    print("Directory Files has been removed successfully")

if not os.path.exists(PDF_PATH):
    os.mkdir(PDF_PATH)

def upload_file(file):
    if file is None:
        return "No file provided"
    file_path = os.path.join(PDF_PATH, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

def initialize_db(file_path):
    if file_path:
        db = word_smith()
        return db
    else:
        return None

def chat_with_bot(user_input, history, db):
    try:
        if db is None:
            return "Database is not initialized. Please upload a PDF first.", history
        response = retrieve_info(db, query=user_input) 
        bot_response = response['result']
        print('metadata:', response['sources'])
        history.append((user_input, bot_response))
        return bot_response, history
    except Exception as e:
        error_message = f"Error processing query: {str(e)}"
        history.append((user_input, error_message))
        return "", history
    


st.title("WORD SMITH")

# Upload PDF Tab
st.header("Upload PDF")
uploaded_file = st.file_uploader("Upload your PDF document here:", type=["pdf"])
if uploaded_file is not None:
    file_path = upload_file(uploaded_file)
    st.session_state.db = initialize_db(file_path)
    st.success("File saved successfully and database initialized.")

# Chatbot 
st.header("Chatbot")
if 'history' not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Enter your question here...", placeholder="Enter your question here...")
if st.button("Submit"):
    if user_input:
        _, st.session_state.history = chat_with_bot(user_input, st.session_state.history, st.session_state.get('db'))

if st.button("Clear"):
    st.session_state.history = []

for user_msg, bot_msg in reversed(st.session_state.history):
    st.write(f"**You:** {user_msg}")
    st.write(f"**Word Smith:** {bot_msg}")
