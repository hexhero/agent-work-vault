#!/usr/bin/env python3
"""按 CLAUDE.md、skills/project-docs 和 skills/daily-log 的约定检查本仓库（Obsidian vault）的文档。

检查项：
  frontmatter  各目录文档的 type 和必填字段
  links        相对路径的 Markdown 链接、frontmatter 里的 [[双链]] 能不能找到目标
  no-task-link projects/ 下的文件不能链到 task/（项目日志 log.md 除外）
  index        docs 各 README 的索引有没有列全
  filename     projects/、task/details/ 的文件名
  size         projects/ 下的项目主文件超过 MAX_PROJECT_BYTES、Design（design*.md）超过 MAX_DESIGN_BYTES 时警告
  sections     已整理的项目主文件（有「## 位置」）的二级标题只能是固定小节，按固定顺序；没整理的汇总警告一条
  project-log  项目日志 log.md、log-YYYYqN.md 的二级标题只能是「## YYYY-MM-DD」，按日期倒序
  daily-log    每日日志的标题顺序、日志 / 事件段里不能有复选框、事件格式；任务下的子行超过 10 行给警告
  task-id      未完成的任务要有内部编号（T-N），编号不能重复；报告人标签 #reporter/AliceChen 的格式
  skills       调用 bin/sync_skills.py --check

用法：
  bin/lint_vault.py            # 有错误时退出码为 1，警告不影响退出码
  bin/lint_vault.py -q         # 只输出错误
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault  # noqa: E402

ROOT = vault.ROOT
# oss/ 是开源版的素材（导出后才是完整的仓库），i18n/、examples/ 是开源版里的另一种语言和示例，都不按本仓库的规则查
SKIP_DIRS = {".git", ".obsidian", ".claude", "temp", "node_modules", "oss", "i18n", "examples"}
DAILY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
MAX_SUBITEMS = 10
MAX_PROJECT_BYTES = 16_000
MAX_DESIGN_BYTES = 32_000
MAX_LOG_BYTES = 64_000
PROJECT_LOG_RE = re.compile(r"^log(-\d{4}q[1-4])?\.md$")
# 项目主文件的固定小节，中文、英文各一套（一个文件里用同一套）
PROJECT_SECTIONS_BY_LANG = [[s[1] for s in vault.PROJECT_SECTIONS], [s[2] for s in vault.PROJECT_SECTIONS]]
unsorted_projects: list[str] = []

errors: list[str] = []
warnings: list[str] = []


def err(path: Path, line: int | None, check: str, msg: str) -> None:
    errors.append(f"{rel(path)}{f':{line}' if line else ''}  [{check}] {msg}")


def warn(path: Path, line: int | None, check: str, msg: str) -> None:
    warnings.append(f"{rel(path)}{f':{line}' if line else ''}  [{check}] {msg}")


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


def md_files() -> list[Path]:
    out = []
    for p in ROOT.rglob("*.md"):
        parts = p.relative_to(ROOT).parts
        if any(x in SKIP_DIRS for x in parts[:-1]):
            continue
        if parts[0] == "asset" and p.name == "config.yaml":
            continue
        out.append(p)
    return sorted(out)


def frontmatter(text: str) -> tuple[dict[str, object], int]:
    """极简 YAML：只认顶层 `key: value` 和 `- item` 列表。返回 (字段, 正文起始行号)。"""
    if not text.startswith("---\n"):
        return {}, 0
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, 0
    fm: dict[str, object] = {}
    key = None
    for line in text[4:end].split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            fm[key] = val if val else []
        elif key and re.match(r"^\s+-\s+", line):
            if not isinstance(fm[key], list):
                fm[key] = []
            fm[key].append(re.sub(r"^\s+-\s+", "", line).strip())
    return fm, text[: end + 5].count("\n")


def strip_code(text: str) -> str:
    """去掉代码块和行内代码，保留行数。"""
    text = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


LINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKI_RE = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")


def vault_names() -> set[str]:
    return {p.stem for p in ROOT.rglob("*.md") if ".git" not in p.parts} | \
           {p.name for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}


# ---------------------------------------------------------------- 检查
def check_frontmatter(p: Path, fm: dict) -> None:
    parts = p.relative_to(ROOT).parts
    if p.name == "README.md":
        return
    want, required = None, ()
    if parts[0] == "projects" and len(parts) == 2:
        want, required = "project", ("name", "description", "aliases", "repo", "hosts")
    elif parts[0] == "projects" and len(parts) >= 3:
        want, required = "project-doc", ("project",)
    elif parts[:2] == ("docs", "guides"):
        want, required = "guide", ()
    elif parts[:2] == ("docs", "research"):
        want, required = "research", ()
    elif parts[:2] == ("task", "details"):
        want, required = "task-doc", ("project", "log")
    if not want:
        return
    if not fm:
        err(p, 1, "frontmatter", f"缺 frontmatter（应为 type: {want}）")
        return
    if fm.get("type") != want:
        err(p, 1, "frontmatter", f"type 应为 {want}，实际是 {fm.get('type') or '（空）'}")
    for k in required:
        if k not in fm:
            err(p, 1, "frontmatter", f"缺字段 {k}")
    if want == "project":
        if fm.get("name") not in (None, p.stem):
            err(p, 1, "frontmatter", f"name 应等于文件名 {p.stem}")
        if "description" in fm and not str(fm["description"]).strip('"').strip():
            err(p, 1, "frontmatter", "description 不能为空")
    if want == "project-doc" and isinstance(fm.get("project"), str):
        if fm["project"].strip('"') != f"[[{parts[1]}]]":
            err(p, 1, "frontmatter", f"project 应为 \"[[{parts[1]}]]\"")


def check_links(p: Path, text: str, fm: dict, names: set[str]) -> None:
    body = strip_code(text)
    parts = p.relative_to(ROOT).parts
    # 项目日志（projects/<项目>/log.md）可以链到任务，其他项目文件不行
    in_projects = parts[0] == "projects" and not (len(parts) == 3 and PROJECT_LOG_RE.match(p.name))
    for i, line in enumerate(body.split("\n"), 1):
        for m in LINK_RE.finditer(line):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            path = target.split("#")[0]
            if not path:
                continue
            from urllib.parse import unquote
            dest = (p.parent / unquote(path)).resolve()
            if not dest.exists():
                err(p, i, "links", f"链接目标不存在：{target}")
                continue
            if in_projects and ROOT / "task" in dest.parents:
                err(p, i, "no-task-link", f"项目文件不能链到任务：{target}")
    # frontmatter 里的双链（正文里不该用双链，见 CLAUDE.md「链接」）
    for k, v in fm.items():
        for item in (v if isinstance(v, list) else [v]):
            for m in WIKI_RE.finditer(str(item)):
                name = m.group(1).strip()
                if name not in names:
                    err(p, 1, "links", f"frontmatter {k} 的双链找不到：[[{name}]]")
                elif in_projects and DAILY_RE.match(name + ".md"):
                    err(p, 1, "no-task-link", f"项目文件不能链到任务：[[{name}]]")


def check_index(readme: Path, files: list[Path]) -> None:
    if not readme.exists():
        return
    text = readme.read_text()
    linked = {(readme.parent / t.split("#")[0]).resolve() for t in LINK_RE.findall(strip_code(text))}
    for f in files:
        if f.resolve() not in linked:
            err(readme, None, "index", f"索引里没有列出 {rel(f)}")


def check_filenames(p: Path) -> None:
    parts = p.relative_to(ROOT).parts
    if p.name == "README.md":
        return
    if parts[0] == "projects" and not re.match(r"^[a-z0-9-]+\.md$", p.name):
        err(p, None, "filename", "projects/ 下文件名只能用小写字母、数字和中横线")
    if parts[:2] == ("task", "details") and not re.match(r"^[a-z0-9_-]+\.md$", p.name):
        err(p, None, "filename", "task/details/ 下文件名只能用小写字母、数字、中横线和下划线")


def check_project_sections(p: Path, text: str) -> None:
    heads = [(i, l[3:].strip()) for i, l in enumerate(strip_code(text).split("\n"), 1) if l.startswith("## ")]
    names = [h for _, h in heads]
    sections = next((s for s in PROJECT_SECTIONS_BY_LANG if s[0] in names), None)
    if sections is None:
        unsorted_projects.append(p.stem)
        return
    PROJECT_SECTIONS = sections
    for i, h in heads:
        if h not in PROJECT_SECTIONS:
            err(p, i, "sections", f"项目主文件的二级标题只能是 {' / '.join(PROJECT_SECTIONS)}：{h}")
    known = [h for h in names if h in PROJECT_SECTIONS]
    if len(set(known)) != len(known) or known != [s for s in PROJECT_SECTIONS if s in known]:
        err(p, heads[0][0], "sections", f"小节按固定顺序、各一个：{' / '.join(PROJECT_SECTIONS)}")
    if (p.parent / p.stem).is_dir() and sections[2] not in names:
        err(p, heads[0][0], "sections", "有同名目录的项目要有「## 按需读」表")


def check_project_log(p: Path, text: str) -> None:
    dates = []
    for i, line in enumerate(strip_code(text).split("\n"), 1):
        if not line.startswith("## "):
            continue
        m = re.match(r"^## (\d{4}-\d{2}-\d{2})$", line.strip())
        if not m:
            err(p, i, "project-log", f"项目日志的二级标题只能是「## YYYY-MM-DD」：{line.strip()}")
            continue
        if dates and m.group(1) >= dates[-1]:
            err(p, i, "project-log", "项目日志按日期倒序，最新的在最上面，一天一个标题")
        dates.append(m.group(1))


DAILY_SECTIONS_BY_LANG = [[f"## {s[1]}" for s in vault.DAILY_SECTIONS], [f"## {s[2]}" for s in vault.DAILY_SECTIONS]]


def check_daily(p: Path, text: str) -> None:
    heads = [(i, l.strip()) for i, l in enumerate(text.split("\n"), 1) if l.startswith("## ")]
    titles = [h for _, h in heads]
    # 一个文件里用同一套标题：按第一个认得的标题定是中文还是英文
    DAILY_SECTIONS = next((s for s in DAILY_SECTIONS_BY_LANG if any(t in s for t in titles)), DAILY_SECTIONS_BY_LANG[0])
    for i, h in heads:
        if h not in DAILY_SECTIONS:
            err(p, i, "daily-log", f"每日日志只能有「## 任务」「## 日志」「## 事件」三个二级标题：{h}")
    if len(set(titles)) != len(titles) or titles != [t for t in DAILY_SECTIONS if t in titles]:
        err(p, heads[0][0], "daily-log", "二级标题按「## 任务」「## 日志」「## 事件」的顺序，各一个")
    section = None
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            section = vault.daily_key(line)
            continue
        if section in ("log", "events") and re.match(r"^\s*[-*]\s+\[.\]\s", line):
            err(p, i, "daily-log", f"{'日志' if section == 'log' else '事件'}段里不能用复选框（会被当成任务）")
        elif section == "events" and line.strip() and not re.match(r"^- \d{2}:\d{2} \S", line):
            err(p, i, "daily-log", "事件每条一行：「- HH:MM 做了什么」，不挂子列表")
        if section is None and re.match(r"^- \[.\]\s", line):
            err(p, i, "daily-log", "任务要写在「## 任务」标题下")
        if section == "tasks" and re.match(r"^- \[.\]\s", line) and not any(m in line for m in vault.DETAILS_MARKERS):
            n = 0
            for nxt in lines[i:]:
                if not nxt.startswith("  "):
                    break
                if re.match(r"^  [-*]\s", nxt):
                    n += 1
            if n > MAX_SUBITEMS:
                warn(p, i, "daily-log", f"任务下有 {n} 行子行，超过 {MAX_SUBITEMS} 行：转成 task/details/ 文档，或精简、挪到项目那边")


def check_task_ids() -> None:
    sys.path.insert(0, str(ROOT / "bin"))
    import unfinished_tasks as ut

    seen: dict[str, tuple[Path, int]] = {}
    for t in ut.collect(include_closed=True):
        p = ROOT / "task" / f"{t['date']}.md"
        if t.get("type") and (t["nested"] or not re.fullmatch(r"[a-z0-9-]+", t["type"])):
            err(p, t["line"], "task-id", f"类型标签写在顶层任务行上，格式 #type/message（小写字母、数字、中横线）：#type/{t['type']}")
        if t["reporter"] and (t["nested"] or not re.fullmatch(r"(?:[A-Z][a-z]+){2,}", t["reporter"])):
            err(p, t["line"], "task-id", f"报告人标签写在顶层任务行上，格式 #reporter/AliceChen（英文名去空格、每段首字母大写）：#reporter/{t['reporter']}")
        if t["id"]:
            if t["id"] in seen:
                first = seen[t["id"]]
                err(p, t["line"], "task-id", f"内部编号 {t['id']} 和 {rel(first[0])}:{first[1]} 重复，改成 bin/unfinished_tasks.py --next-id 给的号")
            else:
                seen[t["id"]] = (p, t["line"])
        elif not t["nested"] and t["status"] not in ut.CLOSED:
            err(p, t["line"], "task-id", "未完成的任务要有内部编号：时间后面加 T-N，号用 bin/unfinished_tasks.py --next-id 取")


def check_skills() -> None:
    p = subprocess.run([sys.executable, str(ROOT / "bin" / "sync_skills.py"), "--check"],
                       cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        errors.append(f"skills  [skills] .claude/skills 和 skills/ 不一致，跑 bin/sync_skills.py：\n"
                      + (p.stdout + p.stderr).strip())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-q", "--quiet", action="store_true", help="只输出错误")
    args = ap.parse_args()

    files = md_files()
    names = vault_names()
    for p in files:
        text = p.read_text()
        fm, _ = frontmatter(text)
        check_frontmatter(p, fm)
        check_links(p, text, fm, names)
        check_filenames(p)
        if p.parent == ROOT / "projects" and p.name != "README.md" and len(text.encode()) > MAX_PROJECT_BYTES:
            warn(p, None, "size", f"项目文件 {len(text.encode()) // 1000}KB，超过 {MAX_PROJECT_BYTES // 1000}KB，应把按需才用的内容拆到同名目录的子文件")
        pp = p.relative_to(ROOT).parts
        if pp[0] == "projects" and len(pp) == 3:
            if PROJECT_LOG_RE.match(p.name):
                check_project_log(p, text)
                if p.name == "log.md" and len(text.encode()) > MAX_LOG_BYTES:
                    warn(p, None, "size", f"项目日志 {len(text.encode()) // 1000}KB，超过 {MAX_LOG_BYTES // 1000}KB，把上个季度及更早的挪到 log-YYYYqN.md")
            elif re.match(r"^design(-[a-z0-9-]+)?\.md$", p.name) and len(text.encode()) > MAX_DESIGN_BYTES:
                warn(p, None, "size", f"Design {len(text.encode()) // 1000}KB，超过 {MAX_DESIGN_BYTES // 1000}KB，应按主题拆成 design-<主题>.md，带日期的决定和过程挪进 log.md")
            elif p.name == "pitfalls.md" and len(text.encode()) > MAX_DESIGN_BYTES:
                warn(p, None, "size", f"pitfalls.md {len(text.encode()) // 1000}KB，超过 {MAX_DESIGN_BYTES // 1000}KB，删掉不再成立的，经过挪进 log.md")
        if pp[0] == "projects" and len(pp) == 2 and p.name != "README.md":
            check_project_sections(p, text)
        if p.parent == ROOT / "task" and DAILY_RE.match(p.name):
            check_daily(p, text)

    for sub in ("guides", "research"):
        d = ROOT / "docs" / sub
        check_index(d / "README.md", [p for p in d.rglob("*.md") if p.name != "README.md"])
    check_index(ROOT / "docs" / "README.md", [ROOT / "docs" / s / "README.md" for s in ("guides", "research")])
    check_task_ids()
    check_skills()
    if unsorted_projects:
        warnings.append(f"projects  [sections] {len(unsorted_projects)} 个项目主文件还没按固定小节整理：{'、'.join(sorted(unsorted_projects))}")

    for e in errors:
        print(f"错误  {e}")
    if not args.quiet:
        for w in warnings:
            print(f"警告  {w}")
        print(f"共检查 {len(files)} 个文件：错误 {len(errors)}，警告 {len(warnings)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
