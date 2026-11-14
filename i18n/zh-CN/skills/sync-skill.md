# skill 安装与同步

本目录（`skills/`）是 skill 的唯一来源。Agent 要把这里的 skill 装成本仓库的项目 skill（`.claude/skills/`），才能按名字和触发词自动调用。

安装和同步都用 [bin/sync_skills.py](../bin/README.md) 做，不手工生成入口：`bin/sync_skills.py` 安装 / 同步，`bin/sync_skills.py --check` 只检查。下面是脚本遵循的规则。

## 约定

- **源**：`skills/<name>/SKILL.md`，内容、脚本、`config.json` 都只放在这里。
- **目录名 = skill name**：`skills/` 下的目录名必须和 `SKILL.md` frontmatter 里的 `name` 一致；不一致时以 `name` 为准改目录名，并用 `grep` 把引用旧路径的地方改过来。
- **安装位置**：本仓库的 `.claude/skills/<name>/SKILL.md`，只在本仓库生效。不装到用户级 `~/.claude/skills/`。
- **只装 skill 目录**：`skills/` 下带 `SKILL.md` 的子目录才算 skill；本文件这类说明文档不装。

## 安装

安装不是复制，而是放一个「入口」：名字和描述跟源一致，执行内容指回源目录。

对 `skills/` 下每个 skill，生成 `.claude/skills/<name>/SKILL.md`：

```markdown
---
name: <与源 SKILL.md 的 name 完全一致>
description: <与源 SKILL.md 的 description 完全一致>
---

本 skill 的实际内容在 `skills/<name>/SKILL.md`。先完整读取该文件，再严格按其中的说明执行；
命令在仓库根目录执行，源文件里写的脚本、配置路径都按它原样使用。
```

- frontmatter 只放 `name`、`description` 两项，逐字照抄源文件，不改写、不缩写。
- 正文用 `vault.config.json` 的 `language` 指定的语言（中文是上面这段，英文版见 `bin/sync_skills.py`）。
- 入口目录里只有这一个 `SKILL.md`，不复制脚本、`config.json`、参考文档等任何其他文件。凭据始终只在源目录。

## 同步

以 `skills/` 为准，检查 `.claude/skills/` 是否对齐：

| 情况 | 处理 |
|---|---|
| 源里有、入口没有 | 按「安装」补装 |
| 入口有、源里没有（被删或改名） | 删除该入口 |
| `name` 或 `description` 不一致 | 用源的值覆盖入口 |
| 入口正文不是指向源的标准写法 | 按「安装」的模板重写 |

- 只比对 frontmatter 和入口正文；源 skill 的正文、脚本改了不用同步，入口每次都会去读源文件。
- 什么时候同步：拉取本仓库更新后、新增 / 删除 / 改名 skill 后，或用户要求时。
- 同步完在回复里列出补装、删除、更新了哪些 skill。
