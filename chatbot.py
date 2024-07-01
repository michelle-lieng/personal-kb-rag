# Import libraries
from nodes.pdf_node import create_vectordb, read_pdf_files_from_folder
from src.chatbot_setup import system_prompt
from openai import OpenAI
import json # for readability of the chat history

# Read openai key
with open(r'src\GPT_api_key.txt') as f:
    openai_api_key = f.read()

# Function for chatbot
def conversation():
    user_query = ""  # Initialize x with an empty string
    chat_history = [] # Define chat history

    data_folder = "data"  # Path to the folder where PDFs are stored.
    pdf_files, pdf_names = read_pdf_files_from_folder(data_folder)

    # create vector database and index
    db = create_vectordb(pdf_files, pdf_names, openai_api_key)
    
    while True:
        user_query = input("Ask anything: ")

        if user_query.lower() == "end":
            break
        else:
            # retrieve 3 similar document chunks to the user query
            docs = db.similarity_search(user_query, k=3) 

            # add these document chunks to the system prompt
            #pdf_extract = "/n ".join([result.page_content for result in docs])
            pdf_extract = docs

            #initialize system prompt to be added to the model
            system = {"role": "system", "content": system_prompt.format(pdf_extract=pdf_extract)}

            # add in user_query to chat history 
            chat_history.append({"role": "user", "content": user_query})

            # call openai api
            client = OpenAI(api_key=openai_api_key)

            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[system] + chat_history,
                temperature=0,
                max_tokens=200,
                frequency_penalty=0
            )

            chatbot_response = completion.choices[0].message.content
            chat_history.append({"role": "assistant", "content": chatbot_response})
            
            print("\n")
            print("This is the pdf extracts: ")
            print("-------------------------")
            for line in docs:
                print(line)
                print("\n")
            print("This is the chatbot response: ")
            print("-----------------------------")
            print(chatbot_response)
            print("\n")
            print("This is the chat history: ")
            print("-------------------------")
            for entry in chat_history:
                print(json.dumps(entry, indent=4))
            print("\n")
            print("This is the token count: ")
            print("-------------------------")
            print(f'{completion.usage.prompt_tokens} prompt tokens counted by the OpenAI API.')
            print(f'You have {4097 - completion.usage.prompt_tokens} remaining tokens for the gpt-3.5-turbo model.')
            print("\n")
            continue

# run function
conversation()