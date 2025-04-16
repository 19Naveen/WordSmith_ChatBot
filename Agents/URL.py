from Utilities.Tools import create_vector_db, create_chunks
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_url(url: str):
    """
    Loads content from a given URL using WebBaseLoader.
    """
    loader = WebBaseLoader(url, show_progress=True, continue_on_failure=True)
    docs = loader.load()
    return docs

def preprocess(text: str) -> str:
    """
    Cleans up text by removing newlines and redundant spaces.
    """
    text = text.replace('\n', ' ').strip()
    while '  ' in text:
        text = text.replace('  ', ' ')
    return text


def url_RAG(url):
    docs = process_url(url)
    text = preprocess(docs)
    text = create_chunks(text, False)
    db = create_vector_db(text, 'Chroma/', 'URL_Vector')
    return db

