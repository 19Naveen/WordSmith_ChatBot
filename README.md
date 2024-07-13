# Word Smith - RAG-Based ChatBot

Word Smith is an intelligent chatbot powered by Retrieval-Augmented Generation (RAG) technology. It allows users to upload PDF documents and engage in conversations based on the content of those documents.

## Features

- PDF document upload and processing
- Conversational interface for querying document content
- RAG-based information retrieval and response generation
- Streamlit-based user interface

## Technologies Used

- Python
- Streamlit
- LangChain
- Google Palm API (Gemini model)
- Hugging Face Instructor Embeddings
- ChromaDB for vector storage

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/19Naveen/WordSmith_ChatBot.git
   cd word-smith
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install Instructor Embeddings:
   ```
   git clone https://github.com/HKUNLP/instructor-embedding
   pip install -r instructor-embedding/requirements.txt
   ```

4. Set up your Google Palm API key:
   - Create a `.env` file in the project root
   - Add your API key: `GOOGLE_API_KEY=your_api_key_here`

## Usage

1. Start the Streamlit app:
   ```
   streamlit run App.py
   ```

2. Open your web browser and navigate to the provided local URL (usually `http://localhost:8501`).

3. Use the "Upload PDF" section to upload your document.

4. Once uploaded, use the chat interface to ask questions about the document content.

## Project Structure

- `App.py`: Main Streamlit application file
- `RAG.py`: Contains the RAG implementation and document processing logic
- `PDF/`: Directory for storing uploaded PDF files
- `Chroma/`: Directory for ChromaDB vector storage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
