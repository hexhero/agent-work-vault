#!/usr/bin/env python3
"""Watcher: met when a URL responds with the expected status and its body contains some text.

  http_contains.py URL TEXT [TEXT ...] [--status 200] [--all] [--header "Name: value"]

Exit 0 = met (prints the matching lines), 1 = not yet, 2 = error.
Examples: wait for a release page to list v1.4; wait for a health endpoint to say "ok".
For pages that need a token, write your own watcher that reads it from asset/config.yaml;
never put secrets in the --check command (it is stored in task/follow-up.json).
"""
import argparse
import sys
import urllib.error
import urllib.request


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("text", nargs="+", help="text to look for (case-insensitive); any of them, or all with --all")
    ap.add_argument("--status", type=int, default=200, help="expected HTTP status (default 200)")
    ap.add_argument("--all", action="store_true", help="require every TEXT")
    ap.add_argument("--header", action="append", default=[], help='extra request header "Name: value"')
    a = ap.parse_args()
    req = urllib.request.Request(a.url, headers={"User-Agent": "follow-up-watcher"})
    for h in a.header:
        k, _, v = h.partition(":")
        req.add_header(k.strip(), v.strip())
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            status, body = r.status, r.read(2_000_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read(200_000).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as e:
        print(f"request failed: {e}")
        return 2
    if status != a.status:
        print(f"HTTP {status} (waiting for {a.status})")
        return 1
    low = body.lower()
    hits = [t for t in a.text if t.lower() in low]
    if (a.all and len(hits) == len(a.text)) or (not a.all and hits):
        lines = [l.strip() for l in body.splitlines() if any(t.lower() in l.lower() for t in hits)]
        print(f"HTTP {status}, found: {', '.join(hits)}")
        print("\n".join(lines[:20])[:3000])
        return 0
    print(f"HTTP {status}, not found yet: {', '.join(t for t in a.text if t not in hits)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
