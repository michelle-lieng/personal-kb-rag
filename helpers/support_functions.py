import json

def read_api_key(key_name, file_path='helpers/api_keys.json'):
    try:
        with open("helpers/api_keys.json", 'r') as f:
            api_keys = json.load(f)
            return api_keys.get(key_name)
    except FileNotFoundError:
        print(f"API keys file not found at {file_path}.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the API keys file at {file_path}.")
        return None
"""
# Usage example
openai_api_key = read_api_key('openai')
"""