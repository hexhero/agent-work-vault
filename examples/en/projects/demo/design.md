---
type: project-doc
project: "[[demo]]"
---
# Demo API design

> Only the current design. Dated decisions and implementation records are in the [project log](log.md).

## Goals and scope

- Give the finance team invoices for any date range without database access.
- Out of scope: editing invoices, customer-facing access.

## Architecture

- One FastAPI service, stateless; reads `example_db` through the `readonly` user.
- `GET /export/invoices?from=&to=&format=json|csv`; times are converted to the customer's time zone on export.

## Phases and progress

| Phase | Scope | Milestones | Status | Done on |
| --- | --- | --- | --- | --- |
| Phase 1 | JSON export with correct time zones | — | Done | 2026-01-05 |
| Phase 2 | CSV export for the month-end spreadsheet | See below | In progress | |

Phase 2 milestones:

| Milestone | Who | Status |
| --- | --- | --- |
| 1. Agree the CSV columns with finance | User | Done |
| 2. Implement `format=csv` | AI | In progress |
| 3. Add test cases for every column | AI sub-agent (sonnet) | Not started |
| 4. Release to production | User | Not started |
