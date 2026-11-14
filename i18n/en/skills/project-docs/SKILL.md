---
name: project-docs
description: How to write and manage this repo's project files (projects/) - where a project's four kinds of content go (location, resources and pitfalls in the main file, design and progress in Design, what happened in the project log log.md), the main file's fixed sections, the resource table, pitfalls and pitfalls.md, how to split Design, the "Phases and progress" table, how to keep the project log, creating a project, reorganizing an old project file into the new structure. Load before writing anything under projects/, and when updating project files after project work. Triggers - update the project file, add to the project log, project log, note this pitfall, add it to the project, create a project file, tidy up this project file, where is the project at, update progress, write a design, split the design, what resources does the project use.
---

# project-docs — writing project docs

The red lines (when to read project files, whether changes need asking first) are in the "Projects" section of the root CLAUDE.md; this is how to write things. Run `bin/lint_vault.py` afterwards; it reports format problems.

For a sample, see the demo project in `examples/` (main file, Design with progress table, project log); `bin/setup.py --examples` installs it into `projects/`.

## What counts as a project

Not just software projects: anything long-lived you keep knowledge about and return to counts, such as a service, a customer, a product line, a recurring process (hiring, month-end close, on-call), an area of responsibility, a research area. A single piece of work with an end is a task and goes in the daily log. All fixed sections of the main file are optional; a customer or a process that has no "Location" or "Resources" simply leaves them out, with `repo` and `hosts` empty.

## A project's four kinds of content

| Content | Answers | Where | How |
| --- | --- | --- | --- |
| **Location and resources** | Where is it, where to look, what does it use | Main file `projects/<project>.md` | Rewrite, keep current |
| **Pitfalls** | What to watch out for | "Red lines" and "Pitfalls" in the main file; split into `projects/<project>/pitfalls.md` when there are many | Rewrite, delete stale ones |
| **Design and progress** | What the system looks like, why, what's planned, how far along | `projects/<project>/design.md`, `design-<topic>.md` | Rewrite, describe only the current design |
| **What happened** | What happened when | `projects/<project>/log.md` (project log) | Append only, never edit |

**Deciding where it goes**:

- What you follow when doing the work goes in the main file.
- What describes "how things are now" and gets rewritten when the design changes goes in Design.
- What is dated and won't change once past goes in the project log.
- A decision changed the design: one entry in the project log (date, who, why), and rewrite Design to the new design.
- A new conclusion replaces old content in the main file: move the old one to the project log and rewrite the main file, rather than appending a paragraph.

## Updating after the work

After project work, without asking first, go through the table below; say in your reply which file you changed and what.

| What happened | Update |
| --- | --- |
| Address, directory, container or deployment method changed | Main file "Location" |
| A server, database, internal / external service or credential was added or dropped | Main file "Resources" |
| Hit a pitfall the file doesn't mention | Conclusion in main file "Pitfalls" or `pitfalls.md`; the story in the project log |
| The user decided something, the plan changed | One entry in the project log; also change Design if the design is affected |
| Released, shipped, a milestone done | One entry in the project log; update the status in `design.md` "Phases and progress"; adjust the main file's "Current status" line if needed |
| Reached a debugging conclusion | One entry in the project log (may link to a task); if it will bite again, also put the conclusion in "Pitfalls" |
| Did something on the project (deploy to staging / production, restart, config change) | One entry in the project log; not repeated in the daily log's "Events" |
| The project's main file isn't organized into the fixed sections yet | Tidy it up while you're there, see the last section |

## Main file

**Record entry points and where to look**: projects move fast, and hard-coded values go stale without anyone noticing. Values that change with the code (service lists, counts, ports, timeouts, versions, current branch, etc.) are not copied in; write where to look them up instead. Put a verified date only where you actually state a fact.

**frontmatter**: only stable entry points; no values that change, such as ports or versions.

```yaml
---
type: project
name: demo                   # equals the file name
description: "What it is, what others call it, where it runs, how it's deployed - one or two sentences"
aliases:                      # other names people use for it
  - Demo
repo:                         # repository URLs
  - https://github.com/...
hosts:                        # deployment host IPs
  - 192.0.2.10
---
```

- `name` and `description` work like a skill's: `bin/projects.py` reads only these two to list all projects, to decide which project the work at hand belongs to and which file to read. So `description` must say **what it is, what others call it, where it runs**, with searchable keywords; no versions or progress. Wrap it in double quotes and don't use double quotes inside.
- `aliases`, `repo` and `hosts` feed [overview.base](../../overview.base).
- There is no separate index file under `projects/`; `name` and `description` are the index. In Obsidian, see the "Projects" view of [overview.base](../../overview.base).

**Opening**: below the title, a few bullets with a "Summary" and a single "Current status" line (at most two sentences, replaced wholesale each time, never appended to; if there's a Design, point to its "Phases and progress" table).

**Fixed sections**: in this order, with these names; leave out sections that have no content.

| Section | Contents |
| --- | --- |
| `## Location` | Repository, hosts per environment, deploy directory, containers, public address, how deployment is triggered. Use a table for several environments |
| `## Resources` | Resources the project uses, see "Resource table" below |
| `## Read on demand` | Which files are in the same-name folder and which to read for what. Required whenever the folder exists |
| `## Where to look` | Which command, file, table or API to check for values that change |
| `## How to` | Step outlines for operations such as releasing, rolling back, adding a config entry |
| `## Red lines` | Things you must ask the user about before touching. Only what the user has explicitly set; don't add your own |
| `## Pitfalls` | Easy ways to get it wrong, see "Pitfalls" below |
| `## Related` | Related projects and skills, as relative Markdown links |

**Split when too long**: when the main file exceeds about 16KB (lint warns), move content needed only for certain kinds of work into sub-files of the same-name folder and keep only what's needed every time. Domain knowledge of a particular code repository (vendor API quirks, etc.) is better written into that repository's `AGENTS.md` / README.

### Resource table

One table, three columns: category, resource, what it's used for. Categories:

| Category | Examples |
| --- | --- |
| Servers | Hosts per environment, jump hosts, scheduled jobs on the dev machine |
| Databases and storage | Databases, Redis, object storage, data directories on hosts |
| Internal services | The company's own services: gateway, auth, observability, platform API, other projects |
| External services | Third parties: identity provider, CI, vendor APIs, documentation sites |
| Accounts and credentials | Which account is used and where its credentials are. **Only where they are, never the value**, see below |
| Downstream | Services and tools that depend on this project; check them before changing interfaces |

- **Resources and credentials point to `asset/`**:
  - **Resources**: each row links to the matching section of the service list (the file under `asset/` named in PROFILE "Assets"). The project may repeat a resource's details (address, host name, port, directory) for convenience; if the two disagree, `asset/` wins, and fix both when you notice.  Other projects are written as project links.
  - **Credentials**: a project file may **only say where a credential is stored**, never the value or any part of it. Three ways to write the location: `→ config.yaml: <key>` (in `asset/config.yaml`); a file path and variable name on a host (e.g. "`XXX` in `/data/.../secrets.env` on app01"); an `.env` file name and variable name in a code repository. Passwords, tokens, API keys and passwords inside connection strings all count as credentials, and must not appear in Design, the project log or pitfalls either.
- If the project uses a resource that isn't in the service list yet, add its address there (no need to ask first; say so); the value of a new credential goes only into `asset/config.yaml`, per "Sensitive information" in CLAUDE.md.

### Pitfalls

- Write only **the conclusion and how to avoid it**, with a verified date. How it was found, ticket numbers and figures at the time go in the project log.
- Keep "Red lines" and "Pitfalls" apart: red lines need asking the user first; pitfalls are easy mistakes.
- Delete ones that were fixed or no longer hold, and note it in the project log.
- When the main file is over the limit, split into `projects/<project>/pitfalls.md`: level-2 headings by topic (auth, deployment, a subsystem …); the main file keeps only the few that can bite any time, and the "Read on demand" table says when to read the rest. Lint warns when `pitfalls.md` exceeds about 32KB.

## Design

- **Contents**: goals and scope, architecture, data model, interfaces, key trade-offs and reasons, later phases not yet started, the "Phases and progress" table.
- **Describe only the current design**: no "design changes" or "decision of some day" sections; dated decisions and implementation records go in the project log. Differences between implementation and design go in the project log; if the difference is permanent, change Design to match reality too.
- **Split by topic, not by time**: `design.md` is the overview (goals, scope, architecture, "Phases and progress", and a list of the other design files); one `design-<topic>.md` per subsystem or phase. Lint warns when one exceeds about 32KB; split further by topic then.
- **Don't copy designs whose original lives in a code repository**; write the path in the main file's "Where to look".
- Ask the user before creating a Design file.

### Phases and progress

Plan and progress live in the "Phases and progress" section of `design.md`, one table, rewritten in place:

```markdown
| Phase | Scope | Milestones | Status | Done on |
| --- | --- | --- | --- | --- |
| Phase 1 | … | See below | In progress | |
| Phase 2 | … | TBD | Not started | |
```

- The phase in progress may expand into a milestone table; a finished phase collapses into one row, with details in the project log.
- **The milestone table says "Who"**: when breaking a phase into milestones and tasks, decide for each one who does it, per "Sub-agents and cheaper models" in CLAUDE.md, and fill in the "Who" column: `User`, `AI` (main session), `AI sub-agent (haiku / sonnet)`. Well-scoped, easily verified mechanical work goes to a sub-agent on a cheaper model; judgement, user decisions and outward actions stay in the main session.

  ```markdown
  | Milestone | Who | Status |
  | --- | --- | --- |
  | 1. Agree the CSV columns | User | Done |
  | 2. Implement the export endpoint | AI | In progress |
  | 3. Add 20 test cases for export formats | AI sub-agent (sonnet) | Not started |
  | 4. Rename the old field names across the docs | AI sub-agent (haiku) | Not started |
  ```
- Every status change gets an entry in the project log. The main file's "Current status" is one sentence pointing to this table.
- A small project without phases doesn't need a Design just for a progress table; the main file's "Current status" line is enough.

## Project log (log.md)

- **Contents**: who decided what on which day and why, design changes, milestones, release and deployment records, debugging conclusions, differences between implementation and design, estimates. Only changes to the system and project itself; external communication (ticket comments and status, chat messages, email) does not go here but in the daily log's "Events". Progress and events of project tasks are recorded **only here**; the daily log keeps a single task entry and doesn't repeat them (see "Project tasks" in [daily-log](../daily-log/SKILL.md)).
- **Granularity**: one entry per thing, at the level of "something got done / a feature reached staging or production". Individual commits or retries aren't recorded; git has them. Follow-ups on the same thing on the same day go into that day's entry rather than a new one.
- **Format**: reverse date order, newest on top, one level-2 heading `## YYYY-MM-DD` per day; below it one bullet per thing saying what was done or decided, who decided, why and the result (version, commit, ticket). Lint checks the headings and order.

```markdown
---
type: project-doc
project: "[[demo]]"
---
# Demo project log

## 2026-11-04

- `v1.2.3` to staging and production: fixed the export time zone (PROJ-123, `0082fef`). Story in the [task details](../../task/details/xxx.md).
```

- **Append only**: never edit an entry once written; if it turns out to be wrong, add a new correcting entry.
- **May link to tasks**, with relative paths (`../../task/details/xxx.md`, `../../task/YYYY-MM-DD.md`). The main file, Design, pitfalls and other material never link to tasks.
- Create it the first time you need it, without asking; when you do, add a row to the main file's "Read on demand" table.
- Several sessions may write at once: re-read right before changing it, append locally, never overwrite the whole file.
- **Archive by quarter when too long**: when `log.md` exceeds about 64KB (lint warns), move the previous quarter and older wholesale into `log-YYYYqN.md` (e.g. `log-2026q4.md`, same format); `log.md` keeps only the current quarter.
- To see what every project recorded on a given day, use `bin/day_summary.py [date]`.

## The same-name folder projects/<project>/

- Besides `design*.md`, `log.md` and `pitfalls.md`, it can hold on-demand how-tos, product plans, background material, release records maintained by scripts, etc.; the main file's "Read on demand" table says when to read each.
- Only things whose original isn't in a code repository. A task's process goes in `task/details/`; once settled, long-lived design moves into Design and conclusions into the project log.
- File names use lowercase letters, digits and hyphens `-`, and start with frontmatter: `type: project-doc`, `project: "[[project file name]]"`.
- Ask the user before creating one, except the project log `log.md`, a `pitfalls.md` split out of an oversized main file, and files maintained by scripts (e.g. `<project>/deploy-log.md`).

## Creating a project

1. Ask the user first.
2. Use lowercase letters and hyphens for the file name; write the frontmatter, opening and fixed sections per "Main file".
3. Run `bin/projects.py` to check the new project is listed and its `description` reads clearly.

## Reorganizing an old project file into the new structure

Lint summarizes main files that aren't organized yet. **Tidy whichever you touch**; don't do them in bulk. Steps:

1. Read the whole main file and same-name folder and decide, item by item, which of the four kinds it is.
2. Rewrite the main file: the two opening bullets, then everything into the fixed sections. Use tables for location and where-to-look where possible; build the resource table from text scattered across sections.
3. Turn dated history, release records and problems already fixed into project log entries, filed by date in `log.md`.
4. If the main file is still over the limit, split topic-based pitfalls into `pitfalls.md`.
5. Only move over "Red lines" the user explicitly set; if there are none, leave the section out.
6. **Don't lose a single technical fact**: after reorganizing, check against the original; where a date or owner is unclear, write it honestly in the log ("date not recorded") rather than guessing.
7. Run `bin/lint_vault.py`, and say in your reply which files it was split into, what was rewritten, and what you weren't sure about.

## Related

- [daily-log](../daily-log/SKILL.md): how to write the daily task log and task details
- Project list: `bin/projects.py`
