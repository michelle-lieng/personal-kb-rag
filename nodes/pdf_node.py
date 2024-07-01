# Import libraries
import re
from io import BytesIO
from typing import List # use List as then we can be specific on which elements the list can contain, e.g. List(str)
from langchain.docstore.document import Document
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS

#-------------------FUNCTION TO READ PDF, EXTRACT TEXT, CLEAN TEXT
def parse_pdf(file: BytesIO, filename: str) -> tuple[List[str], str]:
    """

    This function is used to:
        - Read a PDF file
        - Extract text
        - Apply text processing and cleaning operations to the text
    
    """
    # Initialize the PDF reader for the provided file
    pdf = PdfReader(file) # enables to use method pages
    cleaned_text = []
    
    # Loop through all the pages in the PDF
    for page in pdf.pages:
        # Extract the text from the page
        text = page.extract_text()
        
        # re.sub is used to find and then replace certain parts of the text to clean it up
        # replace single newlines with spaces
        text = re.sub(r"\n", " ",text)
        
        # Append the cleaned text to the output list.
        cleaned_text.append(text)
    
    # Return the list of cleaned texts and the filename.
    return cleaned_text, filename

"""
# Trialing the parse_pdf function
pdf = PdfReader(r"user_kb\pdfs\amex_ultimatecard.pdf")
text = pdf.pages[0].extract_text()
parse_pdf(r"user_kb\pdfs\amex_ultimatecard.pdf", "amex_ultimatecard")
"""

#------------------FUNCTION TO CHUNK TEXT AND ADD METADATA TO CHUNKS USING LABGCHAIN'S DOCUMENT OBJECT
def text_to_docs(text: List[str], filename: str) -> List[Document]:
    """

    Note: the text variable is a list of cleaned text where each element is a page from a pdf

    This function is used to:
        - Take a list of text strings & file name
        - Processes the text to create a list of chunked "Document" objects
        - These objects each represent a smaller portion of the original text with associated metadata
    
    """
    # Ensure the input text is a list. If it's a string, convert it to a list.
    if isinstance(text, str):
        text = [text]
    
    # Convert each text (from a page) to a Langchain Document object
    page_docs = [Document(page_content=page) for page in text]
    
    # Assign a page number to the metadata of each document.
    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = 1+i #as enumerate starts at 0

    doc_chunks = []
    
    # Split each page's text into smaller chunks and store them as separate documents.
    for doc in page_docs:
        # Initialize the text splitter with specific chunk sizes and delimiters.
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, 
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            chunk_overlap=0,
        )
        
        # Split the dcument pages into chunks
        chunks = text_splitter.split_text(doc.page_content)
        # print(chunks)

        # Convert each chunk into a new document, storing its chunk number, page number, and source file name in its metadata.
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk, 
                metadata={"page": doc.metadata["page"], #this is the page metadata from previous doc object before it was chunked
                          "chunk": i+1}
                          )
            # doc.metadata["source"] = f"page {doc.metadata['page']} - section {doc.metadata['chunk']}"
            doc.metadata["filename"] = filename
            doc_chunks.append(doc)
    
    # Return the list of chunked documents.
    return doc_chunks

"""
# Trialing the functions

cleaned_text, filename = parse_pdf(r"user_kb\pdfs\pds_ultimatecard.pdf", "pds_ultimatecard")
include_metadata = text_to_docs(cleaned_text,filename)

for line in include_metadata:
    print(line)
    print("\n")
"""

#---------------FUNCTION TO CREATE VECTOR DATABASE
def create_vectordb(pdf_files: List[str], pdf_names: List[str], openai_api_key: str):

    """
    This function aims to index PDF files. It accepts a list of PDF file objects and their names.

    The steps outlined include:
        1. parse_pdf function - reads PDF content and cleans the data
        2. text_to_docs function - splits the text into smaller chunks suitable for embedding and indexing
        3. FAISS.from_ducments - creates embeddings from chucks and returns a FAISS index and vector db 

    Langchain's "FAISS.from_documents" method takes a lists of documents and the openapi key 
    and changes all the documents into embeddings and creates a faiss vector database and index.
    """
    
    documents = []

    for pdf_file, pdf_name in zip(pdf_files, pdf_names):
        text, filename = parse_pdf(pdf_file, pdf_name)
        documents = documents + text_to_docs(text, filename)

    # documents are the cleaned and chucked PDF data
    # this data is then turned into a vector db
    
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    db = FAISS.from_documents(documents, embeddings)
    
    return db

# Get all PDF file names
import os
def read_pdf_files_from_folder(folder_path: str):
    pdf_files = []
    pdf_names = []
    
    for file in os.listdir(folder_path):
        if file.endswith(".pdf"):
            pdf_names.append(file[:-4]) # Use slicing to remove the last 4 characters which are '.pdf'
            pdf_files.append(os.path.join(folder_path, file))
    return pdf_files, pdf_names

"""
#try function

pdf_files, pdf_names = read_pdf_files_from_folder(r"user_kb\pdfs")   

# Read openai key
from helpers.support_functions import read_api_key
openai_api_key = read_api_key('openai')

#db = create_vectordb([r"user_kb\pdfs\amex_ultimatecard.pdf"], ["amex_ultimatecard"], openai_api_key)

db = create_vectordb(pdf_files, pdf_names, openai_api_key)

query = "Who is eligible for travel insurance?"
docs = db.similarity_search(query, k=3) #get 3 chunks

for line in docs:
    print(line)
    print("\n")

#docs[1] # can slice chunks like this -> get the 2nd chunk
#print(docs[0].page_content)
"""

# Define the template for the chatbot system prompt
system_prompt_pdf = """
    You are a helpful assistant who answers to users questions based on multiple contexts given to you.
    Keep your answer short and to the point.
    The evidence are the context of the pdf extract with metadata. 
    Carefully focus on the metadata specially 'filename' and 'page' whenever answering.
    Make sure to add filename and page number at the end of sentence you are citing to.
    Reply "Not applicable" if text is irrelevant.
    The PDF content is:
    {pdf_extract}
"""