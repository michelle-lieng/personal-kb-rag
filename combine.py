import json
from nodes.pdf_node import extract_and_chunk_pdfs
from nodes.link_node import extract_and_chunk_links

# Function to combine PDF and Link data and save to JSON
def save_to_json(pdf_folder_path: str, 
                 links_file_path: str, 
                 extracted_links_file_path: str, 
                 output_file: str):
    pdf_data = extract_and_chunk_pdfs(pdf_folder_path)
    link_data = extract_and_chunk_links(links_file_path, extracted_links_file_path)
    combined_data = pdf_data + link_data
    
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4)

if __name__ == "__main__":
    pdf_folder_path = "user_kb/pdfs"
    links_file_path = "user_kb\links.json"
    extracted_links_file_path = "user_kb\extracted_links.json"
    output_file = "user_kb/combined_data.json"

    # Combine PDF and link data and save to JSON
    save_to_json(pdf_folder_path, links_file_path, extracted_links_file_path, output_file)