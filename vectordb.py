import json
from sentence_transformers import SentenceTransformer
import faiss

# Load combined data
def load_combined_data(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        combined_data = json.load(f)
    return combined_data

# Create embeddings
def create_embeddings(data, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    texts = [item["content"] for item in data]
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings, data

# Create FAISS index
def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

# Save FAISS index and metadata
def save_faiss_index(index, metadata, index_path='faiss_index.bin', metadata_path='metadata.json'):
    faiss.write_index(index, index_path)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4)

# Load combined data, create embeddings, and save the FAISS index and metadata
if __name__ == "__main__":
    combined_data_path = "user_kb/combined_data.json"
    combined_data = load_combined_data(combined_data_path)

    embeddings, metadata = create_embeddings(combined_data)
    index = create_faiss_index(embeddings)

    save_faiss_index(index, metadata)
    print("Vector database created and saved successfully.")