from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from Utilities.Tools import create_vector_db, create_chunks

PDF_PATH = 'PDF/'

def load_pdf(path: str):
    """Load all PDFs from a directory."""
    loader = DirectoryLoader(path, glob="*.pdf", loader_cls=PyPDFLoader)
    return loader.load()

def document_RAG():
    """Create a vector DB from PDF documents."""
    pages = load_pdf(PDF_PATH)
    if not pages:
        return "No PDF documents found."
    chunks = create_chunks(pages, metadata=True)
    db = create_vector_db(chunks, CHROMA_PATH='Chroma/', collection_name='Document_Vector')
    return db
