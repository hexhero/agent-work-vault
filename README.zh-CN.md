# agent-work-vault

[English](README.md)

和 AI agent 一起用的工作知识库：一个 Git 仓库，同时是 [Obsidian](https://obsidian.md) vault 和 [Claude Code](https://claude.com/claude-code) 项目。你跟 agent 说话，它按 `CLAUDE.md` 和几个 skill 里写的规则，帮你维护每日任务日志、项目文件和笔记；几个小脚本和 lint 保证这些东西都能检查。

它来自一位后端工程师每天在用的真实工作环境，去掉了所有个人和公司的内容。

## 有什么

- **每日日志**（`task/YYYY-MM-DD.md`）：跨项目的待办清单，带状态（未开始 / 进行中 / Review / Block / 完成 / 取消）、稳定的任务编号（`T-12`）、报告人标签，另有日志和事件流。agent 需要你决定时把任务推到 Review，没有你同意不会标记完成。
- **项目文件**（`projects/<项目>.md` 加 `projects/<项目>/`）：主文件写在哪、用到什么；Design 写设计和进度；只追加的项目日志记什么时候发生了什么。项目靠 frontmatter 索引，不用维护索引文件。
- **Skill**（`skills/`）：`daily-log`、`project-docs` 教 agent 这些格式；`bin/sync_skills.py` 把它们装成项目 skill。你自己的 skill 放在旁边就行。
- **脚本**（`bin/`，只用 Python 标准库）：列未完成任务、汇总某一天、列项目、实时任务看板，以及 `lint_vault.py`（查 frontmatter、链接、标题和任务编号，作为 pre-commit 钩子运行）。
- **凭据不进文档**：敏感信息都在 gitignore 掉的 `asset/config.yaml` 里，文档里只写存在哪（`→ config.yaml: <键>`）。
- **中英文**：规则文件都有中英两版，脚本两种语言的标题都认。

## 上手

需要：Python 3.10+、Git、[Claude Code](https://claude.com/claude-code)；Obsidian 可选，建议装。

```bash
git clone https://github.com/hexhero/agent-work-vault.git my-vault
cd my-vault
python3 bin/setup.py --lang zh-CN --timezone Asia/Shanghai --examples
```

然后：

1. 填好 `PROFILE.md`（你是谁、时区、偏好）和 `asset/services.md`（用到的服务器和服务）。凭据复制 `asset/config.example.yaml` 为 `asset/config.yaml` 再填。
2. 用 Claude Code 打开这个目录，说「记个任务：……」「还有哪些没做完」「demo v1.3 发生产了，记一下」「给……建个项目文件」。
3. 用 Obsidian 打开这个目录，看关系图和 `overview.base` 的视图。任务看板跑 `python3 bin/board.py`。
4. `--examples` 装了一个示例项目和两天的日志，不需要了就删掉（`projects/demo*`、`task/2026-01-0*`、`task/details/error-tracking.md`）。

## 目录

```
.
├── CLAUDE.md          agent 遵守的规则（每次会话加载）
├── PROFILE.md         关于你（每次会话加载）
├── projects/          一个项目一个文件，同名目录放 Design 和项目日志
├── task/              每日日志、任务详情、临时文件（已 gitignore）
├── docs/              长期的指南和调研
├── skills/            skill 源文件；.claude/skills/ 是生成的入口
├── bin/               脚本，见 bin/README.md
├── asset/             服务清单、凭据（config.yaml 已 gitignore）
├── examples/          各语言的示例项目和每日日志
├── i18n/              各语言的规则文件（bin/setup.py --lang 切换）
└── vault.config.json  脚本用的语言和时区
```

## 现状和限制

- 脚本的输出、注释和任务看板的界面目前是中文；文档、规则和 skill 中英文都齐。
- 看板的「跟进」面板需要一个可选的后台服务，不在本仓库里；没有它面板就是空的。

## 许可证

[MIT](LICENSE)
