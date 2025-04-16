from Agents.RAG import retrieve_info, word_smith

PATH = ''
query = ''

db = word_smith(PATH)
result = retrieve_info(db, query)
print(result)