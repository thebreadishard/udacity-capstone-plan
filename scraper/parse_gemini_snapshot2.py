"""One-off helper: convert a Playwright accessibility-tree snapshot dump (as
produced by the read_page tool) into a readable markdown transcript of a
shared Gemini chat. Not part of the regular scraper pipeline.

This is v2 of parse_gemini_snapshot.py: it additionally captures inline
subscript/symbol fragments that live in bare `generic [ref=...]: content`
nodes (e.g. formula subscripts like the "2" in H2O, or math symbols), which
the original v1 parser dropped entirely because it only matched `text:`
prefixed lines. It also inserts a paragraph break at every paragraph/listitem
boundary (instead of only at headings) and emits explicit "### You said" /
"### Gemini said" speaker markers at turn boundaries.
"""
import re
import sys

NOISE_EXACT = {
    "New chat", "Gemini", "About Gemini link", "About Gemini",
    "Get Gemini app link", "Get Gemini App", "Subscriptions link",
    "Subscriptions", "For Business link", "For Business", "Sign in",
    "Expand", "content_copy", "flag", "expand_more",
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
    if t.startswith("Created with") or t.startswith("• Published"):
        return True
    return False


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


heading_quoted_re = re.compile(r'^-?\s*\'?heading\s+"((?:[^"\\]|\\.)*)"\s*\[level=(\d+)\]')
heading_bare_re = re.compile(r'^-?\s*heading\s+\[level=(\d+)\]\s*\[ref=')
para_quoted_re = re.compile(r'^-?\s*(?:paragraph|listitem)\s+"((?:[^"\\]|\\.)*)"\s*\[ref=')
para_colon_re = re.compile(r'^-?\s*(?:paragraph|listitem)\s+\[ref=[^\]]*\]:\s*(.*)$')
para_bare_re = re.compile(r'^-?\s*(?:paragraph|listitem)\s+\[ref=[^\]]*\]:?\s*$')
text_re = re.compile(r'^-?\s*text:\s*(.*)$')
simple_generic_re = re.compile(r'^-?\s*generic\s+\[ref=[^\]]*\]:\s*(.*)$')
copy_prompt_re = re.compile(r'^-?\s*button\s+"Copy prompt"')


def main(path, out_path):
    with open(path, encoding="utf-8") as f:
        lines = [fix_mojibake(line.rstrip("\n")) for line in f.readlines()]

    out = []  # list of tuples: ("speaker", name) | ("heading", level, text) | ("break",) | ("text", frag)
    in_snapshot = False
    awaiting_speaker_label = False
    pending_dupe_check = None  # user-prompt text that may be repeated in the next paragraph

    for raw in lines:
        stripped = raw.strip()
        if stripped.startswith("Snapshot:"):
            in_snapshot = True
            continue
        if not in_snapshot:
            continue

        if copy_prompt_re.match(stripped):
            pending_dupe_check = None
            out.append(("break",))
            out.append(("speaker", "Gemini"))
            continue

        hq = heading_quoted_re.match(stripped)
        if hq:
            title, level = hq.group(1), int(hq.group(2))
            if title.startswith("You said"):
                out.append(("break",))
                out.append(("speaker", "You"))
                rest = title[len("You said"):].strip()
                if rest:
                    out.append(("break",))
                    out.append(("text", rest))
                    pending_dupe_check = rest
            else:
                out.append(("heading", level, title))
            continue

        if heading_bare_re.match(stripped):
            out.append(("break",))
            awaiting_speaker_label = True
            continue

        pq = para_quoted_re.match(stripped)
        if pq:
            frag = pq.group(1).replace('\\"', '"').strip()
            is_dupe = pending_dupe_check is not None and frag == pending_dupe_check
            pending_dupe_check = None
            out.append(("break",))
            if not is_dupe and not should_skip(frag):
                out.append(("text", frag))
            out.append(("break",))
            continue

        if para_bare_re.match(stripped):
            pending_dupe_check = None
            out.append(("break",))
            continue

        pc = para_colon_re.match(stripped)
        if pc:
            frag = pc.group(1).strip()
            is_dupe = pending_dupe_check is not None and frag == pending_dupe_check
            pending_dupe_check = None
            out.append(("break",))
            if not is_dupe and not should_skip(frag):
                out.append(("text", frag))
            out.append(("break",))
            continue

        tm = text_re.match(stripped)
        if tm:
            frag = tm.group(1).strip()
            if awaiting_speaker_label:
                awaiting_speaker_label = False
                if frag == "You said":
                    out.append(("speaker", "You"))
                    continue
            if not should_skip(frag):
                out.append(("text", frag))
            continue

        gm = simple_generic_re.match(stripped)
        if gm:
            frag = gm.group(1).strip()
            if awaiting_speaker_label:
                awaiting_speaker_label = False
                if frag == "You said":
                    out.append(("speaker", "You"))
                    continue
            if frag and not should_skip(frag):
                out.append(("text", frag))
            continue

    # Render
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
        kind = item[0]
        if kind == "break":
            flush()
        elif kind == "speaker":
            flush()
            rendered.append(f"\n### {item[1]} said\n")
        elif kind == "heading":
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
