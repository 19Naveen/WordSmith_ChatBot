import os

PDF_PATH = 'PDF'

if os.path.exists(PDF_PATH):
    for file in os.listdir(PDF_PATH):
        Path = os.path.join(PDF_PATH, file)
        os.remove(Path)
    print("Directory Files has been removed successfully")

if not os.path.exists(PDF_PATH):
    os.mkdir(PDF_PATH)

def upload_file(file):
    if file is None:
        return "No file provided"
    file_path = os.path.join(PDF_PATH, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())
    return file_path

def chat_with_bot(user_input, history, db):
    try:
        if db is None:
            return "Database is not initialized. Please upload a PDF first.", history
        response = retrieve_info(db, query=user_input) 
        bot_response = response['result']
        sources = response['sources']
        print('metadata:', response['sources'])
        history.append((user_input, bot_response, sources))
        return bot_response, history
    except Exception as e:
        error_message = f"Error processing query: {str(e)}"
        history.append((user_input, error_message))
        return "", history
    
