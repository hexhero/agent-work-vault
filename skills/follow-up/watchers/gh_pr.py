#!/usr/bin/env python3
"""Watcher: a GitHub pull request reached a state, got approved, or got a new comment. Needs the GitHub CLI (`gh`), logged in.

  gh_pr.py OWNER/REPO NUMBER [--state merged|closed|open ...] [--approved] [--comment-by LOGIN ...] [--comment-has WORD ...]

Any of the given conditions is enough. New comments only count when made after the item was added
(FOLLOWUP_SINCE, set by follow.py). Exit 0 = met (prints what happened), 1 = not yet, 2 = error.
"""
import argparse
import json
import os
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", help="OWNER/REPO")
    ap.add_argument("number")
    ap.add_argument("--state", nargs="+", choices=["merged", "closed", "open"], help="met when the PR is in one of these states")
    ap.add_argument("--approved", action="store_true", help="met when the review decision is APPROVED")
    ap.add_argument("--comment-by", nargs="+", help="met when one of these logins comments (after the item was added)")
    ap.add_argument("--comment-has", nargs="+", help="met when a new comment contains one of these words")
    a = ap.parse_args()
    if not (a.state or a.approved or a.comment_by or a.comment_has):
        ap.error("give at least one of --state / --approved / --comment-by / --comment-has")
    try:
        p = subprocess.run(["gh", "pr", "view", a.number, "--repo", a.repo, "--json",
                            "state,title,url,reviewDecision,comments,reviews"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"gh failed: {e}")
        return 2
    if p.returncode:
        print(f"gh failed: {p.stderr.strip()[:500]}")
        return 2
    pr = json.loads(p.stdout)
    since = os.environ.get("FOLLOWUP_SINCE", "")
    hits = []
    if a.state and pr["state"].lower() in a.state:
        hits.append(f"state is {pr['state']}")
    if a.approved and pr.get("reviewDecision") == "APPROVED":
        hits.append("review decision is APPROVED")
    if a.comment_by or a.comment_has:
        notes = [{"author": c["author"]["login"], "at": c["createdAt"], "body": c["body"]} for c in pr.get("comments", [])]
        notes += [{"author": r["author"]["login"], "at": r.get("submittedAt") or "", "body": r.get("body") or ""}
                  for r in pr.get("reviews", []) if r.get("body")]
        for n in sorted(notes, key=lambda n: n["at"]):
            if since and n["at"] <= since:
                continue
            by = not a.comment_by or n["author"].lower() in [x.lower() for x in a.comment_by]
            has = not a.comment_has or any(w.lower() in n["body"].lower() for w in a.comment_has)
            if by and has:
                hits.append(f"{n['at']} {n['author']} commented: {n['body'][:500]}")
    head = f"{pr['url']} {pr['title']} (state {pr['state']}, review {pr.get('reviewDecision') or 'none'})"
    print(head)
    if hits:
        print("\n".join(hits))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
