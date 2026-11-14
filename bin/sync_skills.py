#!/usr/bin/env python3
"""把 skills/ 下的 skill 安装 / 同步成本仓库的项目 skill（.claude/skills/）。

规则见 skills/sync-skill.md：
- skills/<name>/SKILL.md 是唯一来源，目录名必须等于 frontmatter 的 name。
- .claude/skills/<name>/SKILL.md 只是入口：name、description 逐字照抄源文件，
  正文只指回源文件，不复制脚本、config.json 等其他文件。
- 以 skills/ 为准：补装新增的、删除源里已没有的、覆盖内容不一致的。

用法:
  bin/sync_skills.py            # 安装 / 同步，并列出改了什么
  bin/sync_skills.py --check    # 只检查不改，有差异时退出码为 1
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vault  # noqa: E402

ROOT = vault.ROOT
SRC_DIR = ROOT / "skills"
DST_DIR = ROOT / ".claude" / "skills"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
# 入口正文的固定标记，用来识别哪些 .claude/skills 目录是本脚本管的
MARKERS = ("本 skill 的实际内容在 `skills/", "This skill lives in `skills/")

# 入口正文按 vault.config.json 的 language 用中文或英文
BODIES = {
    "zh-CN": """本 skill 的实际内容在 `skills/{name}/SKILL.md`。先完整读取该文件，再严格按其中的说明执行；
命令在仓库根目录执行，源文件里写的脚本、配置路径都按它原样使用。
""",
    "en": """This skill lives in `skills/{name}/SKILL.md`. Read that file in full first, then follow it exactly;
run commands from the repository root and use the script and config paths exactly as written there.
""",
}
BODY = BODIES.get(vault.language(), BODIES["zh-CN"])


def field_lines(fm, key):
    """取 frontmatter 里某个键的原文（含多行值的缩进续行），找不到返回 None。"""
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        if line.startswith(key + ":"):
            out = [line]
            for nxt in lines[i + 1:]:
                if nxt.startswith((" ", "\t")) or nxt == "":
                    out.append(nxt)
                else:
                    break
            while out and out[-1] == "":
                out.pop()
            return "\n".join(out)
    return None


def load_sources(errors):
    """返回 {name: 入口文件内容}；有问题的 skill 记进 errors 并跳过。"""
    sources = {}
    for d in sorted(p for p in SRC_DIR.iterdir() if p.is_dir()):
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            continue
        rel = skill_md.relative_to(ROOT)
        m = FRONTMATTER.match(skill_md.read_text(encoding="utf-8"))
        if not m:
            errors.append(f"{rel}: 没有 frontmatter")
            continue
        name_line = field_lines(m.group(1), "name")
        desc_line = field_lines(m.group(1), "description")
        if not name_line or not desc_line:
            errors.append(f"{rel}: frontmatter 缺少 name 或 description")
            continue
        name = name_line.split(":", 1)[1].strip().strip("'\"")
        if name != d.name:
            errors.append(f"{rel}: 目录名 {d.name} 和 name {name} 不一致，"
                          f"请以 name 为准改目录名并改掉旧路径引用")
            continue
        sources[name] = f"---\n{name_line}\n{desc_line}\n---\n\n" + BODY.format(name=name)
    return sources


def main():
    ap = argparse.ArgumentParser(description="安装 / 同步 skills/ 到 .claude/skills/")
    ap.add_argument("--check", action="store_true", help="只检查不改，有差异时退出码为 1")
    args = ap.parse_args()

    errors, warnings = [], []
    sources = load_sources(errors)
    added, updated, removed, ok = [], [], [], []

    for name, content in sources.items():
        entry = DST_DIR / name / "SKILL.md"
        if not entry.is_file():
            added.append(name)
        elif entry.read_text(encoding="utf-8") != content:
            updated.append(name)
        else:
            ok.append(name)
        if not args.check and name not in ok:
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_text(content, encoding="utf-8")
        extras = [p.name for p in (DST_DIR / name).iterdir() if p.name != "SKILL.md"] \
            if (DST_DIR / name).is_dir() else []
        if extras:
            warnings.append(f".claude/skills/{name}/ 里有多余文件：{', '.join(extras)}"
                            "（入口只应有 SKILL.md，请人工确认后删除）")

    if DST_DIR.is_dir():
        for d in sorted(p for p in DST_DIR.iterdir() if p.is_dir()):
            if d.name in sources:
                continue
            entry = d / "SKILL.md"
            managed = entry.is_file() and any(m in entry.read_text(encoding="utf-8") for m in MARKERS)
            if not managed:
                warnings.append(f".claude/skills/{d.name}/ 不是本脚本生成的入口，未处理")
            elif any(e.startswith(f"skills/{d.name}/") for e in errors):
                continue  # 源还在，只是有错误，先不删
            else:
                removed.append(d.name)
                if not args.check:
                    shutil.rmtree(d)

    verb = "需要" if args.check else "已"
    for label, names in ((f"{verb}补装", added), (f"{verb}更新", updated), (f"{verb}删除", removed)):
        for n in names:
            print(f"{label}  {n}")
    for w in warnings:
        print(f"警告  {w}")
    for e in errors:
        print(f"错误  {e}", file=sys.stderr)
    changed = len(added) + len(updated) + len(removed)
    print(f"共 {len(sources)} 个 skill：一致 {len(ok)}，补装 {len(added)}，"
          f"更新 {len(updated)}，删除 {len(removed)}，错误 {len(errors)}")

    if errors or (args.check and changed):
        sys.exit(1)


if __name__ == "__main__":
    main()
