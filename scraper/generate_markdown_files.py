import json
import re
import os
from markdownify import markdownify as md

def convert_to_md_and_clean(html_text):
    # Convert HTML to Markdown (preserves links, bold, tables, lists perfectly)
    # the 'strip' argument ensures all images and SVG icons are physically deleted so they don't produce base64 gibberish
    text = md(html_text, heading_style="ATX", escape_asterisks=False, strip=['img', 'svg', 'picture'])
    
    # Just in case any embedded data URLs bypass markdownify via background images
    text = re.sub(r'!\[.*?\]\(data:image/[^)]+\)', '', text)
    text = re.sub(r'\[.*?\]\(data:image/[^)]+\)', '', text)
    
    # Clean up Marvin AI and other UI clutter
    marvin_split = re.split(r"Give Page Feedback|\nMarvin AI\n", text)
    if len(marvin_split) > 1:
        text = marvin_split[0]
        
    # Udacity's progress tracker dynamically updates as we traverse pages, so we use regex
    # to split everything before "Program is XX% complete"
    top_split = re.split(r"Program is \d+% complete\**", text)
    if len(top_split) > 1:
        text = top_split[-1]
        
    # Occasionally the raw percentage number might sneak past if the layout shifts slightly
    text = re.sub(r'^\s*\*\*?\d+%\*\*?\n', '', text)
    
    # Strip generic Udacity navigation links and isolated buttons that markdownify captured
    text = re.sub(r'\[Previous\]\(/cd001-[^\)]+\)', '', text)
    text = re.sub(r'\[Next\]\(/cd001-[^\)]+\)', '', text)
    text = re.sub(r'(?m)^Previous\s*$', '', text)
    text = re.sub(r'(?m)^Next\s*$', '', text)
    
    # Generic newline cleaning (remove excessive blank lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def get_lesson_key(url):
    # Udacity uses 'lessonKey=' in the URL to delimit major project modules
    match = re.search(r"lessonKey=([^&]+)", url)
    if match:
        return match.group(1)
    return "unknown_lesson"

def generate():
    # If ran from root or scraper dir, find the json file
    data_path = 'capstone_full_content.json'
    if not os.path.exists(data_path) and os.path.exists('scraper/capstone_full_content.json'):
        data_path = 'scraper/capstone_full_content.json'
        
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    modules = []
    current_lesson_key = None
    current_module = []
    
    # Group the pages by their unique lessonKey
    for page in data:
        title = page.get("title", "")
        url = page.get("url", "")
        
        # Apply markdownify to the html content
        content = convert_to_md_and_clean(page.get("content", ""))
        
        lKey = get_lesson_key(url)
        
        if current_lesson_key is None:
            current_lesson_key = lKey
            
        if lKey != current_lesson_key:
            # We transitioned into a completely new module!
            modules.append(current_module)
            current_module = []
            current_lesson_key = lKey
            
        current_module.append({
            "title": title,
            "content": content
        })
        
    # Append the final looping block
    if current_module:
        modules.append(current_module)

    # 9 exact modules matched to the sidebar UI
    known_names = [
        "APA Resources",
        "AI Programming Foundations Project",
        "Conduct a Statistical Analysis Using Python",
        "Applied Machine Learning",
        "Deep Learning Systems",
        "Generative AI Applications",
        "Design of Autonomous and Semi-Autonomous Agentic Workflows",
        "Industry-Integrated AI Systems Synthesis",
        "Professional Industry Defense"
    ]
    
    out_dir = "CapstoneProjects"
    os.makedirs(out_dir, exist_ok=True)
    
    for idx, module_pages in enumerate(modules):
        if idx < len(known_names):
            mod_name = known_names[idx]
        else:
            mod_name = f"Extra_Module_{idx+1}"
            
        slug = re.sub(r'[^A-Za-z0-9]+', '_', mod_name).strip('_')
        md_file = os.path.join(out_dir, f"{idx+1:02d}_{slug}.md")
        
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# {mod_name}\n\n")
            
            for page in module_pages:
                f.write(f"## {page['title']}\n\n")
                f.write(page['content'])
                f.write("\n\n---\n\n")
                
        print(f"Generated: {md_file} with {len(module_pages)} pages.")

if __name__ == "__main__":
    generate()
