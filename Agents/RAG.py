from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from Utilities.Tools import create_vector_db, create_chunks
PATH = 'PDF/'

def load_pdf(path):
    loader = DirectoryLoader(path, glob="*.pdf", loader_cls=PyPDFLoader)
    pages = loader.load()
    return pages

def document_RAG():
    pages = load_pdf(PATH)
    chunks = create_chunks(pages, metadata=True)
    db = create_vector_db(chunks, CHROMA_PATH='Chroma/', vector_name='Document_Vector')
    return db

