"""Zenodo deposition for paper D (decision 56; the user, 3 Oct 2026: "Ik heb me inmiddels aangemeld bij Zenodo"). Creates and fills a DRAFT record
with a reserved DOI; it never publishes — publishing is irreversible and stays the user's click on the Zenodo website.

The token is read from the environment (`ZENODO_TOKEN`, or `ZENODO_SANDBOX_TOKEN` with --sandbox) or, failing that, from the `.env` file at the
repository root (git-ignored). The value is never printed, logged or written anywhere.

    python tools/zenodo_deposit.py create   tools/zenodo/metadata_paper_D.json [--sandbox]        # new draft; prints record id, concept DOI, reserved DOI
    python tools/zenodo_deposit.py upload   <record id> <file> [<file> ...] [--sandbox]           # PUT files into the draft's bucket (sha256 shown per file)
    python tools/zenodo_deposit.py metadata <record id> tools/zenodo/metadata_paper_D.json [--sandbox]   # update the draft's metadata
    python tools/zenodo_deposit.py status   <record id> [--sandbox]                              # state, DOI, files
    python tools/zenodo_deposit.py newversion <record id> [--sandbox]                            # open a new draft version of a published record

Uses only the standard library (urllib), so it runs in any of our environments. API: https://developers.zenodo.org (deposition endpoints).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib import error, parse, request

REPO = Path(__file__).resolve().parents[3]          # tools/ → plan → plans/ → the repository root, where the git-ignored .env lives
HOSTS = {False: "https://zenodo.org", True: "https://sandbox.zenodo.org"}


def read_token(sandbox: bool) -> str:
    """The token from the environment or the git-ignored .env at the repository root; never echoed."""
    name = "ZENODO_SANDBOX_TOKEN" if sandbox else "ZENODO_TOKEN"
    val = os.environ.get(name)
    if not val:
        env = REPO / ".env"
        if env.exists():
            for ln in env.read_text(encoding="utf-8-sig").splitlines():
                ln = ln.strip()
                if ln.startswith(name + "="):
                    val = ln.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not val:
        raise SystemExit(f"{name} not set (environment or {env}); create it on Zenodo under Applications → Personal access tokens")
    return val


def call(method: str, url: str, token: str, body: bytes | None = None, content_type: str = "application/json") -> dict | list:
    req = request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        req.add_header("Content-Type", content_type)
    try:
        with request.urlopen(req, timeout=600) as r:
            text = r.read().decode("utf-8")
            return json.loads(text) if text else {}
    except error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:600]
        raise SystemExit(f"Zenodo {method} {url.split('?')[0]} → HTTP {e.code}: {detail}") from None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_metadata(path: Path) -> dict:
    md = json.load(open(path, encoding="utf-8"))
    assert "metadata" in md, f"{path}: top-level key 'metadata' expected (Zenodo deposition metadata)"
    m = md["metadata"]
    for key in ("title", "upload_type", "description", "creators", "license", "access_right"):
        assert key in m, f"{path}: metadata.{key} missing"
    return md


def cmd_create(a, token, host):
    md = load_metadata(Path(a.metadata))
    rec = call("POST", f"{host}/api/deposit/depositions", token, json.dumps(md).encode("utf-8"))
    print(f"draft created: id {rec['id']}; state {rec.get('state')}; concept DOI {rec.get('conceptdoi', '—')}; reserved DOI {rec.get('metadata', {}).get('prereserve_doi', {}).get('doi', '—')}")
    print(f"edit on the website: {rec['links'].get('html', '')}")
    return 0


def cmd_metadata(a, token, host):
    md = load_metadata(Path(a.metadata))
    rec = call("PUT", f"{host}/api/deposit/depositions/{a.record}", token, json.dumps(md).encode("utf-8"))
    print(f"metadata updated: id {rec['id']}; state {rec.get('state')}; title {rec['metadata'].get('title', '')[:80]}")
    return 0


def cmd_upload(a, token, host):
    rec = call("GET", f"{host}/api/deposit/depositions/{a.record}", token)
    bucket = rec["links"]["bucket"]
    for f in a.files:
        p = Path(f)
        if not p.exists():
            raise SystemExit(f"no such file: {p}")
        digest = sha256(p)
        with open(p, "rb") as fh:
            data = fh.read()
        out = call("PUT", f"{bucket}/{parse.quote(p.name)}", token, data, content_type="application/octet-stream")
        remote = out.get("checksum", "")
        ok = remote.endswith(hashlib.md5(data).hexdigest()) if remote.startswith("md5:") else True
        print(f"uploaded {p.name}: {p.stat().st_size:,} bytes; sha256 {digest[:16]}…; remote checksum {'matches' if ok else 'MISMATCH'}")
    return 0


def cmd_status(a, token, host):
    rec = call("GET", f"{host}/api/deposit/depositions/{a.record}", token)
    print(f"id {rec['id']}; state {rec.get('state')}; submitted {rec.get('submitted')}; DOI {rec.get('doi') or rec.get('metadata', {}).get('prereserve_doi', {}).get('doi', '—')}; concept DOI {rec.get('conceptdoi', '—')}")
    for f in rec.get("files", []):
        print(f"  file {f.get('filename')}: {f.get('filesize', 0):,} bytes; checksum {f.get('checksum', '')}")
    print(f"website: {rec['links'].get('html', '')}")
    return 0


def cmd_newversion(a, token, host):
    rec = call("POST", f"{host}/api/deposit/depositions/{a.record}/actions/newversion", token)
    latest = rec["links"].get("latest_draft", "")
    print(f"new version draft: {latest} (edit metadata and files there; publishing stays the user's click)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sandbox", action="store_true", help="use sandbox.zenodo.org with ZENODO_SANDBOX_TOKEN")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("create"); s.add_argument("metadata"); s.set_defaults(fn=cmd_create)
    s = sub.add_parser("metadata"); s.add_argument("record"); s.add_argument("metadata"); s.set_defaults(fn=cmd_metadata)
    s = sub.add_parser("upload"); s.add_argument("record"); s.add_argument("files", nargs="+"); s.set_defaults(fn=cmd_upload)
    s = sub.add_parser("status"); s.add_argument("record"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("newversion"); s.add_argument("record"); s.set_defaults(fn=cmd_newversion)
    a = ap.parse_args(argv)
    token = read_token(a.sandbox)
    return a.fn(a, token, HOSTS[a.sandbox])


if __name__ == "__main__":
    sys.exit(main())
