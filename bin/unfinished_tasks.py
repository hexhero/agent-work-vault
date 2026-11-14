#!/usr/bin/env python3
"""从 task/YYYY-MM-DD.md 每日任务日志里捞出未完成的任务。

状态写在复选框里：[ ] 未开始、[/] 进行中、[?] Review、[!] Block、[x] 已完成、[-] 已取消。
除已完成和已取消以外都算未完成。

用法:
  bin/unfinished_tasks.py                 # 列出所有未完成任务
  bin/unfinished_tasks.py -s doing -s blocked   # 只看进行中和 Block 的
  bin/unfinished_tasks.py -d              # 连同任务下面的补充说明一起列出
  bin/unfinished_tasks.py --since 2026-10-01 --until 2026-10-07
  bin/unfinished_tasks.py --json          # JSON 输出，方便其他脚本用
  bin/unfinished_tasks.py --ref PROJ-123 --ref PROJ-456   # 按工单号反查条目（含已完成、已取消）
  bin/unfinished_tasks.py -p demo               # 只看链到某个项目文件的未完成任务
  bin/unfinished_tasks.py --id T-8        # 按内部编号查条目（含已完成、已取消），可重复
  bin/unfinished_tasks.py --next-id       # 下一个可用的内部编号
  bin/unfinished_tasks.py --reporter AliceChen    # 只看某个报告人派的未完成任务，可重复
  bin/unfinished_tasks.py --type message          # 只看某个类型（#type/message）的未完成任务，可重复
  bin/unfinished_tasks.py -a --type message --reporter BobLi   # -a 连已完成、已取消的一起列
"""

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASK_DIR = ROOT / "task"
PROJECT_DIR = ROOT / "projects"
LOG_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")
CHECKBOX = re.compile(r"^(\s*)- \[(.)\] (.*)$")
TIME_PREFIX = re.compile(r"^(\d{1,2}:\d{2})\s+(.*)$")
# 内部编号：写在时间后面、主题前面（T-8）；已完成的条目中间可能隔着结束时间（- 11:30）
TASK_ID = re.compile(r"^(-\s*\d{1,2}:\d{2}\s+)?(T-\d+)\s+(.*)$")
# 报告人：任务行末尾的标签 #reporter/AliceChen（谁派的、做完向谁报告），自己起的任务不写
REPORTER = re.compile(r"(?:^|\s)#reporter/([^\s#]+)")
# 类型：任务行末尾的标签 #type/message（这条任务是哪一类，见 daily-log「类型标签」）
TYPE = re.compile(r"(?:^|\s)#type/([^\s#]+)")
# 工单号：ClickUp 风格的自定义 ID（PROJ-123）或链接里的原始 ID（app.clickup.com/t/86e3fzm03）
CUSTOM_ID = re.compile(r"\b[A-Z][A-Z0-9]{1,5}-\d{2,}\b")
RAW_ID = re.compile(r"app\.clickup\.com/t/(?:\d+/)?([A-Za-z0-9]+)(?![\w/-])")
# 项目链接：主题里的链接，或下面「项目：」行里的链接
PROJECT_LINK = re.compile(r"\]\((?:\.\./)*projects/([a-z0-9-]+)\.md\)")

# 复选框字符 -> (状态键, 中文名)
STATUSES = {
    " ": ("todo", "未开始"),
    "/": ("doing", "进行中"),
    "?": ("review", "Review"),
    "!": ("blocked", "Block"),
    "x": ("done", "已完成"),
    "X": ("done", "已完成"),
    "-": ("cancelled", "已取消"),
}
CLOSED = {"done", "cancelled"}
OPEN_KEYS = [k for k, _ in STATUSES.values() if k not in CLOSED]


def status_of(mark):
    """未登记的字符（如 Task Board 的 <）按「其他」算，也算未完成。"""
    return STATUSES.get(mark, ("other", f"其他({mark})"))


def indent_width(line):
    return len(line) - len(line.lstrip(" \t"))


def refs_of(text):
    """按出现顺序去重，返回文本里提到的 ClickUp 编号。"""
    found = [m.group(0) for m in CUSTOM_ID.finditer(text)]
    found += [m.group(1) for m in RAW_ID.finditer(text)]
    return list(dict.fromkeys(found))


def reporter_name(tag):
    """AliceChen -> Alice Chen。"""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", tag) if tag else None


def projects_of(text):
    return list(dict.fromkeys(PROJECT_LINK.findall(text)))


def parse_log(path, date, include_closed=False):
    """返回该日志里所有未完成任务，包括嵌在子列表里的子任务。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    tasks = []
    for i, line in enumerate(lines):
        m = CHECKBOX.match(line)
        if not m:
            continue
        mark = m.group(2)
        status, label = status_of(mark)
        if status in CLOSED and not include_closed:
            continue
        indent, text = indent_width(line), m.group(3).strip()
        t = TIME_PREFIX.match(text)
        start, title = (t.group(1), t.group(2)) if t else (None, text)
        tid = None
        k = TASK_ID.match(title)
        if k:
            tid, title = k.group(2), (k.group(1) or "") + k.group(3)
        r = REPORTER.search(title)
        reporter = r.group(1) if r else None
        title = REPORTER.sub("", title).strip()
        ty = TYPE.search(title)
        kind = ty.group(1) if ty else None
        title = TYPE.sub("", title).strip()

        # 补充说明：紧跟在后面、缩进更深的行
        detail = []
        for nxt in lines[i + 1:]:
            if nxt.strip() and indent_width(nxt) <= indent:
                break
            detail.append(nxt)
        while detail and not detail[-1].strip():
            detail.pop()
        detail = textwrap.dedent("\n".join(detail)).splitlines()

        tasks.append({
            "date": date,
            "line": i + 1,
            "mark": mark,
            "status": status,
            "status_label": label,
            "start": start,
            "id": tid,
            "title": title,
            "reporter": reporter,
            "type": kind,
            "nested": indent > 0,
            "detail": detail,
            # 标题里的编号排前面：通常是这条任务对应的主单
            "refs": refs_of(title + "\n" + "\n".join(detail)),
            "projects": projects_of(title + "\n" + "\n".join(detail)),
        })
    return tasks


def collect(since=None, until=None, statuses=None, include_closed=False):
    tasks = []
    for path in sorted(TASK_DIR.glob("*.md")):
        m = LOG_NAME.match(path.name)
        if not m:
            continue
        date = m.group(1)
        if (since and date < since) or (until and date > until):
            continue
        tasks.extend(t for t in parse_log(path, date, include_closed)
                     if not statuses or t["status"] in statuses)
    return tasks


def next_id():
    """所有日志（含已完成、已取消）里最大的内部编号加一。"""
    used = [int(t["id"][2:]) for t in collect(include_closed=True) if t["id"]]
    return f"T-{max(used, default=0) + 1}"


def main():
    parser = argparse.ArgumentParser(description="列出 task/ 日志里未完成的任务")
    parser.add_argument("--since", metavar="YYYY-MM-DD", help="只看这天及之后的日志")
    parser.add_argument("--until", metavar="YYYY-MM-DD", help="只看这天及之前的日志")
    parser.add_argument("-s", "--status", action="append", choices=OPEN_KEYS + ["other"],
                        help="只看某种状态，可重复：todo 未开始 / doing 进行中 / review Review / blocked Block / other 其他")
    parser.add_argument("-d", "--detail", action="store_true", help="同时输出任务下面的补充说明")
    parser.add_argument("--ref", action="append", metavar="ID",
                        help="只看提到这个 ClickUp 编号的条目（含已完成、已取消），可重复")
    parser.add_argument("-p", "--project", action="append", metavar="NAME",
                        help="只看链到这个项目的任务，NAME 是 projects/ 下的文件名（不带 .md），可重复")
    parser.add_argument("--id", action="append", metavar="T-N", dest="ids",
                        help="只看这个内部编号的条目（含已完成、已取消），可重复")
    parser.add_argument("--reporter", action="append", metavar="NAME",
                        help="只看这个报告人的任务，NAME 是 #reporter/ 后面的写法（AliceChen），不分大小写，可重复")
    parser.add_argument("--type", action="append", metavar="TYPE", dest="types",
                        help="只看这个类型的任务，TYPE 是 #type/ 后面的写法（message），可重复")
    parser.add_argument("-a", "--all", action="store_true",
                        help="连已完成、已取消的一起列（--ref、--id 本来就含）")
    parser.add_argument("--next-id", action="store_true", help="输出下一个可用的内部编号")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = parser.parse_args()

    if args.next_id:
        print(next_id())
        return

    if args.ids:
        wanted_ids = {i.upper() for i in args.ids}
        tasks = [t for t in collect(args.since, args.until, include_closed=True) if t["id"] in wanted_ids]
    elif args.project:
        names = {n.removesuffix(".md") for n in args.project}
        missing = sorted(n for n in names if not (PROJECT_DIR / f"{n}.md").exists())
        if missing:
            known = ", ".join(sorted(f.stem for f in PROJECT_DIR.glob("*.md") if f.stem != "README"))
            sys.exit(f"projects/ 下没有：{', '.join(missing)}\n可选：{known}")
        tasks = [t for t in collect(args.since, args.until, args.status, args.all)
                 if names & set(t["projects"])]
    elif args.ref:
        wanted = set(args.ref)
        tasks = [t for t in collect(args.since, args.until, include_closed=True)
                 if wanted & set(t["refs"])]
    else:
        tasks = collect(args.since, args.until, args.status, args.all)

    if args.reporter:
        who = {n.removeprefix("#reporter/").replace(" ", "").lower() for n in args.reporter}
        tasks = [t for t in tasks if (t["reporter"] or "").lower() in who]

    if args.types:
        kinds = {n.removeprefix("#type/").lower() for n in args.types}
        tasks = [t for t in tasks if (t["type"] or "").lower() in kinds]

    if args.json:
        json.dump(tasks, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return

    if not tasks:
        print("没有这些编号的条目" if (args.ref or args.ids) and not args.project
              else "没有符合条件的任务" if args.all else "没有未完成的任务")
        return

    current = None
    for t in tasks:
        if t["date"] != current:
            if current is not None:
                print()
            current = t["date"]
            print(f"== {current}  (task/{current}.md)")
        prefix = "  " + ("  └ " if t["nested"] else "")
        when = f"{t['start']} " if t["start"] else ""
        # 已完成的条目标题以结束时间（- 11:30）开头，编号排在它后面，和日志里的写法一致
        end = re.match(r"^-\s*\d{1,2}:\d{2}\s+", t["title"])
        head, rest = (end.group(0), t["title"][end.end():]) if end else ("", t["title"])
        tid = f"{t['id']} " if t["id"] else ""
        who_tag = (f" #type/{t['type']}" if t["type"] else "") + (f" #reporter/{t['reporter']}" if t["reporter"] else "")
        print(f"{prefix}[{t['mark']}] {t['status_label']}  {when}{head}{tid}{rest}{who_tag}  :{t['line']}")
        if args.ref:
            print(f"      提到：{', '.join(r for r in t['refs'] if r in wanted)}")
        if args.detail:
            for d in t["detail"]:
                print(f"      {d}".rstrip())
    counts = {}
    for t in tasks:
        counts[t["status_label"]] = counts.get(t["status_label"], 0) + 1
    summary = "，".join(f"{k} {v}" for k, v in counts.items())
    print(f"\n共 {len(tasks)} 条{'' if args.ref or args.ids or args.all else '未完成'}（{summary}）")


if __name__ == "__main__":
    main()
