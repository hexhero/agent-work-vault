## Layout

```
.
├── PROFILE.md         Work profile (company, my role and reporting line, tech stack)
├── projects/          Projects, one file per project; bin/projects.py lists them all
│   ├── <project>.md   Project main file (repo, where it runs, how to deploy, pitfalls)
│   └── <project>/     Same-name folder: Design (design*.md), project log (log.md) and other material, created as needed
├── docs/              Reference docs (guides/ how-tos and tips, research/ research notes), index in docs/README.md
├── overview.base      Obsidian Bases overview: projects, task details, research, guides
├── task/              Task management
│   ├── YYYY-MM-DD.md  Daily log (tasks + log)
│   ├── details/       Details for complex tasks (ask the user before creating one)
│   └── temp/          Temporary files/scripts (gitignored), one folder per owner, see "Temporary files"
├── bin/               Tool scripts, see bin/README.md
├── asset/             Assets and reference material (service list, account names, org chart, etc., see "Sensitive information")
│   └── config.yaml    All credentials (gitignored, do not read)
├── skills/            Custom skills (see "Skills")
├── examples/          Example project and daily logs (install with bin/setup.py --examples)
├── i18n/              English and Chinese versions of the docs (switch with bin/setup.py --lang)
└── vault.config.json  Script config (language, time zone)
```

## Work profile

Who I am, my reporting line and tech stack, loaded in every session:

@PROFILE.md

## File permissions

- `task/`: read and write
- Everything else: read; ask the user before changing anything
- Exception: existing project files under `projects/` may be updated to match reality without asking first (see "Projects"); creating a new project file still needs asking
- Exception: when writing corrections and confirmed conventions back into a skill, `PROFILE.md` or `asset/` per "Memory", no need to ask first; say what you changed in your reply
- Exception: for `asset/config.yaml` see "Sensitive information" below

## Projects

The projects I own live in `projects/`, one file per project, with no separate index file: the `name` and `description` in each file's frontmatter are the index. How to write them (where the four kinds of content go, the fixed sections of the main file, the resource table, pitfalls, Design, the project log) follows the [project-docs](skills/project-docs/SKILL.md) skill; load it before writing anything under `projects/`.

- **Find projects with [bin/projects.py](bin/README.md)**: it reads `name` and `description` from each project file's frontmatter and lists what projects exist and what each one is. When unsure which project the work at hand belongs to, run it first (keywords allowed) instead of opening project files one by one.
- **Read before touching a project**: before working on a project (changing code, deploying, restarting, debugging, querying data), read its project file and follow the deployment steps and notes in it (if the main file has a "Read on demand" table, also read the sub-files relevant to the work at hand, not all of them); then run `bin/unfinished_tasks.py -p <project file name>` to see its unfinished tasks.
- **Update to match reality when done**: if reality differs from the file (address, directory, port, start-up arguments, deploy steps changed) or you hit a pitfall the file doesn't mention, fix and extend the file after the work, with the date you verified it. No need to ask first, but tell the user in your reply which file you changed and what.
- **Three places**: what you follow when doing the work goes in the main file (location, resources used, where to look, red lines, pitfalls; fixed section names); what the system looks like, the plan and progress go in Design; what happened when (decisions, milestones, releases, debugging conclusions) is appended to the project log `projects/<project>/log.md`, which may link to tasks. Main files not yet organized into the fixed sections are tidied up when you touch them.
- **Record entry points and where to look**: values that change with the code are not copied into project files; write where to look them up instead.
- **Ask before creating**: ask the user before creating a project file or a new material file under `projects/<project>/` (except the project log `log.md`, a `pitfalls.md` split out of an oversized main file, and files maintained by scripts).

## Tasks

Plain Q&A gets no task; anything that executes or changes something (editing files, running state-changing operations, multi-step work) is recorded in the day's `task/YYYY-MM-DD.md`. Log format, statuses and detail docs follow the [daily-log](skills/daily-log/SKILL.md) skill; load it before writing anything under `task/`. A few red lines:

- **Have a task before acting, without asking**: before starting, run `bin/unfinished_tasks.py`; if this work continues an unfinished task, use that one (set it to `[/]`); otherwise create one in today's log first, then start. Say in your reply which task it was recorded as.
- **Usually one task per session**: follow-up requests in the same session that belong to the same thing go on that task; only something clearly unrelated gets a new task, and say why it was split.
- **In progress when starting, Review when a human needs to look**: when you start on a task, change it to `[/]` in progress first; when it needs my decision, or is done, change it to `[?]` Review yourself and write down what I need to look at.
- **`[x]` needs the user's consent**: when done, ask whether it can be marked done and stay in Review until I agree. Other statuses you may change yourself; tell the user when you do.
- **When a task goes blocked, offer to watch it**: when a task becomes `[!]` (waiting on someone or an external condition), check whether [follow-up](skills/follow-up/SKILL.md) can watch that condition automatically; if it can, ask the user in your reply whether to add a follow-up item, and add it only if they agree; if it can't, say why and what would be needed. See "When a task goes blocked" in daily-log.
- **Query unfinished tasks with [bin/unfinished_tasks.py](bin/README.md)**, not by reading logs by hand or grepping.
- **Ask the user before creating a `task/details/` doc** (except when a task's sub-lines exceed 10 and are converted directly, or one created by background automation). Both project and non-project tasks can have one.
- **Project tasks stay thin on the task side**: a task linked to a project keeps a single entry in the daily log (status, title, project, ticket number), with links to material needed for the task hanging below it; progress, history, conclusions and events go on the project side and are not repeated in the daily log; if the task's own process needs a long write-up, create a `task/details/` doc. For "what did I do today", [bin/day_summary.py](bin/README.md) combines both sides.
- **Record events automatically, without asking**: every action that changes state gets one line; pure queries don't. Changes to the project itself (deploys, releases, restarts, config changes, decisions made on the project) go in the project log `projects/<project>/log.md`; everything else (changing tickets, sending messages, changing this repo's rules and skills, storing or reading credentials) goes under `## Events` in the daily log (`- HH:MM what was done`). See daily-log for the format.

## Sub-agents and cheaper models

When planning a project or breaking work into tasks, decide item by item whether a sub-agent on a cheaper model can do it, to save the main session's context and cost:

- **Good to hand off**: well-scoped work you can just follow and easily verify, such as bulk format or text edits, translation, checking a list of files, running checks and summarizing the results, adding tests from an existing spec, tidying data. Start a sub-agent with the Agent tool and pick a cheaper `model`: `haiku` for purely mechanical work, `sonnet` when it needs some judgement.
- **Keep in the main session**: design and trade-offs, anything the user must decide, outward actions (sending messages, changing tickets, deploying), anything touching credentials, changes that are hard to roll back.
- **Brief it fully**: a sub-agent only sees what you give it. State the goal, which files to read, what to change, what not to touch, how to verify, and what to hand back. Independent pieces can run as several sub-agents at once.
- **Verify what comes back**: the main session reviews the result and runs lint or tests before calling it done; task status, logs and commits stay with the main session.
- When the plan goes into a Design milestone table, fill in its "Who" column (see "Phases and progress" in [project-docs](skills/project-docs/SKILL.md)) and split the work that way when it starts.

## Temporary files

Temporary files, scratch scripts and exported data go in `task/temp/` (gitignored), not `/tmp` or elsewhere in the repo, and not directly in the root of `task/temp/`; one folder per owner:

| Owner | Folder |
| --- | --- |
| Produced by a skill | `task/temp/<skill name>/` |
| Belongs to a project | `task/temp/<project file name>/` |
| Belongs to a task | `task/temp/<task id>/` (e.g. `task/temp/T-12/`) |
| Not sure | Ask the user where to put it |

## Memory

Anything to remember across sessions goes into the repo first. Claude Code's built-in auto-memory lives outside the repo, has no history and other agents can't read it; treat it only as a buffer.

- **Find its home first**: corrections from me, confirmed conventions, tool pitfalls you hit go where they belong by content: project-related → the project file; how a skill does something → that skill; my preferences, external wording, dev machine → [PROFILE.md](PROFILE.md); service addresses and where to get keys → the service list in `asset/` (file name in PROFILE "Assets"); rules of this repo → this file. Rules (this file, skills) are rewritten to the current way of doing things, without who decided it when, how it used to be or what went wrong; those live in the daily log's events and git history. Facts in project files keep their verified dates as usual.
- **No need to ask, but say so**: change it directly and say in your reply which file you changed and what.
- **Only when there's no home does it go into auto-memory**; once it has a home, move it into the repo and delete the memory. Don't create a `MEMORY.md` in the repo.

## Links (Obsidian graph)

This repo is an Obsidian vault; files are connected into a graph by links:

- When mentioning a project, skill or doc in the repo, write a **relative Markdown link** (e.g. `[Demo](../projects/demo.md)`), not an inline-code path and not a `[[wikilink]]`; one link per target per paragraph is enough. Exception: frontmatter properties can only hold `"[[file name]]"`.
- **Tasks point to projects; projects don't link back to tasks**; only the project log `projects/<project>/log.md` may link to tasks. Long-lived conclusions drawn from a task go into the project files (main file, Design or project log).
- After moving or renaming a file, `grep` for the old path and fix the links.

## Sensitive information

- **Asset list**: `asset/` holds assets and reference material used at work (service list, account names, org chart, etc.; which file is which is in PROFILE "Assets"). Files other than `config.yaml` may be read directly; ask the user before changing them (generated files are regenerated by rerunning their script). These files **never contain passwords**; where a credential is involved, write `→ config.yaml: <key>`.
- **Credentials file**: `asset/config.yaml` holds all passwords, tokens and API keys; it is gitignored with mode 600. Unless the user explicitly asks, never read, print or commit it, and never copy its values into other files or command lines. The structure template is `asset/config.example.yaml`.
- Exclude `asset/config.yaml` when searching (grep, glob, etc.).
- When adding or changing an external service: the address goes in the service list, the password in `asset/config.yaml`. If a skill's `config.json` also holds this credential, change both.
- **Resources and credentials in project files point to `asset/`**: resources link to the matching section of the service list, and the project may repeat details such as the address; for credentials write only where they are stored (`→ config.yaml: <key>`, a file path and variable name on a host), never the value. See "Resource table" in [project-docs](skills/project-docs/SKILL.md).

## Skills (skills/)

`skills/` is the single source of this repo's skills; they are installed as project skills (`.claude/skills/`) and invoked by name and trigger words. The rules live only in [skills/sync-skill.md](skills/sync-skill.md); read it before touching a skill. The three that matter most:

- To add or change a skill, edit only the source in `skills/`, never the entry in `.claude/skills/`; after adding, removing or renaming one, or changing its `name` / `description`, run [bin/sync_skills.py](bin/README.md) and list what changed in your reply.
- The folder name must equal the `name` in `SKILL.md`.
- **Credentials**: in each skill folder's `config.json` (gitignored), also collected in `asset/config.yaml`. Never read, print or commit these files.

## Checks

Before committing doc changes, run [bin/lint_vault.py](bin/README.md); it checks frontmatter, links, indexes and log formats. The pre-commit hook runs it too (`git config core.hooksPath .githooks`). The rules are written in this file, [project-docs](skills/project-docs/SKILL.md) and [daily-log](skills/daily-log/SKILL.md); lint is their machine version, so change them together.

## Git

- Claude may commit and push on its own
- Use the committer name and email written in PROFILE "Git"
