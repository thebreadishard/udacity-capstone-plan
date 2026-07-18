import json

def summarize():
    try:
        with open('capstone_full_content.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        print(f"Total pages captured: {len(data)}\n")
        print("Page Titles:")
        for idx, page in enumerate(data):
            print(f"{idx+1}. {page.get('title', 'No Title')} ({len(page.get('content', ''))} characters)")
            
    except Exception as e:
        print(f"Error parsing json: {e}")

if __name__ == "__main__":
    summarize()
