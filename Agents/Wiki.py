from langchain.utilities import WikipediaAPIWrapper

wiki = WikipediaAPIWrapper(
    lang="en",
    top_k_results=1,
    load_max_docs=1,
    doc_content_chars_max=5000
)

def get_wiki_summary(topic):
    """Get a summary of a topic from Wikipedia."""
    result = wiki.run(topic)
    return result