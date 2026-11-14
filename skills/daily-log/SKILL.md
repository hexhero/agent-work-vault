---
name: daily-log
description: How to write this repo's daily logs (task/YYYY-MM-DD.md) and task detail docs (task/details/) - recording a task, backfilling one, changing status (not started / in progress / Review / blocked / done / cancelled), marking done, recording events, writing log entries (meeting notes, findings), creating detail docs. The daily log is a cross-project to-do list plus things that belong to no project; a task linked to a project keeps a single line, and progress, conclusions and project events go in the project log (per project-docs). Load before writing anything under task/. For listing unfinished tasks see the Tasks section of CLAUDE.md. Triggers - record a task, add to today's tasks, backfill a task, mark done, this task is finished, set to blocked, set to Review, log this, write a log entry, record an event, create a detail doc, turn this task into a detail doc.
---

# daily-log — writing the daily log

The red lines (what to record, when a task may be ticked done) are in the "Tasks" section of the root CLAUDE.md; this is how to write things. Run `bin/lint_vault.py` afterwards; it reports format problems.

## Decide where it goes first

The daily log only tracks "what needs doing and whether it's done": a cross-project to-do list, plus things that belong to no project. A project's knowledge and history live on the project side, written per [project-docs](../project-docs/SKILL.md).

| Content | Where |
| --- | --- |
| Task entries (project and non-project alike) | Daily log "Tasks" |
| A project's progress, history, debugging conclusions, decisions | Project log `projects/<project>/log.md` |
| Changes to the project itself: a feature reached staging / production, a release, a restart, a config change | Project log; not repeated in the daily log |
| External communication: ticket comments and status (ClickUp etc.), chat messages, email (project-related or not) | Daily log "Events" |
| Things that belong to no project: changing this repo's rules and skills, HR lookups, research, credentials | Daily log "Events" / "Log" |
| Meeting notes, non-project findings | Daily log "Log" |

- The project log only records changes to the system and the project; communication is about people and tickets and stays in the daily log.
- For "what did I do today" use `bin/day_summary.py`; it combines the day's entries from every project log with the daily log.

## File format

- One file per day, `task/YYYY-MM-DD.md` (today's date); create it if missing.
- The date lives in the file name; entries only carry `HH:MM` (24-hour, to the minute). Take the time in the user's time zone from PROFILE (e.g. `TZ=Europe/Berlin date +%H:%M`); when the machine clock is in another zone, plain `date` is off by hours.
- **Several sessions write the same day's log at once**: re-read right before changing it, make only local appends or replacements, never overwrite the whole file with content you read earlier. Before committing, look at `git status` / `git diff --stat`; if an unusual number of lines were deleted, stop and investigate. Another session may already have committed your change along with theirs; then just confirm the content is in HEAD and don't rewrite history.
- The file has three parts under three level-2 headings in a fixed order: `## Tasks`, `## Log`, `## Events`. Leave out a heading if that part is empty for the day.
- Mention projects and skills in the repo as relative Markdown links.

```
## Tasks

- [/] 10:00 T-12 [PROJ-123 exported times are 8 hours off](https://app.clickup.com/t/xxx) #reporter/AliceChen
  - Project: [Demo](../projects/demo.md)
- [ ] 11:00 T-13 Sort out expense claims

## Log

### 14:30 Weekly meeting notes

Body (list or paragraphs).

## Events

- 10:44 ClickUp PROJ-123 set to dev done, comment added
- 15:20 Changed the event rules in the daily-log skill, committed and pushed (2e6abf1)
```

## Tasks

```
- [ ] 10:00 T-12 Title
- [/] 10:00 T-12 Title
- [?] 10:00 T-12 Title
  - Pending: option A or B
- [!] 10:00 T-12 Title
  - Blocked on: waiting for xxx to release
- [x] 10:00 - 11:30 T-12 Title
```

### Sub-line limit

A task has at most 10 sub-lines (the "Project" line, "Blocked on" line, material lines and notes all count), for project and non-project tasks alike; lint checks it. What to do when it's exceeded is in the two sections below.

### Task ID

Every task has an internal ID `T-N`, written after the time and before the title, increasing globally and never reset per day. It is the task's stable handle ("set T-12 to blocked") and lives alongside any ticket number (e.g. a ClickUp ID).

- **Get the number first**: run `bin/unfinished_tasks.py --next-id` and use the number it gives.
- **The ID stays with the line**: changing status or title never changes it; it stays after done or cancelled, so references elsewhere still resolve.
- **Look up by ID**: `bin/unfinished_tasks.py --id T-12`, including done and cancelled ones.
- Subtasks get no ID.
- Two sessions recording tasks at the same time may take the same number; `bin/lint_vault.py` catches duplicates at commit time. On a clash, give the later one a freshly taken number.

### Reporter

For a task someone else assigned, or one whose result goes to a specific person, add the tag `#reporter/<name>` at the end of the task line, e.g. `#reporter/AliceChen`.

```
- [/] 12:00 T-11 Estimate the new report design #reporter/AliceChen
```

- **Name format**: the English name without spaces, each part capitalized (Alice Chen → `AliceChen`), as written in the org chart listed in PROFILE "Assets"; always the same spelling for the same person. People outside the company, such as customers, follow the same format.
- **Position**: only at the end of a top-level task line, preceded by a space; after a `→ [Details](…)` link if there is one, and after the type tag (see "Type tag") if there is one. One per task; never on subtasks or sub-lines.
- **When to add it**: add it when you know who assigned the task; a ticket's reporter or the person asking in chat both count. The user's own tasks get none. If unsure who it is, leave it out; don't guess.
- **Stays with the line**: kept through status changes, done and cancelled.
- **Query by reporter**: `bin/unfinished_tasks.py --reporter AliceChen`; the task board shows the reporter on cards and in details.

### Type tag

A task line may end with one type tag `#type/<type>` saying what kind of task it is. There is currently one:

| Tag | Meaning |
|---|---|
| `#type/message` | Someone reached me on a chat tool (@-mention, direct message, my name) and I need to reply or act; tasks created by an automated inbox always carry it |

- Like the reporter tag it goes at the end of the top-level task line; when both are present the type comes first: `… → [Details](…) #type/message #reporter/BobLi`. One type per task; never on subtasks or sub-lines.
- Types are lowercase letters, digits and hyphens. Kept through status changes, done and cancelled.
- Query by type: `bin/unfinished_tasks.py --type message`; the task board shows it on the card.

### Status

| Mark | Status | When |
|---|---|---|
| `[ ]` | Not started | Recorded, not started |
| `[/]` | In progress | Work has started |
| `[?]` | Review | The AI is done, or halfway and needs the user's decision; write below what the user needs to look at |
| `[!]` | Blocked | Stuck, waiting on someone else; write below what it is blocked on and who it is waiting for |
| `[x]` | Done | Only with the user's consent |
| `[-]` | Cancelled | Not doing it |

You may switch freely between not started, in progress, Review and blocked; tell the user in your reply when you do. When the blocker is gone, set it back to `[/]` and delete the "Blocked on" line.

When the AI works a task, statuses go like this, without asking first:

1. **Starting**: set the task to `[/]` in progress, then do the work.
2. **Needs the user's decision** (choosing an option, granting access, confirming an external action), or **done**: set it to `[?]` Review and add a line `- Pending: …` below it saying what the user needs to decide, or "Done, awaiting acceptance" plus one line on the result. Say in your reply that it moved to Review.
3. **The user decided and work continues**: set it back to `[/]` and delete the "Pending" line.
4. **The user agrees it's done**: tick `[x]` per "Marking done". Without consent it stays in Review; don't tick it yourself.

Review means waiting for the user; blocked means waiting for someone else or an external condition. Don't mix them up.

### Project tasks

Tasks linked to a project.

- The entry **stays a single line**: status, time, task ID, title, ticket number, reporter tag.
- Below it hangs a `- Project: [xxx](../projects/xxx.md)` line (`bin/unfinished_tasks.py -p` filters by project with it); a blocked task adds a "Blocked on" line, a Review task a "Pending" line. Keep the "Project" line after completion; don't move the link into the title.
- **Material lines are fine**: material needed for this task, one line per purpose (e.g. "Follow", "Entry point", "If it breaks, check"), only a link and a short note, so nothing needs hunting down when you start. Point at project files, Design, online docs and pages; don't copy their content.
- No progress, history or conclusions as notes; those go in the project log. Over 10 sub-lines: trim, move content to the project side, or convert to a `task/details/` doc.
- If the task's own process (investigation, option comparison, drafts) needs a long write-up, create a `task/details/` doc and add `→ [Details](details/xxx.md)` to the entry; long-lived design and conclusions still get merged into the project's Design, project log or pitfalls.

### Non-project tasks

- Notes may go under the entry.
- Over 10 sub-lines: convert to a `task/details/` doc directly (no need to ask), leave one sentence plus `→ [Details](details/xxx.md)` on the entry, and tell the user afterwards.
- With a detail doc, the entry is one sentence; details go in the doc.

### Recording a task

1. Run `bin/unfinished_tasks.py` first (`-p` for a project, `--ref` for a ticket number): if this work continues an unfinished task, suggest linking it to that one and update the original entry instead of starting a new one.
2. Only add it when the user says so. When backfilling, the start time is when work started; take the ID from `bin/unfinished_tasks.py --next-id`; if you know who assigned it, add a reporter tag at the end (see "Reporter").
3. When adding, splitting or merging tasks, tell the user exactly which ones were added / split / merged and why.
4. Follow-up steps of the same thing (first an idea, then research, then a refined plan) are the same task: update the original entry. The follow-up content goes on in the project log for project tasks, or in the same detail doc if there is one.

### Marking done

1. When done, set the task to `[?]` Review and ask the user whether it can be marked done.
2. Once the user agrees, locate the entry by the file and line number from `bin/unfinished_tasks.py`, tick `[x]` and add the end time (`start - end`).
3. Until the user agrees, it stays in Review.

## Events

Recorded automatically, **without asking the user**, and without mentioning it in your reply. Every action I take that changes state gets one line; changes to the project itself go in the project log, everything else is appended here in time order.

- Recorded here: changing tickets (status, comments, dependencies), sending chat messages / email, changing this repo's rules / skills / docs and committing and pushing, storing, reading or rotating credentials, adding tasks or changing task status, and any other state change that belongs to no project.
- Recorded in the project log: deploys, releases, restarts, project config changes, decisions made on the project.
- Not recorded: pure queries, reading files, running read-only scripts, drafts (not sent), the stream of individual commits.
- Format: `- HH:MM what was done`, one thing per line, naming the object and result (commit hash, ticket number). No checkboxes, no nested lists.

## Log

Things written down for reference that need no status tracking, such as meeting notes and non-project findings.

- Each entry starts with a level-3 heading `### HH:MM Title`; the body is free-form, but **no checkboxes** (`bin/unfinished_tasks.py` treats checkboxes as tasks).
- Log entries aren't tasks; no need to ask whether they're done.
- Project conclusions don't go here; they go in the project log.

## Detail docs (task/details/)

- Project and non-project tasks can both have one; ask the user before creating it (except the "over 10 lines, convert directly" case above and docs created by background automation). For a project task, put the project in the frontmatter `project`.
- File names use only lowercase letters, digits, hyphens `-` and underscores `_`, with a `.md` suffix.
- Start with frontmatter, and below the title link the task's daily log as a Markdown link:

```markdown
---
type: task-doc
project: []
log: "[[2026-10-13]]"
---
# Title

> Task log: [2026-10-13](../2026-10-13.md)
```

- For a project detail doc (frontmatter `project` not empty), long-lived design and conclusions get merged into the project's Design, project log or pitfalls when the task is done.

## Related

- [project-docs](../project-docs/SKILL.md): how to write project docs; the project log lives there
