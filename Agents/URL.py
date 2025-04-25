from langchain.document_loaders import WebBaseLoader
from Utilities.Tools import create_vector_db, create_chunks

def process_url(url: str):
    """Load and return documents from a URL."""
    loader = WebBaseLoader(url, show_progress=True, continue_on_failure=True)
    return loader.load()

def preprocess(text: str) -> str:
    """Remove excessive whitespace and line breaks."""
    return ' '.join(text.replace('\n', ' ').split())

def url_RAG(url: str):
    """Create a vector DB from web page content."""
    docs = process_url(url)
    if not docs:
        return "No content loaded from URL."
    raw_text = ' '.join([doc.page_content for doc in docs])
    cleaned = preprocess(raw_text)
    chunks = create_chunks(cleaned, metadata=False)
    db = create_vector_db(chunks, 'Chroma/', 'URL_Vector')
    return db
