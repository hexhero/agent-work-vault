#!/usr/bin/env python3
"""First-time setup for agent-work-vault / 新克隆后的初始化。

- --lang en|zh-CN   copy the docs under i18n/<lang>/ into place and record the language in vault.config.json
                    把 i18n/<语言>/ 下的文档换到原位，并把语言写进 vault.config.json
- --timezone NAME   IANA time zone for the scripts (e.g. Asia/Shanghai), written to vault.config.json
                    脚本用的时区，写进 vault.config.json
- --examples        copy examples/<lang>/ (demo project and daily logs) into the vault; existing files are kept
                    把 examples/<语言>/ 里的示例项目和每日日志装进来，已有的文件不覆盖
Always: enable the pre-commit hook (when inside a git repo) and sync the skill entries.
每次都会：启用 pre-commit 钩子（在 git 仓库里时）、同步 skill 入口。

Usage / 用法:
  bin/setup.py --lang zh-CN --timezone Asia/Shanghai
  bin/setup.py --lang en --examples
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "zh-CN")


def copy_tree(src: Path, overwrite: bool) -> list[str]:
    done = []
    for f in sorted(p for p in src.rglob("*") if p.is_file()):
        rel = f.relative_to(src)
        dst = ROOT / rel
        if dst.exists() and not overwrite:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        done.append(str(rel))
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", choices=LANGS, help="documentation language / 文档语言")
    ap.add_argument("--timezone", help="IANA time zone, e.g. Europe/Berlin / 时区")
    ap.add_argument("--examples", action="store_true", help="install the examples / 装上示例")
    args = ap.parse_args()

    cfg_path = ROOT / "vault.config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    lang = args.lang or cfg.get("language") or "en"

    if args.lang:
        src = ROOT / "i18n" / lang
        if not src.is_dir():
            print(f"i18n/{lang}/ not found", file=sys.stderr)
            return 1
        n = len(copy_tree(src, overwrite=True))
        print(f"language: {lang} ({n} files copied from i18n/{lang}/)")
        cfg["language"] = lang
    if args.timezone:
        from zoneinfo import ZoneInfo
        ZoneInfo(args.timezone)  # raises if unknown
        cfg["timezone"] = args.timezone
        print(f"timezone: {args.timezone}")
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.examples:
        src = ROOT / "examples" / lang
        n = len(copy_tree(src, overwrite=False))
        print(f"examples: {n} files copied from examples/{lang}/")

    if (ROOT / ".git").exists():
        subprocess.run(["git", "config", "core.hooksPath", ".githooks"], cwd=ROOT, check=True)
        print("pre-commit hook: enabled (core.hooksPath = .githooks)")
    subprocess.run([sys.executable, str(ROOT / "bin" / "sync_skills.py")], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    print("skills: synced (.claude/skills/)")
    print("next: fill in PROFILE.md and asset/services.md, then open this folder in Claude Code and Obsidian")
    return 0


if __name__ == "__main__":
    sys.exit(main())
