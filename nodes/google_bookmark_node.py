import json

# Function to extract links from the JSON structure
def get_links(bookmark_node):
    links = []
    if 'url' in bookmark_node:
        links.append(bookmark_node['url'])
    if 'children' in bookmark_node:
        for child in bookmark_node['children']:
            links.extend(get_links(child))
    return links

# WHOLE FUNCTION to save all links extracted from desktop file location of google bookmarks 
def extract_bookmarks(bookmarks_json_file):
    # Load the JSON file
    with open(bookmarks_json_file, 'r', encoding='utf-8') as file:
        bookmarks_data = json.load(file)

    # Extract the links
    bookmark_links = get_links(bookmarks_data['roots']['bookmark_bar'])

    bookmark_links = bookmark_links[:10] #TEMPORARY MEASURE - only extracting 10 links because 

    # Save the links to a new JSON file
    with open('user_kb/bookmarked_links.json', 'w', encoding='utf-8') as output_file:
        json.dump(bookmark_links, output_file, indent=4)

# Example usage
if __name__ == "__main__":
    # Path to your exported bookmarks JSON file
    bookmarks_json_file = r"C:\Users\Michelle\AppData\Local\Google\Chrome\User Data\Default\Bookmarks"
    extract_bookmarks(bookmarks_json_file)
