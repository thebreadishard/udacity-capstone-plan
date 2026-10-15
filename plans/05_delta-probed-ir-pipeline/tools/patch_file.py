r"""patch_file — the shared helper promised on 14 September 2026 (QUALITY_POLICY, incident → guard): exact-string edits with an assertion on every
anchor, the whole new text built in memory, then `os.replace` of a temp file over the original. The target is never opened for writing before
every assertion has passed (a probe script was emptied that way on 14 September).

New text may not carry control characters other than a newline unless the caller says so (`controls=True`): a backslash path or a regex
written through a bash heredoc or a non-raw Python string turns \t, \b, \f, \a, \v into a tab, a backspace, … (3–4 Oct and twice on
11 Oct 2026: a log path in TASKS lost its 't' to a tab). In patch(), a control character that the anchor itself carries is allowed.

Library:  from patch_file import patch, append, insert_after_line
    patch(path, [(old, new), ...], count=1)   # every old must occur exactly `count` times; no control characters in new
                                              # (controls=True to allow; append and insert_after_line take it too)
    append(path, text)                        # text after the file's last non-empty line
    insert_after_line(path, needle, text)     # after the single line that contains needle
    patch_many({path: [(old, new), ...], ...})  # every anchor in every file checked before any file is written
CLI:      python patch_file.py <target> <edits.json>     with [{"old": "...", "new": "..."}, ...]   (exit 1 and no write if any anchor fails)
"""
import json
import os
import re
import sys

_CONTROLS = re.compile(r"[\x00-\x09\x0b-\x1f\x7f]")   # every C0 control and DEL except the newline


def _write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def _check_controls(path, new, old=""):
    bad = sorted({c for c in _CONTROLS.findall(new) if c not in old})
    if bad:
        raise AssertionError(f"{path}: new text carries control characters {bad} (a mangled escape?); pass controls=True if intended")


def _patched(path, edits, count=1, controls=False):
    """The text of `path` with `edits` applied, after every check; raises before anything is written."""
    if not controls:
        for old, new in edits:
            _check_controls(path, new, old)
    text = open(path, encoding="utf-8").read()
    problems = [(old[:60], text.count(old)) for old, _ in edits if text.count(old) != count]
    if problems:
        raise AssertionError(f"{path}: anchors not matching exactly {count} time(s): {problems}")
    for old, new in edits:
        text = text.replace(old, new)
    return text


def patch(path, edits, count=1, controls=False):
    _write(path, _patched(path, edits, count, controls))
    return len(edits)


def patch_many(plan, count=1, controls=False):
    """{path: edits}: every file's anchors are checked and every new text built before the first file is written (15 Oct 2026: a four-file
    patch wrote three files and stopped at the fourth). Returns the number of edits."""
    texts = {path: _patched(path, edits, count, controls) for path, edits in plan.items()}
    for path, text in texts.items():
        _write(path, text)
    return sum(len(e) for e in plan.values())


def append(path, text, controls=False):
    if not controls:
        _check_controls(path, text)
    body = open(path, encoding="utf-8").read().rstrip("\n") + "\n" + text
    _write(path, body)


def insert_after_line(path, needle, text, controls=False):
    if not controls:
        _check_controls(path, text)
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
