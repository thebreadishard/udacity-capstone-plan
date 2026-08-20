"""One-off helper: convert a Playwright accessibility-tree snapshot dump (as
produced by the read_page tool) into a readable markdown transcript of a
Gemini shared chat. Not part of the regular scraper pipeline.
"""
import re
import sys

NOISE_EXACT = {
    "New chat", "Gemini", "About Gemini link", "About Gemini",
    "Get Gemini app link", "Get Gemini App", "Subscriptions link",
    "Subscriptions", "For Business link", "For Business", "Sign in",
    "Copy prompt", "Expand", "content_copy", "flag", "expand_more",
    "play_arrow", "copy", "thumb_up", "thumb_down", "more_vert", "edit",
    "Google Privacy Policy Opens in a new window |", "Google Privacy Policy",
    "Opens in a new window", "|",
    "Google Terms of Service Opens in a new window |",
    "Google Terms of Service",
    "Your privacy & Gemini Apps Opens in a new window",
    "Your privacy & Gemini Apps",
    "Gemini may display inaccurate info, including about people, so double-check its responses.",
}

def should_skip(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    if t in NOISE_EXACT:
        return True
    if t.startswith("http") or t.startswith("/url:"):
        return True
    return False

line_re = re.compile(r'^\s*-?\s*(?:img|button|link|generic|heading|paragraph|list|listitem|text|strong|main)\b.*$')
text_re = re.compile(r'text:\s*(.*)$')
quoted_re = re.compile(r'"([^"]*)"')

def fix_mojibake(s: str) -> str:
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s

def main(path, out_path):
    with open(path, encoding="utf-8") as f:
        lines = [fix_mojibake(line) for line in f.readlines()]

    out = []
    in_snapshot = False
    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        if stripped.startswith("Snapshot:"):
            in_snapshot = True
            continue
        if not in_snapshot:
            continue

        m = text_re.search(stripped)
        if m:
            frag = m.group(1).strip()
            if not should_skip(frag):
                out.append(("text", frag))
            continue

        hm = re.match(r'^-?\s*heading\s+"([^"]*)"\s*\[level=(\d+)\]', stripped)
        if hm:
            out.append(("heading", int(hm.group(2)), hm.group(1)))
            continue

        # "You said" / role headings without quotes captured separately via text already

    # Now render
    rendered = []
    buf = []

    def flush():
        if buf:
            para = " ".join(buf)
            para = re.sub(r'\s+([.,:;)])', r'\1', para)
            para = re.sub(r'\s+', ' ', para).strip()
            if para:
                rendered.append(para)
            buf.clear()

    for item in out:
        if item[0] == "heading":
            flush()
            level, text = item[1], item[2]
            rendered.append("\n" + ("#" * min(level + 1, 6)) + " " + text + "\n")
        else:
            buf.append(item[1])
    flush()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(rendered))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
