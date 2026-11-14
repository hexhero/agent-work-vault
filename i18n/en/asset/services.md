# Service list

Addresses of the servers, databases and services you use at work, and where their credentials are. **Never write passwords here**; write `→ config.yaml: <key>` instead. Project files link to the sections below.

## Servers

| Name | Address | What runs there | Login |
| --- | --- | --- | --- |
| app01 | 192.0.2.10 | Demo API (see the demo project) | `deploy` user, → config.yaml: `ssh.app01` |

## Databases

| Name | Address | Notes |
| --- | --- | --- |
| example_db | 192.0.2.20:5432 | Read-only replica, → config.yaml: `example_db` |

## External services

| Service | URL | Account |
| --- | --- | --- |
| GitHub | https://github.com | → config.yaml: `github.token` |
