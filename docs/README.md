# docs — reference docs

Long-lived reference knowledge, in two sub-folders. Projects you own live in `projects/` at the root (`bin/projects.py` lists them), daily tasks and ad-hoc investigations in `task/`; neither goes here.

## Conventions

- guides and research each have a README with three parts: what the folder holds (and how it differs from its sibling), conventions, index. This file only links to those two READMEs, never to individual docs.
- Topic sub-folders further down (e.g. `guides/git/`) that only hold docs get no README; the parent README lists them under a `###` group in its index.
- Docs start with frontmatter whose `type` matches the folder: `guide` / `research`. Open [overview.base](../overview.base) at the root in Obsidian to see every doc by type, together with projects and `task/details/` docs.

## Index

| Folder | Contents |
| --- | --- |
| [guides/](guides/README.md) | How-tos and tips: tool usage and guides you need to remember, kept up to date. Sub-folders per tool or area |
| [research/](research/README.md) | Research: technical research and comparisons, a judgement at a point in time that will go stale. Sub-folders per topic |
