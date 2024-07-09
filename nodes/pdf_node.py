import os
import re
from io import BytesIO
from typing import List
from pypdf import PdfReader

# Function to read the OpenAI API key
from helpers.support_functions import read_api_key

# Read OpenAI key
openai_api_key = read_api_key('openai')

# Function to parse PDF and extract text
def parse_pdf(file: BytesIO, filename: str) -> List[dict]:
    pdf = PdfReader(file)
    docs = []

    for page_num, page in enumerate(pdf.pages):
        text = page.extract_text()
        text = re.sub(r"\n", " ", text)
        docs.append({
            "content": text,
            "metadata": {
                "source": "PDF",
                "identifier": filename,
                "location": f"Page {page_num + 1}"
            }
        })
    return docs

# Function to chunk text
def chunk_text(text: str, chunk_size: int = 200, overlap: int = 30) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(' '.join(words[i:i + chunk_size]))
    return chunks

# Function to extract and parse all PDFs in a folder, then chunk the text
def extract_and_chunk_pdfs(pdf_folder_path: str) -> List[dict]:
    pdf_files = []
    pdf_names = []

    for file in os.listdir(pdf_folder_path):
        if file.endswith(".pdf"):
            pdf_names.append(file)
            pdf_files.append(os.path.join(pdf_folder_path, file))
    
    all_pdf_data = []
    for pdf_file, pdf_name in zip(pdf_files, pdf_names):
        with open(pdf_file, 'rb') as file:
            pdf_data = parse_pdf(file, pdf_name)
            for doc in pdf_data:
                chunks = chunk_text(doc["content"])
                for chunk_num, chunk in enumerate(chunks):
                    all_pdf_data.append({
                        "content": chunk,
                        "metadata": {
                            "source": "PDF",
                            "identifier": pdf_name,
                            "location": f"{doc['metadata']['location']} - Chunk {chunk_num + 1}"
                        }
                    })
    
    return all_pdf_data

# Example usage
if __name__ == "__main__":
    pdf_folder_path = "user_kb/pdfs"
    chunked_pdf_data = extract_and_chunk_pdfs(pdf_folder_path)
    print(chunked_pdf_data)