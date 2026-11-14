#!/usr/bin/env python3
"""汇总某一天干了什么：各项目日志（projects/<项目>/log.md）当天的条目，加上每日日志里的任务和非项目事件。

项目相关的事只记在项目日志里，每日日志不重复记（见 skills/daily-log、skills/project-docs），
所以「今天干了什么」要两边合起来看。

用法:
  bin/day_summary.py                # 今天（时区见 bin/vault.py）
  bin/day_summary.py 2026-11-11     # 指定日期
  bin/day_summary.py -p demo        # 只看某个项目
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault  # noqa: E402

ROOT = vault.ROOT
LOG_RE = re.compile(r"^log(-\d{4}q[1-4])?\.md$")


def section(text: str, *headings: str) -> str:
    """取二级标题 headings（任一种写法）下面的内容（到下一个二级标题为止）。"""
    out, on = [], False
    for line in text.split("\n"):
        if line.startswith("## "):
            on = line.strip() in headings
            continue
        if on:
            out.append(line)
    return "\n".join(out).strip("\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("date", nargs="?", help="YYYY-MM-DD，默认今天（按配置的时区）")
    ap.add_argument("-p", "--project", help="只看某个项目（项目文件名，不带 .md）")
    args = ap.parse_args()
    date = args.date or vault.now().strftime("%Y-%m-%d")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        print(f"日期格式应为 YYYY-MM-DD：{date}", file=sys.stderr)
        return 2

    print(f"# {date}\n")
    found = False
    for d in sorted((ROOT / "projects").iterdir()):
        if not d.is_dir() or (args.project and d.name != args.project):
            continue
        for f in sorted(p for p in d.iterdir() if LOG_RE.match(p.name)):
            body = section(f.read_text(), f"## {date}")
            if body:
                found = True
                print(f"## 项目 {d.name}（projects/{d.name}/{f.name}）\n\n{body}\n")
    if not args.project:
        daily = ROOT / "task" / f"{date}.md"
        if daily.exists():
            text = daily.read_text()
            for key, _, _ in vault.DAILY_SECTIONS:
                heads = vault.daily_heading(key)
                body = section(text, *heads)
                if body:
                    found = True
                    name = next((h for h in heads if h in text.split("\n")), heads[0])[3:]
                    print(f"## 每日日志 · {name}（task/{date}.md）\n\n{body}\n")
    if not found:
        print("这一天没有记录。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
