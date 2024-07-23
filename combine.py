import json
from nodes.pdf_node import extract_and_chunk_pdfs
from nodes.link_node import extract_and_chunk_links
from nodes.google_bookmark_node import extract_bookmarks
from nodes.notion_node import extract_notion_data

# Function to combine PDF and Link data and save to JSON
def save_to_json(pdf_folder_path: str, 
                 links_file_path: str, 
                 extracted_links_file_path: str, 
                 output_file: str,
                 source_link_metadata: str,
                 bookmarks_desktop_url: str,
                 bookmarks_file_path: str,
                 extracted_bookmarks_path: str,
                 source_bookmark_metadata: str,
                 notion_page_id: str):
    pdf_data = extract_and_chunk_pdfs(pdf_folder_path)
    link_data = extract_and_chunk_links(links_file_path, extracted_links_file_path, source_link_metadata)
    
    extract_bookmarks(bookmarks_desktop_url)
    bookmarks_data = extract_and_chunk_links(bookmarks_file_path, extracted_bookmarks_path, source_bookmark_metadata)
    
    notion_data = extract_notion_data(notion_page_id)

    combined_data = pdf_data + link_data + bookmarks_data + notion_data
    
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(combined_data, f, indent=4)

if __name__ == "__main__":
    bookmarks_desktop_url = r"C:\Users\Michelle\AppData\Local\Google\Chrome\User Data\Default\Bookmarks"
    bookmarks_file_path = "user_kb/bookmarked_links.json"
    extracted_bookmarks_path = "user_kb\extracted_bookmarks.json"
    pdf_folder_path = "user_kb/pdfs"
    links_file_path = "user_kb\links.json"
    extracted_links_file_path = "user_kb\extracted_links.json"
    output_file = "user_kb/combined_data.json"
    source_link_metadata = "Link"
    source_bookmark_metadata = "Google Chrome Bookmark"
    notion_page_id = "dc2c5c90fa4d4843a9d2ed3f1cc4bcfb"

    # Combine PDF and link data and save to JSON
    save_to_json(pdf_folder_path, 
                 links_file_path, 
                 extracted_links_file_path, 
                 output_file, 
                 source_link_metadata,
                 bookmarks_desktop_url,
                 bookmarks_file_path,
                 extracted_bookmarks_path,
                 source_bookmark_metadata,
                 notion_page_id)