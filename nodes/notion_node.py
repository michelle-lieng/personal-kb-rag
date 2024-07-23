import json
from notion_client import Client, APIResponseError
from helpers.support_functions import read_api_key

notion_api = read_api_key("notion")

# Initialize Notion client with your integration token
notion = Client(auth=notion_api)

# Function to fetch blocks from a Notion page
def fetch_page_blocks(page_id):
    results = []
    start_cursor = None

    while True:
        try:
            response = notion.blocks.children.list(
                block_id=page_id,
                start_cursor=start_cursor
            )
            results.extend(response['results'])
            if not response['has_more']:
                break
            start_cursor = response['next_cursor']
        except APIResponseError as e:
            print(f"An error occurred: {e}")
            break

    return results

# Function to fetch page title
def fetch_page_title(page_id):
    try:
        response = notion.pages.retrieve(page_id)
        title = response['properties']['title']['title'][0]['plain_text']
    except APIResponseError as e:
        print(f"An error occurred: {e}")
        title = "Unknown Title"
    return title

# Function to extract content from blocks
def extract_content_from_blocks(blocks):
    content_list = []

    for block in blocks:
        block_type = block['type']
        try:
            if block_type == 'paragraph':
                text = block['paragraph']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'heading_1':
                text = block['heading_1']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'heading_2':
                text = block['heading_2']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'heading_3':
                text = block['heading_3']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(content)
            elif block_type == 'bulleted_list_item':
                text = block['bulleted_list_item']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(f"• {content}")
            elif block_type == 'numbered_list_item':
                text = block['numbered_list_item']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(f"{block['numbered_list_item']['number']}. {content}")
            elif block_type == 'to_do':
                text = block['to_do']['rich_text']
                content = ''.join([t['plain_text'] for t in text])
                content_list.append(f"[{'x' if block['to_do']['checked'] else ' '}] {content}")
            # Add more block types as needed
        except KeyError as e:
            print(f"KeyError: {e} in block type: {block_type}")

    return content_list

# Function to chunk text
def chunk_text(text, chunk_size=200, overlap=30):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(' '.join(words[i:i + chunk_size]))
    return chunks

# Function to create JSON structure
def create_json_structure(content_list, source, identifier):
    data = []
    chunk_num = 0
    for content in content_list:
        chunks = chunk_text(content)
        for chunk in chunks:
            chunk_num += 1
            metadata = {
                "source": source,
                "identifier": identifier,
                "location": f"Chunk {chunk_num}"
            }
            data.append({
                "content": chunk,
                "metadata": metadata
            })
    return data

def extract_notion_data(notion_page_id):
    # Fetch page blocks
    page_blocks = fetch_page_blocks(notion_page_id)

    # Fetch page title
    page_title = fetch_page_title(notion_page_id)

    # Extract content from the blocks
    content_list = extract_content_from_blocks(page_blocks)

    # Create JSON structure
    extracted_data = create_json_structure(content_list, source="Notion", identifier=page_title)

    # Write to JSON file
    with open('user_kb/extracted_notion.json', 'w', encoding='utf-8') as json_file:
        json.dump(extracted_data, json_file, ensure_ascii=False, indent=4)

    return extracted_data

if __name__ == "__main__":
    notion_page_id = "dc2c5c90fa4d4843a9d2ed3f1cc4bcfb"
    extract_notion_data(notion_page_id)
