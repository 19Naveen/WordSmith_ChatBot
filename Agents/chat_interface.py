from Utilities.Tools import LLM
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain

# Setup
llm = LLM().model()
memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=5000,
    return_messages=True,
    memory_key="history"
)

prompt = PromptTemplate(
    input_variables=["history", "input"],
    template="""
    The conversation so far:
    {history}

    User: {input}
    AI:"""
)

# Create chain
chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

def chat_with_llm(query: str) -> str:
    """Interact with LLM using a conversational chain."""
    try:
        response = chain.invoke({"input": query})
        return response['text']
    except Exception as e:
        return f"Error during LLM interaction: {e}"
