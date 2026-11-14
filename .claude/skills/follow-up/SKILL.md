---
name: follow-up
description: Automatic follow-up for blocked tasks - one background loop checks the conditions you are waiting for (a PR merged, a page changed, a ticket moved, someone replied) with cheap scripts called watchers, and only when a condition is met starts a cheaper model to update the task (back to in progress or to Review). Not tied to any external system - bundled watchers cover web pages and GitHub PRs, and you add your own for Jira, Slack, ClickUp, email and so on. Use when a task becomes blocked, to check whether its condition can be watched and add a follow-up item if the user agrees. Triggers - watch this for me, follow up on this, tell me when X is merged, when they reply, add a follow-up item, list follow-up items, cancel the follow-up, is the follow-up loop running, add a watcher.
---

This skill lives in `skills/follow-up/SKILL.md`. Read that file in full first, then follow it exactly;
run commands from the repository root and use the script and config paths exactly as written there.
