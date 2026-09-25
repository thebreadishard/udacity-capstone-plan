"""Number audit of a consolidated reading copy against its sources (2026-09-16).

The reading copy of the proposal was drafted from the 6 September text plus dated decisions; the rule "measured, not
asserted" requires that no number appears in the copy that is not in a source. This script extracts every numeric token
(integers, decimals, ranges, percentages, times, with a little context) from the copy and looks for the same token in the
source files; tokens found nowhere are listed with their context for a human check.

Usage:  python check_reading_copy_numbers.py <copy.md> <source.md> [more sources...]
A token is "found" if the same digit string (commas and thin spaces removed) occurs in any source. Section numbers, years
in citations and line references are excluded by simple rules; the remainder is a reading list, not a verdict.
"""
import re
import sys

NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:[,   ]\d{3})+|\d+(?:\.\d+)?)(?![\w])")
SKIP_PREFIX = re.compile(r"(§|item|items|decision|decisions|P|X|R|T|M|Q|line|lines|module|Module|rung|Rung|§§)\s*-?$")


def norm(tok):
    return re.sub(r"[,   ]", "", tok)


def tokens(text):
    out = []
    for m in NUM.finditer(text):
        tok = m.group(1)
        pre = text[max(0, m.start() - 12):m.start()]
        post = text[m.end():m.end() + 14]
        if SKIP_PREFIX.search(pre.strip()[-10:] or ""):
            continue
        if re.match(r"^(19|20)\d\d$", tok) or re.match(r"^\d{1,2}$", tok) and not re.match(r"^\s*(%|cm|h\b|GB|min|s\b|µE|days|weeks|energies|modes|atoms|nodes)", post):
            # bare small integers and years are too common to audit; keep only if followed by a unit
            if re.match(r"^(19|20)\d\d$", tok) or not re.match(r"^\s*(%|cm|h\b|GB|min|s\b|µE|days|weeks|energies|modes|atoms|nodes|×)", post):
                continue
        ctx = (text[max(0, m.start() - 50):m.end() + 40]).replace("\n", " ")
        out.append((norm(tok), tok, ctx))
    return out


def main():
    if len(sys.argv) < 3:   # 25 Sep 2026: without sources every token is 'missing' and the run looks like a total failure
        sys.exit("usage: check_reading_copy_numbers.py <reading copy> <source files...>   e.g. README.md GoalGathering/notes/*.md modules/05_support_predictor/out/*.md probes/results_m1/*/REPORT.md")
    copy = open(sys.argv[1], encoding="utf-8").read()
    sources = "\n".join(open(p, encoding="utf-8").read() for p in sys.argv[2:])
    src_norm = re.sub(r"[,  ]", "", sources)
    seen, missing = set(), []
    for n, tok, ctx in tokens(copy):
        if n in seen:
            continue
        seen.add(n)
        if n not in src_norm:
            missing.append((tok, ctx))
    print(f"copy tokens audited: {len(seen)}; not found in any source: {len(missing)}\n")
    for tok, ctx in missing:
        print(f"- `{tok}`  …{ctx}…")


if __name__ == "__main__":
    main()
