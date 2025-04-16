import os
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
load_dotenv()

class LLM:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLM, cls).__new__(cls)
            cls._instance.llm_model = cls.create_chat_model()
        return cls._instance
    
    @staticmethod
    def create_chat_model():
        """
        Creates a Language Model (LLM) using Google API Key.

        Returns:
            ChatGoogleGenerativeAI: An instance of the LLM model, or None if the API key is missing.
        """
        api_key = os.getenv('GOOGLE_API_KEY')
        try:
            if not api_key:
                raise EnvironmentError("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
                
            chat_llm = ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model='gemini-1.5-flash-latest',
                temperature=0.5
            )
            return chat_llm
        
        except EnvironmentError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Failed to create ChatGoogleGenerativeAI instance: {e}")

    def model(self):
        return self.model

def create_chunks(pages, metadata=False):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(pages)
    if not metadata:
        return chunks
    
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
            "exact_words": exact_words.strip()
        })
    return chunks

def load_embeddings():
    instructor_embeddings = HuggingFaceInstructEmbeddings(
        cache_folder='Embeddings',
        model_name="all-mpnet-base-v2", 
        model_kwargs={"device": "cpu"},  
        encode_kwargs={"normalize_embeddings": True},
        embed_instruction = "Encode this document to make its content easily retrievable by relevant questions.",
        query_instruction = "Embed this question to retrieve the most relevant information from stored documents."
    ) 
    return instructor_embeddings

def create_vector_db(chunks, CHROMA_PATH, collection_name='default'):
    embedding = load_embeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        collection_name=collection_name,
        embedding=embedding,
        persist_directory=CHROMA_PATH
    )
    return vectordb

def retrieve_info(db, query, return_source=False):
    llm = LLM()
    retriever = db.as_retriever(search_kwargs={'k': 3})
    qa = RetrievalQA.from_chain_type(
        llm=llm.model(),
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=return_source,
        chain_type_kwargs={
            'verbose': True
        }
    )

    result = qa.invoke(query)
    if return_source:
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
                "text": metadata.get("exact_words", doc.page_content[:200])  
            })

        return {
            "answer": answer,
            "sources": sources
        }
    else:
        return result