import json
from helpers.web_crawler import run_spider
import spacy

def read_links_from_json(file_path: str):
    with open(file_path, "r") as file:
        return json.load(file)
    
def chunk_clean_links(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    # Check if the string contains multiple lists
    if '][' in data:
        # Correct the format by adding commas between the lists
        data = data.replace('][', '],[')
        # Wrap the entire string in square brackets to form a valid JSON array
        data = f'[{data}]'
        # Load the corrected JSON string
        data = json.loads(data)[-1]
    else:
        data = json.loads(data)

    nlp = spacy.load('en_core_web_sm')

    def clean_text(text):
        text = text.replace('\n', ' ').replace('\r', ' ')
        doc = nlp(text)
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(tokens)

    def chunk_text(text, chunk_size=150, overlap=30):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(' '.join(words[i:i + chunk_size]))
        return chunks

    all_chunks = []
    for entry in data:
        clean_content = clean_text(entry['content'])
        chunks = chunk_text(clean_content)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "content": chunk,
                "metadata": {
                    "source": entry['metadata']['source'],
                    "identifier": entry['metadata']['identifier'],
                    "location": f"Chunk {i + 1}"
                }
            })

    return all_chunks

def extract_and_chunk_links(links_file_path: str, extracted_links_file_path: str):
    # get the urls used for scraping
    urls_list = read_links_from_json(links_file_path)

    # run spider to scrape the urls
    run_spider(urls_list)

    # chunk and clean the extracted data from links
    return chunk_clean_links(extracted_links_file_path)

# Example usage
if __name__ == "__main__":
    links_file_path = "user_kb\links.json"
    extracted_links_file_path = "user_kb\extracted_links.json"
    print(extract_and_chunk_links(links_file_path, extracted_links_file_path))
