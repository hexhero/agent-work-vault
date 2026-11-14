---
type: project
name: demo
description: "Demo API: a small internal HTTP service that exports invoices as JSON and CSV for the finance team. Also called the invoice export service. Runs as a container on app01, deployed by tagging a release."
aliases:
  - Demo
  - Demo API
  - invoice export service
repo:
  - https://github.com/example/demo-api
hosts:
  - 192.0.2.10
---
# Demo API

- **Summary**: internal HTTP service (Python + FastAPI) that exports invoices from the read-only database as JSON and CSV; the finance team uses it for month-end reports.
- **Current status** (2026-01-06): running in production; CSV export in progress, see "Phases and progress" in the [Design](demo/design.md).

## Location

| | Staging | Production |
| --- | --- | --- |
| Host | app01 (`192.0.2.10`) | app01 (`192.0.2.10`) |
| Directory | `/srv/demo-staging` | `/srv/demo` |
| Container | `demo-staging-api-1` | `demo-api-1` |
| URL | `https://staging.demo.example.com` | `https://demo.example.com` |
| Deploy | push a `v*-rc*` tag | push a `v*` tag |

## Resources

| Category | Resource | Used for |
| --- | --- | --- |
| Servers | app01, see [service list](../asset/services.md#servers) | Runs both environments |
| Databases and storage | example_db, see [service list](../asset/services.md#databases) | Source of invoice data (read-only) |
| External services | GitHub Actions | Builds the image and deploys on tags |
| Accounts and credentials | Database user `readonly` → config.yaml: `example_db`; deploy user → config.yaml: `ssh.app01` | |
| Downstream | Finance month-end spreadsheet | Reads `/export/invoices.csv`; check with Alice Chen before changing columns |

## Read on demand

| File | When to read |
| --- | --- |
| [design.md](demo/design.md) | Before changing the API or the export format; phases and progress |
| [log.md](demo/log.md) | To see what was decided or shipped when |

## Where to look

- Running version: `curl https://demo.example.com/version`
- Settings: `.env.example` in the repository; the real `.env` is in `/srv/demo` on app01

## How to

- **Release**: merge to `main`, push a `vX.Y.Z-rc1` tag, check staging, then push `vX.Y.Z`.
- **Roll back**: push the previous version's tag again.

## Red lines

- Don't change the CSV column order without asking: the finance spreadsheet reads columns by position.

## Pitfalls

- Timestamps in the database are UTC; convert to the customer's time zone only at export time (verified 2026-01-05).

## Related

- [daily-log](../skills/daily-log/SKILL.md), [project-docs](../skills/project-docs/SKILL.md)
