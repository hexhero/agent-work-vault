# agent-work-vault

[中文](README.zh-CN.md)

A work vault you run together with an AI agent: one Git repository that is at once an [Obsidian](https://obsidian.md) vault and a [Claude Code](https://claude.com/claude-code) project. You talk to the agent; it keeps your daily task log, your project files and your notes in shape by following the rules written in `CLAUDE.md` and a few skills, and a set of small scripts and a linter keep everything checkable.

It grew out of a real working setup used every day by a backend engineer, with everything personal and company-specific stripped out.

## What you get

- **Daily log** (`task/YYYY-MM-DD.md`): a cross-project to-do list with statuses (not started / in progress / Review / blocked / done / cancelled), stable task IDs (`T-12`), reporter tags, plus a log and an event stream. The agent moves tasks to Review when it needs you, and never marks anything done without your consent.
- **Project files** (`projects/<project>.md` + `projects/<project>/`): where it runs and what it uses in the main file, design and progress in Design, an append-only project log for what happened when. Projects are indexed by their frontmatter, no index file to maintain.
- **Skills** (`skills/`): `daily-log` and `project-docs` teach the agent the formats; `bin/sync_skills.py` installs them as project skills. Add your own skills next to them.
- **Scripts** (`bin/`, Python standard library only): list unfinished tasks, summarize a day, list projects, a live task board, and `lint_vault.py`, which checks frontmatter, links, headings and task IDs and runs as a pre-commit hook.
- **Credentials stay out of the docs**: everything sensitive lives in a gitignored `asset/config.yaml`; docs only say where a credential is (`→ config.yaml: <key>`).
- **English and Chinese**: every rule file comes in both languages; the scripts understand headings in either.

## Quick start

Requirements: Python 3.10+, Git, [Claude Code](https://claude.com/claude-code); Obsidian is optional but recommended.

```bash
git clone https://github.com/hexhero/agent-work-vault.git my-vault
cd my-vault
python3 bin/setup.py --lang en --timezone Europe/Berlin --examples   # or --lang zh-CN
```

Then:

1. Fill in `PROFILE.md` (who you are, time zone, preferences) and `asset/services.md` (servers and services you use). Copy `asset/config.example.yaml` to `asset/config.yaml` for credentials.
2. Open the folder in Claude Code and say things like "record a task: …", "what's still open?", "I deployed demo v1.3 to production, log it", "create a project file for …".
3. Open the folder in Obsidian to browse the graph and the `overview.base` views. Run `python3 bin/board.py` for the task board.
4. `--examples` installed a demo project and two days of logs; delete them (`projects/demo*`, `task/2026-01-0*`, `task/details/error-tracking.md`) when you no longer need them.

## Layout

```
.
├── CLAUDE.md          Rules the agent follows (loaded every session)
├── PROFILE.md         About you (loaded every session)
├── projects/          One file per project, plus a same-name folder for Design and the project log
├── task/              Daily logs, task details, temp files (gitignored)
├── docs/              Long-lived guides and research notes
├── skills/            Skills (source); .claude/skills/ holds the generated entries
├── bin/               Scripts, see bin/README.md
├── asset/             Service list, credentials (config.yaml is gitignored)
├── examples/          Demo project and daily logs in each language
├── i18n/              The rule files in each language (bin/setup.py --lang switches)
└── vault.config.json  Language and time zone for the scripts
```

## Status and limitations

- Script output, comments and the task board UI are in Chinese for now; the docs, rules and skills are fully in English.
- The board's follow-up panel expects an optional background service that isn't part of this repo; without it the panel stays empty.

## License

[MIT](LICENSE)
