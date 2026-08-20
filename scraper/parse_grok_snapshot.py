"""One-off helper: convert a Playwright accessibility-tree snapshot dump (as
produced by the read_page tool) into a readable markdown transcript of a
shared Grok conversation. Not part of the regular scraper pipeline.
"""
import re
import sys

NOISE_EXACT = {
    "Skip to main content", "Home page", "Settings", "Sign in", "Sign up",
    "Copy", "Report",
}


def should_skip(text: str) -> bool:
    t = text.strip()
    if not t:
        return True
    if t in NOISE_EXACT:
        return True
    if t.startswith("http") or t.startswith("/url:"):
        return True
    if re.match(r'^Worked for .*$', t):
        return True
    return False


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("cp1252").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def main(path, out_path):
    with open(path, encoding="utf-8") as f:
        raw_lines = [fix_mojibake(line) for line in f.readlines()]

    lines = []
    in_snapshot = False
    for raw in raw_lines:
        line = raw.rstrip("\n")
        if line.strip().startswith("Snapshot:"):
            in_snapshot = True
            continue
        if in_snapshot:
            lines.append(line)

    out = []  # list of ("speaker"|"heading"|"text", ...)
    skip_until_indent = None  # used to skip inside math[] subtrees

    heading_re = re.compile(r'^-?\s*heading\s+"([^"]*)"\s*\[level=(\d+)\]')
    article_re = re.compile(r'^-?\s*article\s+"([^"]*)"')
    math_re = re.compile(r'^-?\s*math\b')
    quoted_leaf_re = re.compile(r'^-?\s*(?:paragraph|listitem)\s+"((?:[^"\\]|\\.)*)"\s*\[ref=')
    colon_leaf_re = re.compile(r'^-?\s*(?:paragraph|listitem)\s+\[ref=[^\]]*\]:\s*(.*)$')
    text_re = re.compile(r'^-?\s*text:\s*(.*)$')
    simple_generic_re = re.compile(r'^-?\s*generic\s+\[ref=[^\]]*\]:\s*(.*)$')

    for line in lines:
        stripped = line.strip()
        ind = indent_of(line)

        if skip_until_indent is not None:
            if stripped and ind > skip_until_indent:
                continue
            else:
                skip_until_indent = None

        if math_re.match(stripped):
            skip_until_indent = ind
            continue

        am = article_re.match(stripped)
        if am:
            out.append(("speaker", am.group(1)))
            continue

        hm = heading_re.match(stripped)
        if hm:
            out.append(("heading", int(hm.group(2)), hm.group(1)))
            continue

        qm = quoted_leaf_re.match(stripped)
        if qm:
            frag = qm.group(1).replace('\\"', '"').strip()
            if not should_skip(frag):
                out.append(("text", frag))
            continue

        cm = colon_leaf_re.match(stripped)
        if cm:
            frag = cm.group(1).strip()
            if not should_skip(frag):
                out.append(("text", frag))
            continue

        tm = text_re.match(stripped)
        if tm:
            frag = tm.group(1).strip()
            if not should_skip(frag):
                out.append(("text", frag))
            continue

        gm = simple_generic_re.match(stripped)
        if gm:
            frag = gm.group(1).strip()
            # Only keep short leaf fragments (single symbols/words), skip
            # anything that looks like a nested container description.
            if frag and len(frag) <= 40 and not should_skip(frag):
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
        if item[0] == "speaker":
            flush()
            rendered.append(f"\n### {item[1]} said\n")
        elif item[0] == "heading":
            flush()
            level, text = item[1], item[2]
            rendered.append("\n" + ("#" * min(level + 2, 6)) + " " + text + "\n")
        else:
            buf.append(item[1])
    flush()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(rendered))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
