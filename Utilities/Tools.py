import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
load_dotenv()

class LLM:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.llm_model = cls._instance._create_chat_model()
        return cls._instance

    def _create_chat_model(self):
        """
        Creates a Google Generative AI model using Gemini.
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise EnvironmentError("Missing GOOGLE_API_KEY in .env.")
        try:
            return ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model='gemini-1.5-flash-latest',
                temperature=0.5
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Gemini model: {e}")

    def model(self):
        return self.llm_model


def create_chunks(pages, metadata=False):
    """
    Splits documents into chunks with optional metadata.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(pages)

    if metadata:
        for i, chunk in enumerate(chunks):
            normalized_text = chunk.page_content.replace("\r\n", "\n").replace("\r", "\n")
            start_index = chunk.metadata.get("start_index", 0)
            page_number = chunk.metadata.get("page", i + 1)
            preceding_text = normalized_text[:start_index]
            line_number = preceding_text.count("\n") + 1
            exact_words = normalized_text[start_index:start_index + 512]

            chunk.metadata.update({
                "page_number": page_number,
                "line_number": line_number,
                "exact_words": exact_words.strip(),
                "chunk_id": i
            })

    return chunks

def load_embeddings():
    """
    Loads HuggingFace sentence embeddings for instruction tuning.
    """
    return HuggingFaceInstructEmbeddings(
        cache_folder='Embeddings',
        model_name="all-mpnet-base-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
        embed_instruction="Encode this document to make its content easily retrievable by relevant questions.",
        query_instruction="Embed this question to retrieve the most relevant information from stored documents."
    )


def create_vector_db(chunks, CHROMA_PATH, collection_name='default'):
    """
    Creates and returns a persistent vector database.
    """
    embedding = load_embeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        collection_name=collection_name,
        embedding=embedding,
        persist_directory=CHROMA_PATH
    )
    return vectordb


### ----------- Retrieval & QA -----------

def retrieve_info(db, query, return_source=False):
    """
    Uses RetrievalQA to answer a query using the vector database.
    """
    llm = LLM().model()
    retriever = db.as_retriever(search_kwargs={'k': 3})
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=retriever,
        return_source_documents=return_source,
        chain_type_kwargs={'verbose': True}
    )

    result = qa.invoke(query)
    if return_source:
        answer = result['result']
        sources = result['source_documents']

        formatted_sources = []
        for doc in sources:
            metadata = doc.metadata
            formatted_sources.append({
                "file": metadata.get("source", "N/A"),
                "page": metadata.get("page_number", "N/A"),
                "line": metadata.get("line_number", "N/A"),
                "chunk": metadata.get("chunk_id", "N/A"),
                "text": metadata.get("exact_words", doc.page_content[:200])
            })

        return {"answer": answer, "sources": formatted_sources}
    else:
        return result

def chat_with_bot(user_input, history, db):
    """
    Handles a conversation with the LLM using the vector DB.
    """
    try:
        if db is None:
            return "Database is not initialized. Please upload a document first.", history

        response = retrieve_info(db, query=user_input, return_source=True)
        answer = response.get("answer", "No answer found.")
        sources = response.get("sources", [])

        if not sources:
            bot_response = answer
        else:
            sources_text = "\n".join(
                f"{src['file']} (Page {src['page']}, Line {src['line']})"
                for src in sources
            )
            bot_response = f"{answer}\n\nSources:\n{sources_text}"

        history.append((user_input, bot_response, sources))
        return bot_response, history

    except Exception as e:
        error_message = f"Error: {str(e)}"
        history.append((user_input, error_message))
        return error_message, history
