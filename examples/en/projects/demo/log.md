---
type: project-doc
project: "[[demo]]"
---
# Demo API project log

## 2026-01-06

- CSV columns agreed with Alice Chen: same order as the month-end spreadsheet, dates as `YYYY-MM-DD`. Implementation started ([task](../../task/2026-01-06.md) T-3).

## 2026-01-05

- `v1.2.3` to staging and production: export times were 8 hours off because UTC timestamps were formatted without conversion; now converted to the customer's time zone on export (PROJ-123, [task](../../task/2026-01-05.md) T-1). Phase 1 done.
