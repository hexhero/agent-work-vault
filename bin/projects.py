#!/usr/bin/env python3
"""列出 projects/ 下的项目：读每个项目文件 frontmatter 里的 name 和 description（和读 skill 的方式一样）。

不用读正文就能知道有哪些项目、各是什么，再决定去读哪个项目文件。

用法:
  bin/projects.py                 # 每个项目一行：name — description
  bin/projects.py -v              # 加上别名、仓库、主机、文件路径、同名目录里的文件
  bin/projects.py demo api        # 按关键词筛选（匹配 name、别名、description，不分大小写，满足任一个）
  bin/projects.py --json          # JSON 输出，方便其他脚本用
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_DIR = ROOT / "projects"


def frontmatter(text: str) -> dict[str, object]:
    """极简 YAML：只认顶层 `key: value` 和 `- item` 列表。"""
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    fm: dict[str, object] = {}
    key = None
    for line in text[4:end].split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            fm[key] = val.strip('"') if val else []
        elif key and re.match(r"^\s+-\s+", line):
            if not isinstance(fm[key], list):
                fm[key] = []
            fm[key].append(re.sub(r"^\s+-\s+", "", line).strip().strip('"'))
    return fm


def as_list(v: object) -> list[str]:
    return v if isinstance(v, list) else ([v] if v else [])


def load() -> list[dict]:
    out = []
    for p in sorted(PROJECT_DIR.glob("*.md")):
        if p.name == "README.md":
            continue
        fm = frontmatter(p.read_text())
        sub = PROJECT_DIR / p.stem
        out.append({
            "name": fm.get("name") or p.stem,
            "description": fm.get("description") or "",
            "aliases": as_list(fm.get("aliases")),
            "repo": as_list(fm.get("repo")),
            "hosts": as_list(fm.get("hosts")),
            "file": str(p.relative_to(ROOT)),
            "docs": sorted(str(f.relative_to(ROOT)) for f in sub.glob("*.md")) if sub.is_dir() else [],
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("keywords", nargs="*", help="关键词，匹配 name、别名、description")
    ap.add_argument("-v", "--verbose", action="store_true", help="加上别名、仓库、主机、文件路径、同名目录里的文件")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    projects = load()
    if args.keywords:
        kws = [k.lower() for k in args.keywords]
        projects = [p for p in projects
                    if any(k in " ".join([p["name"], p["description"], *p["aliases"]]).lower() for k in kws)]
    if args.json:
        print(json.dumps(projects, ensure_ascii=False, indent=2))
        return 0
    if not projects:
        print("没有匹配的项目。", file=sys.stderr)
        return 1
    for p in projects:
        print(f"{p['name']} — {p['description'] or '（没写 description）'}")
        if args.verbose:
            for label, key in (("别名", "aliases"), ("仓库", "repo"), ("主机", "hosts"), ("资料", "docs")):
                if p[key]:
                    print(f"    {label}：{'、'.join(p[key])}")
            print(f"    文件：{p['file']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
