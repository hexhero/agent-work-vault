# Work profile

> Template: replace the placeholders with your own details. CLAUDE.md loads this file into every session, so keep it short.

## Company

**Example Corp**, what the company does in one line. Where the team works.

## Me

- Name: Your Name
- Email: you@example.com
- Role: your title
- Team / department:
- Reporting line: your manager → their manager

## Preferences

- **Time zone**: e.g. Europe/Berlin. "Today", "yesterday", "6 pm" mean this time zone; times in replies and in the daily log use it too. If the machine clock is in another zone, take the time with `TZ=Europe/Berlin date`; the scripts read the time zone from `vault.config.json`.
- **Language**: which language to talk to me in, and when output (docs, message drafts) should be in another language.
- How to refer to products externally, things never to share outside, and similar rules.

## Assets

- Service list: [asset/services.md](asset/services.md) (servers, databases, internal services, where to get keys)
- Org chart: optional, e.g. `asset/org-chart.md`; names in task `#reporter/` tags follow it
- Credentials: `asset/config.yaml` (gitignored), template `asset/config.example.yaml`

## Git

- Committer for this repo: name `claude`, email `claude@example.com` (set with `git config user.name` / `user.email`)

## Dev machine

- Host, where code repositories are cloned, tool quirks worth knowing.

## Tech stack

- Languages, databases, frameworks you use.
