"""各脚本共用的约定：中英文的固定标题、时区。

每日日志、项目文件的固定标题中文、英文两套都认（一个文件里用同一套）。
语言（skill 入口用哪种）取 vault.config.json 的 "language"（zh-CN / en，默认 zh-CN）。
时区按顺序取：环境变量 VAULT_TZ、仓库根目录 vault.config.json 的 "timezone"（IANA 名，如 Asia/Shanghai）、本机时区。
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 每日日志的三个二级标题，顺序固定：(键, 中文, 英文)
DAILY_SECTIONS = [("tasks", "任务", "Tasks"), ("log", "日志", "Log"), ("events", "事件", "Events")]
# 项目主文件的固定小节，顺序固定
PROJECT_SECTIONS = [
    ("location", "位置", "Location"),
    ("resources", "资源", "Resources"),
    ("read-on-demand", "按需读", "Read on demand"),
    ("where-to-look", "去哪查", "Where to look"),
    ("how-to", "怎么做", "How to"),
    ("red-lines", "红线", "Red lines"),
    ("pitfalls", "坑", "Pitfalls"),
    ("related", "相关", "Related"),
]
# 任务下面挂项目的那一行：「- 项目：[x](…)」/「- Project: [x](…)」
PROJECT_LINE_PREFIXES = ("项目：", "Project:")
# 任务行上指向详情文档的链接：「→ [详情](…)」/「→ [Details](…)」
DETAILS_MARKERS = ("→ [详情]", "→ [Details]")


def daily_heading(key: str) -> tuple[str, str]:
    """某个每日日志小节的两种写法（带 ## ）。"""
    _, zh, en = next(s for s in DAILY_SECTIONS if s[0] == key)
    return f"## {zh}", f"## {en}"


def daily_key(heading: str) -> str | None:
    """二级标题（带 ## ）→ 小节键；不是固定标题返回 None。"""
    h = heading.strip()
    for key, zh, en in DAILY_SECTIONS:
        if h in (f"## {zh}", f"## {en}"):
            return key
    return None


def _config() -> dict:
    p = ROOT / "vault.config.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def language() -> str:
    """文档语言：zh-CN 或 en，在 vault.config.json 的 "language" 里配，默认 zh-CN。"""
    return _config().get("language") or "zh-CN"


def timezone_name() -> str | None:
    return os.environ.get("VAULT_TZ") or _config().get("timezone") or None


def now() -> datetime:
    """按配置的时区取当前时间；没配就用本机时区。"""
    name = timezone_name()
    if name:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(name))
    return datetime.now().astimezone()
