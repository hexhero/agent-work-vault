#!/usr/bin/env python3
"""任务看板：把 projects/、task/ 和 skills/ 渲染成一个实时刷新的关系图网页（项目、任务、skill 是节点，带项目日志和事件流）。

只读，不改任何文件。数据来自 projects.py（项目）、unfinished_tasks.py（任务）、skills/ 下各 SKILL.md 的 frontmatter、
各项目的 log.md、每日日志的「## 事件」、follow-up 的跟进项和运行状态（task/follow-up.json、~/.local/state/follow-up/，Teams 只取数量）；Claude 用量只读本机
~/.claude/projects 会话记录里的 token 数字和模型名，不读对话内容；订阅额度（近 5 小时 / 本周用了多少）定时发一条 haiku 短请求、从返回的限额信息里取；文件一变，页面经 SSE 自动刷新。页面在 bin/board.html。

用法:
  bin/board.py                    # http://127.0.0.1:8765
  bin/board.py --port 9000
  bin/board.py --host 0.0.0.0     # 让同网段的其他机器也能打开

页面里的接口都是相对路径，可以挂在反向代理的子路径下（末尾要带斜杠）。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
sys.path.insert(0, str(BIN))

import day_summary as summary_mod  # noqa: E402
import projects as projects_mod  # noqa: E402
import unfinished_tasks as tasks_mod  # noqa: E402
import vault  # noqa: E402

TASK_DIR = ROOT / "task"
PROJECT_DIR = ROOT / "projects"
SKILL_DIR = ROOT / "skills"
SKILL_PROJECT = re.compile(r"projects/([a-z0-9_-]+)\.md")
PAGE = BIN / "board.html"
LOG_RE = re.compile(r"^log(-\d{4}q[1-4])?\.md$")
LOG_DATE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")
END_TIME = re.compile(r"^-\s*(\d{1,2}:\d{2})\s+(.*)$")
DETAIL_DOC = re.compile(r"\]\((details/[a-z0-9_-]+\.md)\)")
DETAIL_ARROW = re.compile(r"\s*→\s*\[[^\]]*\]\(details/[^)]*\)")
DOC_PATH = re.compile(r"^details/[a-z0-9_-]+\.md$")
PROJECT_LINE = re.compile(r"^- (?:" + "|".join(map(re.escape, vault.PROJECT_LINE_PREFIXES)) + ")")
NO_PROJECT = "_none"
EVENT = re.compile(r"^- (\d{1,2}:\d{2})\s+(.*)$")
EVENT_LIMIT = 300
CLAUDE_DIR = Path.home() / ".claude" / "projects"
USAGE_DAYS = 7
TZ_OFFSET = vault.now().utcoffset()  # 按 vault.config.json / VAULT_TZ 的时区
FOLLOW_ITEMS = TASK_DIR / "follow-up.json"
FOLLOW_STATE = Path(os.environ.get("FOLLOWUP_STATE") or Path.home() / ".local" / "state" / "follow-up")


def load_logs(name: str) -> list[dict]:
    """项目日志按日期切开，最新的在前。"""
    d = PROJECT_DIR / name
    entries: dict[str, list[str]] = {}
    if d.is_dir():
        for f in sorted(p for p in d.iterdir() if LOG_RE.match(p.name)):
            cur = None
            for line in f.read_text(encoding="utf-8").split("\n"):
                m = LOG_DATE.match(line)
                if m:
                    cur = m.group(1)
                    entries.setdefault(cur, [])
                elif cur:
                    entries[cur].append(line)
    return [{"date": k, "body": "\n".join(v).strip("\n")}
            for k, v in sorted(entries.items(), reverse=True) if "\n".join(v).strip()]


def load_skills(project_ids: set[str]) -> list[dict]:
    """skills/ 下的 skill：name、description、SKILL.md 里链到的项目、在任务和项目日志里被提到的次数。"""
    corpus = "\n".join(f.read_text(encoding="utf-8") for f in
                       [*TASK_DIR.glob("*.md"), *PROJECT_DIR.glob("*.md"), *PROJECT_DIR.glob("*/log*.md")])
    out = []
    for f in sorted(SKILL_DIR.glob("*/SKILL.md")):
        text = f.read_text(encoding="utf-8")
        fm = projects_mod.frontmatter(text)
        name = fm.get("name") or f.parent.name
        out.append({
            "id": name,
            "description": fm.get("description") or "",
            "projects": sorted({m for m in SKILL_PROJECT.findall(text) if m in project_ids}),
            "uses": len(skill_re(name).findall(corpus)),
        })
    return out


def skill_re(name: str) -> re.Pattern:
    return re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")


def load_tasks(skills: list[str]) -> list[dict]:
    out = []
    pats = [(n, skill_re(n)) for n in skills]
    covered = ("", 0)  # (日期, 上一条顶层任务的补充说明覆盖到第几行)
    for t in tasks_mod.collect(include_closed=True):
        # 子任务已经在父任务的补充说明里，不单列
        if t["nested"] and t["date"] == covered[0] and t["line"] <= covered[1]:
            continue
        if not t["nested"]:
            covered = (t["date"], t["line"] + len(t["detail"]))
        title, end = t["title"], None
        m = END_TIME.match(title)
        if m:
            end, title = m.group(1), m.group(2)
        raw = title + "\n" + "\n".join(t["detail"])
        doc = DETAIL_DOC.search(raw)
        out.append({
            "date": t["date"],
            "line": t["line"],
            "id": t["id"],
            "status": t["status"],
            "label": t["status_label"],
            "start": t["start"],
            "end": end,
            "title": DETAIL_ARROW.sub("", title).strip(),
            "detail": "\n".join(l for l in t["detail"] if not PROJECT_LINE.match(l)).strip("\n"),
            "refs": t["refs"],
            "reporter": tasks_mod.reporter_name(t["reporter"]),
            "type": t["type"],
            "projects": t["projects"] or [NO_PROJECT],
            "doc": doc.group(1) if doc else None,
            "skills": [n for n, pat in pats if pat.search(raw)],
        })
    return out


def load_events() -> list[dict]:
    """每日日志「## 事件」里的条目，最新的在前。"""
    out = []
    for f in sorted(TASK_DIR.glob("*.md"), reverse=True):
        m = tasks_mod.LOG_NAME.match(f.name)
        if not m:
            continue
        day = []
        for line in summary_mod.section(f.read_text(encoding="utf-8"), *vault.daily_heading("events")).split("\n"):
            e = EVENT.match(line)
            if e:
                day.append({"date": m.group(1), "time": e.group(1).zfill(5), "text": e.group(2)})
        out.extend(sorted(day, key=lambda x: x["time"], reverse=True))
        if len(out) >= EVENT_LIMIT:
            break
    return out[:EVENT_LIMIT]


def _json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def follow_cond(e: dict) -> str:
    """跟进项的触发条件，一句话。"""
    if e.get("source") == "clickup":
        c = e.get("clickup") or {}
        parts = []
        if c.get("status"):
            parts.append("status is " + " / ".join(c["status"]))
        if c.get("comment_by"):
            parts.append("new comment by " + " / ".join(c["comment_by"]))
        if c.get("comment_has"):
            parts.append("comment contains " + ", ".join(f'"{k}"' for k in c["comment_has"]))
        if c.get("any_change"):
            parts.append("any update")
        return " ".join(c.get("tickets") or []) + ": " + ", or ".join(parts)
    if e.get("source") == "teams":
        t = e.get("teams") or {}
        parts = ["Teams " + ("thread" if t.get("thread") else "chat" if t.get("chat") else "message")]
        if t.get("from"):
            parts.append("from " + " / ".join(t["from"]))
        if t.get("keywords"):
            parts.append("containing " + ", ".join(f'"{k}"' for k in t["keywords"]))
        return ", ".join(parts)
    if e.get("source") == "command":
        return e.get("check") or ""
    if e.get("source") == "mail":
        m = e.get("mail") or {}
        return f"mailbox {m.get('mailbox', '')} readable" + (f", search finds {', '.join(m['search'])}" if m.get("search") else "")
    return ""


def load_followup() -> dict:
    """follow-up 后台服务（skills/follow-up）：跟进项、服务状态、Teams 收件箱计数。Teams 只给数量，不给消息内容。"""
    items = []
    for e in (_json(FOLLOW_ITEMS, {}) or {}).get("items", []):
        st = _json(FOLLOW_STATE / "items" / f"{e.get('id')}.json", {})
        items.append({k: e.get(k) for k in ("id", "task", "title", "source", "action", "until", "on_expire", "added", "paused", "fails")}
                     | {"cond": follow_cond(e), "last_check": st.get("last_check"), "last_error": st.get("last_error")})
    last = _json(FOLLOW_STATE / "last_tick.json", {})
    today = (datetime.now(timezone.utc) + TZ_OFFSET).strftime("%Y-%m-%d")

    def count(d: str, today_only=False) -> int:
        try:
            fs = list((FOLLOW_STATE / "teams" / d).glob("*.json"))
        except OSError:
            return 0
        if today_only:
            fs = [f for f in fs if (datetime.fromtimestamp(f.stat().st_mtime, timezone.utc) + TZ_OFFSET).strftime("%Y-%m-%d") == today]
        return len(fs)

    try:
        active = subprocess.run(["systemctl", "--user", "is-active", "--quiet", "follow-up"], timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        active = None
    return {"items": items, "active": active, "last_tick": last.get("at"),
            "errors": [x[:200] for x in last.get("errors") or []],
            "triggered": [x.get("id") for x in last.get("triggered") or []], "expired": last.get("expired") or [],
            "teams": {"paused": (FOLLOW_STATE / "paused").exists(), "queue": count("queue"),
                      "done_today": count("done", True), "failed": count("failed")}}


def build_state() -> dict:
    projects = [{
        "id": Path(p["file"]).stem,
        "name": p["name"],
        "description": p["description"],
        "aliases": p["aliases"],
        "log": load_logs(Path(p["file"]).stem),
    } for p in projects_mod.load()]
    projects.append({"id": NO_PROJECT, "name": "No project", "aliases": [], "log": [],
                     "description": "Tasks not linked to any project: this repo's rules and skills, research, odds and ends."})
    skills = load_skills({p["id"] for p in projects})
    now = datetime.now(timezone.utc) + TZ_OFFSET
    return {"generated": now.strftime("%Y-%m-%d %H:%M:%S"), "tz_offset_min": int(TZ_OFFSET.total_seconds() // 60), "vault": ROOT.name, "projects": projects,
            "tasks": load_tasks([s["id"] for s in skills]), "skills": skills, "events": load_events(),
            "followup": load_followup()}


def signature() -> tuple:
    files = [*TASK_DIR.glob("*.md"), *(TASK_DIR / "details").glob("*.md"),
             *PROJECT_DIR.glob("*.md"), *PROJECT_DIR.glob("*/log*.md"), *SKILL_DIR.glob("*/SKILL.md"),
             FOLLOW_ITEMS, FOLLOW_STATE / "last_tick.json", FOLLOW_STATE / "paused", *(FOLLOW_STATE / "items").glob("*.json"),
             *(FOLLOW_STATE / "teams" / d for d in ("queue", "done", "failed"))]
    sig = []
    for f in sorted(files):
        try:
            st = f.stat()
            sig.append((str(f), st.st_mtime_ns, st.st_size))
        except OSError:
            pass
    return tuple(sig)


class Usage:
    """本机 Claude Code 的 token 用量：增量读会话记录（jsonl 只追加），只取 usage 数字和模型名。"""

    def __init__(self):
        self.files: dict[str, list] = {}  # 路径 -> [已读到的偏移, {消息 id: (时间, 模型, in, out, 写缓存, 读缓存)}, mtime]

    def scan(self):
        cutoff = time.time() - (USAGE_DAYS + 1) * 86400
        for f in CLAUDE_DIR.rglob("*.jsonl"):
            try:
                st = f.stat()
            except OSError:
                continue
            if st.st_mtime < cutoff:
                continue
            rec = self.files.setdefault(str(f), [0, {}, 0.0])
            rec[2] = st.st_mtime
            if st.st_size < rec[0]:
                rec[0], rec[1] = 0, {}
            if st.st_size == rec[0]:
                continue
            with open(f, "rb") as fh:
                fh.seek(rec[0])
                data = fh.read()
            end = data.rfind(b"\n") + 1  # 只吃完整的行
            for line in data[:end].split(b"\n"):
                if b'"usage"' not in line or b'"assistant"' not in line:
                    continue
                try:
                    o = json.loads(line)
                    m = o["message"]
                    u = m["usage"]
                    model = m.get("model") or "unknown"
                    if o.get("type") != "assistant" or model.startswith("<"):
                        continue
                    ts = datetime.fromisoformat(o["timestamp"].replace("Z", "+00:00")).timestamp()
                    # 同一条消息流式写多行，后面的覆盖前面的
                    rec[1][m.get("id") or o.get("uuid")] = (
                        ts, model, u.get("input_tokens") or 0, u.get("output_tokens") or 0,
                        u.get("cache_creation_input_tokens") or 0, u.get("cache_read_input_tokens") or 0)
                except (ValueError, KeyError, TypeError, AttributeError):
                    continue
            rec[0] += end

    def summary(self) -> dict:
        now = time.time()
        merged: dict = {}
        for rec in self.files.values():
            merged.update(rec[1])  # 续接的会话会把旧消息抄进新文件，按消息 id 去重
        zero = lambda: {"in": 0, "out": 0, "cw": 0, "cr": 0, "n": 0}  # noqa: E731

        def add(t, e):
            t["in"] += e[2]; t["out"] += e[3]; t["cw"] += e[4]; t["cr"] += e[5]; t["n"] += 1  # noqa: E702

        local_now = datetime.fromtimestamp(now, timezone.utc) + TZ_OFFSET
        today = local_now.strftime("%Y-%m-%d")
        day_keys = [(local_now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(USAGE_DAYS - 1, -1, -1)]
        hour0 = int(now // 3600) - 23
        days = {k: zero() for k in day_keys}
        hours = [zero() for _ in range(24)]
        today_t, win, models, latest = zero(), zero(), {}, None
        for e in merged.values():
            d = (datetime.fromtimestamp(e[0], timezone.utc) + TZ_OFFSET).strftime("%Y-%m-%d")
            if d in days:
                add(days[d], e)
            if d == today:
                add(today_t, e)
                add(models.setdefault(e[1], zero()), e)
            if now - e[0] <= 5 * 3600:
                add(win, e)
            h = int(e[0] // 3600) - hour0
            if 0 <= h < 24:
                add(hours[h], e)
            if latest is None or e[0] > latest[0]:
                latest = e
        active = sum(1 for path, rec in self.files.items() if now - rec[2] <= 300 and "/subagents/" not in path)
        return {
            "model": latest[1] if latest else None,
            "last": (datetime.fromtimestamp(latest[0], timezone.utc) + TZ_OFFSET).strftime("%m-%d %H:%M") if latest else None,
            "active": active,
            "today": today_t,
            "win5h": win,
            "models": sorted(({"model": k, **v} for k, v in models.items()),
                             key=lambda x: -(x["in"] + x["out"] + x["cw"] + x["cr"])),
            "days": [{"d": k[5:], **days[k]} for k in day_keys],
            "hours": [{"h": (datetime.fromtimestamp((hour0 + i) * 3600, timezone.utc) + TZ_OFFSET).strftime("%H"), **hours[i]}
                      for i in range(24)],
        }


class Quota:
    """订阅额度：近 5 小时和本周各用了多少（0～1）、什么时候重置。

    本机没有文件记这个数，它只跟着 API 响应回来。所以定时用 haiku 发一条最短的无头请求
    （claude -p，不存会话、不带工具和 MCP），从输出里的 rate_limit_event 取。每次约一万 haiku token。
    """

    def __init__(self):
        self.data = None

    def probe(self, timeout: float = 90.0):
        exe = shutil.which("claude") or str(Path.home() / ".local" / "bin" / "claude")
        cwd = Path.home() / ".cache" / "task-board"
        cwd.mkdir(parents=True, exist_ok=True)
        out = subprocess.run(
            [exe, "-p", "reply with: ok", "--model", "haiku", "--strict-mcp-config", "--disable-slash-commands",
             "--tools", "", "--no-session-persistence", "--output-format", "stream-json", "--verbose"],
            cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout).stdout
        for line in out.split("\n"):
            if '"rate_limit_event"' not in line:
                continue
            try:
                win = json.loads(line)["rate_limit_info"]["unifiedWindows"]
            except (ValueError, KeyError, TypeError):
                continue
            data = {"at": int(time.time())}
            for key in ("five_hour", "seven_day"):
                w = win.get(key)
                if w and w.get("utilization") is not None:
                    data[key] = {"used": w["utilization"], "resets_at": w.get("resetsAt")}
            if len(data) > 1:
                self.data = data

    def watch(self, interval: float):
        while True:
            try:
                self.probe()
            except Exception as e:
                print(f"[board] quota check failed: {e}", file=sys.stderr)
            time.sleep(interval)


QUOTA = Quota()


class Hub:
    """当前状态和版本号；文件变了由 watch 线程重建并叫醒所有 SSE 连接。"""

    def __init__(self):
        self.cond = threading.Condition()
        self.version = 0
        self.payload = b"{}"
        self.sig = None
        self.usage = Usage()
        self.usage_version = 0
        self.usage_payload = b"null"

    def refresh(self):
        sig = signature()
        if sig == self.sig:
            return
        try:
            payload = json.dumps(build_state(), ensure_ascii=False).encode("utf-8")
        except Exception as e:  # 文件正写到一半之类，下一轮再试
            print(f"[board] rebuild failed: {e}", file=sys.stderr)
            return
        with self.cond:
            self.sig, self.payload = sig, payload
            self.version += 1
            self.cond.notify_all()

    def watch(self, interval: float):
        while True:
            time.sleep(interval)
            self.refresh()

    def watch_usage(self, interval: float):
        while True:
            try:
                self.usage.scan()
                payload = json.dumps({**self.usage.summary(), "quota": QUOTA.data}, ensure_ascii=False).encode("utf-8")
                if payload != self.usage_payload:
                    with self.cond:
                        self.usage_payload = payload
                        self.usage_version += 1
                        self.cond.notify_all()
            except Exception as e:
                print(f"[board] usage scan failed: {e}", file=sys.stderr)
            time.sleep(interval)


HUB = Hub()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, code: int, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self.send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
        elif url.path == "/api/state":
            self.send(200, HUB.payload, "application/json; charset=utf-8")
        elif url.path == "/api/usage":
            self.send(200, HUB.usage_payload, "application/json; charset=utf-8")
        elif url.path == "/api/events":
            self.events()
        elif url.path == "/api/doc":
            self.doc(parse_qs(url.query).get("path", [""])[0])
        else:
            self.send(404, b"not found", "text/plain")

    def doc(self, rel: str):
        """只放行 task/details/ 下的详情文档。"""
        f = TASK_DIR / rel
        if not DOC_PATH.match(rel) or not f.is_file():
            self.send(404, b"not found", "text/plain")
            return
        text = f.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end > 0:
                text = text[end + 5:]
        self.send(200, text.encode("utf-8"), "text/plain; charset=utf-8")

    def events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        seen, seen_usage = -1, -1
        try:
            while True:
                with HUB.cond:
                    if HUB.version == seen and HUB.usage_version == seen_usage:
                        HUB.cond.wait(15)
                    version, payload = HUB.version, HUB.payload
                    usage_version, usage_payload = HUB.usage_version, HUB.usage_payload
                if version == seen and usage_version == seen_usage:
                    self.wfile.write(b"event: ping\ndata: 1\n\n")  # 页面靠它判断连接还活着
                if version != seen:
                    self.wfile.write(b"data: " + payload + b"\n\n")
                    seen = version
                if usage_version != seen_usage:
                    self.wfile.write(b"event: usage\ndata: " + usage_payload + b"\n\n")
                    seen_usage = usage_version
                self.wfile.flush()
        except OSError:
            pass


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1", help="listen address, localhost only by default")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--interval", type=float, default=1.0, help="how often to check files for changes (seconds)")
    ap.add_argument("--quota-interval", type=float, default=900.0, help="how often to check the subscription quota (seconds), one short haiku request each time; 0 disables")
    args = ap.parse_args()

    HUB.refresh()
    threading.Thread(target=HUB.watch, args=(args.interval,), daemon=True).start()
    threading.Thread(target=HUB.watch_usage, args=(5.0,), daemon=True).start()
    if args.quota_interval > 0:
        threading.Thread(target=QUOTA.watch, args=(args.quota_interval,), daemon=True).start()
    server = Server((args.host, args.port), Handler)
    print(f"Task board: http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
