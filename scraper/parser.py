import re
import json

def parse():
    html = open("classroom_page.html", encoding="utf-8").read()
    
    state_match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});", html, re.DOTALL)
    if state_match:
        print("Found window.__INITIAL_STATE__!")
    else:
        print("No window.__INITIAL_STATE__ found.")
        
    apollo_match = re.search(r"window\.__APOLLO_STATE__\s*=\s*(\{.*?\});", html, re.DOTALL)
    if apollo_match:
        print("Found window.__APOLLO_STATE__!")
    else:
        print("No window.__APOLLO_STATE__ found.")

    next_match = re.search(r"__NEXT_DATA__.*?(\{.*?\})</script>", html, re.DOTALL)
    if next_match:
        print("Found __NEXT_DATA__!")
    else:
        print("No __NEXT_DATA__ found.")

if __name__ == "__main__":
    parse()
