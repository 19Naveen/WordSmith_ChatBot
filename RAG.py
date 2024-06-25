import os
import shutil
from langchain.document_loaders import TextLoader
from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chat_models import ChatGooglePalm
from langchain.embeddings import HuggingFaceInstructEmbeddings
from dotenv import load_dotenv
from langchain.chains import RetrievalQA

chat_llm = ChatGooglePalm(google_api_key = 'AIzaSyCe-7cr2qgoxBS5LyVa_-fd2Fngh4Xwv2U',model = 'gemini-1.5-flash', temperature=0.5)
instructor_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large") 

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
    return chunks

def create_vector_db(chunks):
    embedding = instructor_embeddings
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedding
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
        retriever=retriever
    )
    return qa.invoke(query)
