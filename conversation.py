import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI
from helpers.support_functions import read_api_key

# Read OpenAI key
openai_api_key = read_api_key('openai')

# Load the FAISS index and metadata
def load_faiss_index(index_path='faiss_index.bin', metadata_path='metadata.json'):
    index = faiss.read_index(index_path)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    return index, metadata

# Function for similarity search
def similarity_search(query, model, index, metadata, top_k=3):
    query_vector = model.encode([query])[0].astype('float32')
    distances, indices = index.search(np.array([query_vector]), top_k)
    results = [metadata[i] for i in indices[0]]
    return results

# Universal system prompt
system_prompt_universal = """
    You are a helpful assistant who answers users' questions based on multiple contexts given to you.
    Keep your answers short and to the point.
    The evidence provided is the context of the extracts from various sources with metadata.
    Carefully focus on the metadata, especially 'identifier' and 'location' whenever answering.
    Make sure to add the identifier (filename/URL) and location (page/chunk) at the end of the sentence you are citing.
    Reply "Not applicable" if the text is irrelevant.
    The content provided is:
    {extract}
"""

# Function for chatbot conversation
def conversation():
    user_query = ""  # Initialize user_query with an empty string
    chat_history = [] # Define chat history

    # Load FAISS index and metadata
    index, metadata = load_faiss_index()

    # Load SentenceTransformer model for encoding queries
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    while True:
        user_query = input("Ask anything: ")

        if user_query.lower() == "end":
            break
        else:
            # Retrieve 3 similar document chunks to the user query
            docs = similarity_search(user_query, model, index, metadata, top_k=3)

            # Format the document chunks for the system prompt
            extract = "\n\n".join([f"Identifier: {doc['metadata']['identifier']} - {doc['metadata']['location']}\n\n{doc['content']}" for doc in docs])

            # Initialize system prompt to be added to the model
            system = {"role": "system", "content": system_prompt_universal.format(extract=extract)}

            # Add the user query to chat history 
            chat_history.append({"role": "user", "content": user_query})

            # Call OpenAI API
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
                print(f"Identifier: {line['metadata']['identifier']} - {line['metadata']['location']}\n{line['content']}\n")
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

# Run function
if __name__ == "__main__":
    conversation()
