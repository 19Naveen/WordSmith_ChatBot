import os
import shutil
import streamlit as st
from Agents.RAG import word_smith
from Agents.RAG import retrieve_info

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
