import os
import shutil
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatGooglePalm
from langchain.embeddings import HuggingFaceInstructEmbeddings
from dotenv import load_dotenv
from langchain.chains import RetrievalQA

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
chat_llm = ChatGooglePalm(google_api_key = api_key, model = 'gemini-2.0-flash', temperature=0.5)
instructor_embeddings = HuggingFaceInstructEmbeddings(
    model_name="hkunlp/instructor-large", 
    model_kwargs={"device": "cpu"},  
    encode_kwargs={"normalize_embeddings": True},
    embed_instruction = "Encode this document to make its content easily retrievable by relevant questions.",
    query_instruction = "Embed this question to retrieve the most relevant information from stored documents."
) 

PATH = 'PDF/'
CHROMA_PATH = 'Chroma/'

def load_pdf(path):
    loader = DirectoryLoader(path, glob="*.pdf", loader_cls=PyPDFLoader)
    pages = loader.load()
    return pages

def create_chunks(pages):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(pages)
    for i, chunk in enumerate(chunks):
        normalized_text = chunk.page_content.replace("\r\n", "\n").replace("\r", "\n") or ""
        start_index = chunk.metadata.get("start_index", 0)
        page_number = chunk.metadata.get("page", i + 1)
        preceding_text = normalized_text[:start_index]
        line_number = preceding_text.count("\n") + 1
        exact_words = normalized_text[start_index:start_index + 512]

        # Update metadata
        chunk.metadata.update({
            "page_number": page_number,
            "line_number": line_number,
            "exact_words": exact_words.strip(),
            "chunk_id": i
        })
    return chunks


def create_vector_db(chunks):
    embedding = instructor_embeddings
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding,
        persist_directory=CHROMA_PATH
    )
    return vectordb

def word_smith():
    pages = load_pdf(PATH)
    chunks = create_chunks(pages)
    db = create_vector_db(chunks)
    return db

def retrieve_info(db, query):
    retriever = db.as_retriever(search_kwargs={'k': 3})
    qa = RetrievalQA.from_chain_type(
        llm=chat_llm,
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={
            'verbose': True
        }
    )

    result = qa.invoke(query)
    answer = result['result']
    source_docs = result['source_documents']

    sources = []
    for doc in source_docs:
        metadata = doc.metadata
        sources.append({
            "file": metadata.get("source", "N/A"),
            "page": metadata.get("page_number", "N/A"),
            "line": metadata.get("line_number", "N/A"),
            "chunk": metadata.get("chunk_id", "N/A"),
            "text": metadata.get("exact_words", doc.page_content[:200])  # limit preview
        })

    return {
        "answer": answer,
        "sources": sources
    }