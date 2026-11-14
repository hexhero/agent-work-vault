# Installing and syncing skills

This folder (`skills/`) is the single source of skills. An agent installs the skills here as this repo's project skills (`.claude/skills/`) so they can be invoked automatically by name and trigger words.

Installing and syncing are both done with [bin/sync_skills.py](../bin/README.md); never write entries by hand: `bin/sync_skills.py` installs / syncs, `bin/sync_skills.py --check` only checks. These are the rules the script follows.

## Conventions

- **Source**: `skills/<name>/SKILL.md`; content, scripts and `config.json` live only here.
- **Folder name = skill name**: a folder under `skills/` must have the same name as the `name` in its `SKILL.md` frontmatter; if they differ, `name` wins: rename the folder and `grep` for references to the old path.
- **Install location**: this repo's `.claude/skills/<name>/SKILL.md`, effective only in this repo. Never install into the user-level `~/.claude/skills/`.
- **Only skill folders are installed**: only sub-folders of `skills/` that contain a `SKILL.md` are skills; docs like this file are not installed.

## Installing

Installing is not copying but placing an "entry": same name and description as the source, with a body that points back to the source folder.

For each skill under `skills/`, generate `.claude/skills/<name>/SKILL.md`:

```markdown
---
name: <exactly the name from the source SKILL.md>
description: <exactly the description from the source SKILL.md>
---

This skill lives in `skills/<name>/SKILL.md`. Read that file in full first, then follow it exactly;
run commands from the repository root and use the script and config paths exactly as written there.
```

- The frontmatter holds only `name` and `description`, copied verbatim from the source, never rewritten or shortened.
- The body is in the language set in `vault.config.json` (`language`).
- The entry folder holds only this one `SKILL.md`; no scripts, `config.json`, reference docs or any other files are copied. Credentials always stay in the source folder.

## Syncing

`skills/` wins; check that `.claude/skills/` matches:

| Situation | Action |
|---|---|
| In the source, no entry | Install per "Installing" |
| Entry exists, source gone (deleted or renamed) | Delete the entry |
| `name` or `description` differs | Overwrite the entry with the source's values |
| Entry body isn't the standard pointer to the source | Rewrite it from the "Installing" template |

- Only frontmatter and the entry body are compared; changes to a source skill's body or scripts need no sync, since the entry always reads the source file.
- When to sync: after pulling updates to this repo, after adding / removing / renaming a skill, or when the user asks.
- After syncing, list in your reply which skills were installed, removed or updated.
