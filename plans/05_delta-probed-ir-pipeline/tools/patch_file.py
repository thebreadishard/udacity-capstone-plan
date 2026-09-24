"""patch_file — the shared helper promised on 14 September 2026 (QUALITY_POLICY, incident → guard): exact-string edits with an assertion on every
anchor, the whole new text built in memory, then `os.replace` of a temp file over the original. The target is never opened for writing before
every assertion has passed (a probe script was emptied that way on 14 September).

Library:  from patch_file import patch, append, insert_after_line
    patch(path, [(old, new), ...], count=1)   # every old must occur exactly `count` times
    append(path, text)                        # text after the file's last non-empty line
    insert_after_line(path, needle, text)     # after the single line that contains needle
CLI:      python patch_file.py <target> <edits.json>     with [{"old": "...", "new": "..."}, ...]   (exit 1 and no write if any anchor fails)
"""
import json
import os
import sys


def _write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def patch(path, edits, count=1):
    text = open(path, encoding="utf-8").read()
    problems = [(old[:60], text.count(old)) for old, _ in edits if text.count(old) != count]
    if problems:
        raise AssertionError(f"{path}: anchors not matching exactly {count} time(s): {problems}")
    for old, new in edits:
        text = text.replace(old, new)
    _write(path, text)
    return len(edits)


def append(path, text):
    body = open(path, encoding="utf-8").read().rstrip("\n") + "\n" + text
    _write(path, body)


def insert_after_line(path, needle, text):
    lines = open(path, encoding="utf-8").read().split("\n")
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise AssertionError(f"{path}: needle {needle[:60]!r} found {len(hits)} times, need exactly 1")
    lines.insert(hits[0] + 1, text)
    _write(path, "\n".join(lines))


def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(2)
    target, edits_p = sys.argv[1], sys.argv[2]
    edits = [(e["old"], e["new"]) for e in json.load(open(edits_p, encoding="utf-8"))]
    try:
        n = patch(target, edits)
    except AssertionError as e:
        print("no write:", e); sys.exit(1)
    print(f"{n} edit(s) applied to {target}")


if __name__ == "__main__":
    main()
