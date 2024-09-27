import json
import re

def is_valid_content(text):
    # Split the text into words and numbers
    words = re.findall(r'\b\w+\b', text)
    return len(words) >= 3

def remove_duplicates_and_short_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data:
        if 'content' in entry:
            # Remove duplicates and short content
            unique_valid_content = list(dict.fromkeys(
                item for item in entry['content'] if is_valid_content(item)
            ))
            entry['content'] = unique_valid_content

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Usage
remove_duplicates_and_short_content('ai_agent_framework/knowledge/JOJOProduct_knowledge.json')