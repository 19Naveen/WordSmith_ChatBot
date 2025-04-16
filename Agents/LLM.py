from Utilities.Tools import LLM
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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
chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

def chat_with_llm(query: str) -> str:
    '''
    Function to interact with the LLM
        query (str): The input query to send to the LLM
    Returns:
        str: The response from the LLM
    '''
    response = chain.invoke({"input": query})
    return response['text']
