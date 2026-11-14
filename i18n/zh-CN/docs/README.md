# docs — 工作参考文档

长期要查的参考知识，按性质分两个子目录。负责的项目在根目录的 `projects/`（`bin/projects.py` 列出全部），每天的任务和临时排查在 `task/`，都不放这里。

## 约定

- guides / research 各有一个 README，固定写三块：这个目录放什么（和同级目录的区别）、约定、索引。本文件只链到这两个 README，不越级列文档。
- 再往下的主题子目录（如 `guides/git/`）只放文档时不建 README，由上一级 README 在索引里按 `###` 分组列出。
- 文档开头写 frontmatter，`type` 和目录对应：`guide` / `research`。在 Obsidian 里打开根目录的 [overview.base](../overview.base) 能按类型看到全部文档，连同项目和 `task/details/` 详情文档。

## 索引

| 目录 | 放什么 |
| --- | --- |
| [guides/](guides/README.md) | 用法和技巧：自己要用、要记住的工具用法和指南，持续更新。按工具或领域分子目录 |
| [research/](research/README.md) | 调研：技术调研和选型对比，是某个时间点的判断，会过时。按主题分子目录 |
