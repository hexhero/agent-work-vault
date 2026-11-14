---
type: task-doc
project: []
log: "[[2026-01-06]]"
---
# Choose a hosted error-tracking service

> Task log: [2026-01-06](../2026-01-06.md)

## Need

Get alerted when the Demo API throws, with the request that caused it.

## Options

| | A: hosted SaaS | B: self-hosted |
| --- | --- | --- |
| Setup | 10 minutes, SDK only | A VM plus upgrades |
| Cost | Free tier is enough for now | VM cost and our time |
| Data | Leaves our network | Stays on app01 |

## Recommendation

A, unless error payloads may contain customer data that must not leave the network; that's the decision needed.
