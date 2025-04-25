from langchain.utilities import WikipediaAPIWrapper
from Utilities.Tools import LLM, create_vector_db, create_chunks
from langchain.memory import ConversationSummaryBufferMemory

# Set up LLM and memory
llm = LLM().model()
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=5000,
    return_messages=True,
    memory_key="history"
)

# Configure Wikipedia wrapper
wiki = WikipediaAPIWrapper(,
    wiki_client=None,
    search_results=1,
    lang="en",
    top_k_results=1,
    load_all_available_meta=True,
    doc_content_chars_max=10000
)

def get_wiki_summary(topic: str) -> str:
    """Fetch a summary from Wikipedia for a given topic."""
    try:
        result = wiki.run(topic)
        return result['content']
    except Exception as e:
        return f"Error fetching summary: {e}"

def create_wiki_db(topic: str):
    """Create a vector DB from Wikipedia content."""
    content = get_wiki_summary(topic)
    if not content:
        return "No content retrieved from Wikipedia."
    chunks = create_chunks(content, metadata=False)
    db = create_vector_db(chunks, 'Chroma/', 'Wiki_Vector')
    return db
