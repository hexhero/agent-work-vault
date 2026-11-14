## 目录结构

```
.
├── PROFILE.md         工作档案（公司、我的职位和汇报线、技术栈）
├── projects/          项目，一个项目一个文件；bin/projects.py 列出全部
│   ├── <项目>.md      项目介绍（仓库、部署位置、部署方式、踩过的坑）
│   └── <项目>/        同名目录：Design（design*.md）、项目日志（log.md）和其他资料，按需创建
├── docs/              工作参考文档（guides/ 用法和技巧、research/ 调研），索引见 docs/README.md
├── overview.base      Obsidian Bases 总览：项目、任务详情、调研、指南
├── task/              任务管理
│   ├── YYYY-MM-DD.md  每日日志（任务 + 日志）
│   ├── details/       复杂任务详情（创建前问用户）
│   └── temp/          临时文件/脚本（已 gitignore），按归属分目录，见「临时文件」
├── bin/               工具脚本，说明见 bin/README.md
├── asset/             资产和参考资料（服务清单、账号名、组织架构等，见「敏感信息」）
│   └── config.yaml    凭据汇总（已 gitignore，禁止查看）
├── skills/            自定义技能（见「技能」）
├── examples/          示例项目和每日日志（bin/setup.py --examples 装进来）
├── i18n/              中文、英文两套文档（bin/setup.py --lang 切换）
└── vault.config.json  脚本的配置（语言、时区）
```

## 工作档案

我的身份、汇报线和技术栈，每次会话自动加载：

@PROFILE.md

## 文件权限

- `task/` 目录：可读写
- 其他目录：可读，修改前需得到用户确认
- 例外：`projects/` 下已有的项目文件，按实际情况补充修改不用事先确认（见「项目」）；新建项目文件仍要先问
- 例外：按「记忆」一节把我纠正的做法、确认过的约定写回 skill、`PROFILE.md`、`asset/` 时不用事先确认，改了在回复里说明
- 例外：`asset/config.yaml` 见下方「敏感信息」

## 项目

负责的项目在 `projects/`，一个项目一个文件，没有单独的索引文件：每个文件 frontmatter 的 `name` 和 `description` 就是索引。写法（四块内容各放哪、主文件的固定小节、资源表、坑、Design、项目日志）都按 [project-docs](skills/project-docs/SKILL.md) skill，往 `projects/` 里写之前先加载它。

- **找项目用 [bin/projects.py](bin/README.md)**：它读每个项目文件 frontmatter 的 `name` 和 `description`，列出有哪些项目、各是什么；不确定手头的事属于哪个项目时先跑它（可带关键词），不用逐个打开项目文件。
- **做项目前先看**：动某个项目（改代码、部署、重启、排查、查数据）之前，先读它的项目文件，按里面写的部署方式和注意事项来（主文件有「按需读」表的，再读跟手头的事相关的子文件，不用全读）；再跑 `bin/unfinished_tasks.py -p <项目文件名>` 看它还有哪些没做完的任务。
- **做完按实际情况补充修改**：实际情况和文件里写的不一样（地址、目录、端口、启动参数、部署步骤变了），或者踩了文件里没写的坑，干完活就把文件改对、补上，写明核实日期。不用事先问，但要在回复里告诉用户改了哪个文件、改了什么。
- **分三处记**：动手要照做的写主文件（位置、用到的资源、去哪查、红线、坑，节名固定）；系统是什么样、计划和进度写 Design；什么时候发生了什么（决定、里程碑、上线、排查结论）追加到项目日志 `projects/<项目>/log.md`，日志可以链到任务。还没按固定小节整理的主文件，动到哪个整理哪个。
- **只记入口和去哪查**：会随代码变的值不抄进项目文件，写成去哪查。
- **新建要先问**：新建项目文件、在 `projects/<项目>/` 下新建资料文件前先问用户（项目日志 `log.md`、主文件超线拆出的 `pitfalls.md` 和脚本自动维护的除外）。

## 任务

只有会改文件、或者要做多步的任务，才在当天的 `task/YYYY-MM-DD.md` 里记；纯问答不用记。日志格式、状态写法、详情文档都按 [daily-log](skills/daily-log/SKILL.md) skill，往 `task/` 里写之前先加载它。几条红线：

- **先干活，不用事先问**。干完在回复末尾提醒用户要不要记成任务，**用户说加才加**。
- **开工改进行中，要人看就改 Review**：开始处理一条任务先把它改成 `[/]` 进行中；需要我决策、或者已经做完，就自动改成 `[?]` Review，写明等我看什么。
- **改成 `[x]` 必须用户同意**：做完先问能不能标记完成，同意前停在 Review。其他状态可以自己改，改了告诉用户。
- **未完成任务用 [bin/unfinished_tasks.py](bin/README.md) 查**，不手动翻日志或 grep。
- **新建 `task/details/` 文档前先问用户**（任务下的子行超过 10 行直接转的、后台自动化建的除外）。项目型和非项目任务都可以建。
- **项目型任务弱化任务这边**：链到项目的任务，每日日志里只留一行条目（状态、主题、项目、工单号），下面可以挂做任务时要用的资料链接；进展、经过、结论、事件都记到项目那边，不在每日日志里重复记；这条任务自己的过程要留长文档时可以建 `task/details/`。「今天干了什么」用 [bin/day_summary.py](bin/README.md) 把两边合起来看。
- **事件自动记，不用问**：我做了改变状态的操作就记一行，纯查询不记。项目本身的变化（部署、发版、重启、改配置、项目上定下来的事）记到项目日志 `projects/<项目>/log.md`；其余的（改工单、发消息、改本仓库的规则和 skill、存取凭据）记到每日日志的 `## 事件`（`- HH:MM 做了什么`）。写法见 daily-log。

## 临时文件

临时文件、临时脚本、导出的数据都放 `task/temp/`（已 gitignore），不放 `/tmp` 或仓库别的目录，也不直接放在 `task/temp/` 根下，按归属分目录：

| 归属 | 目录 |
| --- | --- |
| 某个 skill 跑出来的 | `task/temp/<skill 名>/` |
| 某个项目的 | `task/temp/<项目文件名>/` |
| 某条任务的 | `task/temp/<任务编号>/`（如 `task/temp/T-12/`） |
| 拿不准归哪类的 | 先问用户放哪 |

## 记忆

跨会话要记住的东西优先写进仓库。Claude Code 自带的 auto-memory 在仓库外面，没有版本、别的 agent 读不到，只当缓冲区用。

- **先找归宿**：我纠正的做法、确认过的约定、踩到的工具坑，按内容写到该去的地方：项目相关 → 项目文件；某个 skill 的做法 → 那个 skill；我的偏好、对外口径、开发机 → [PROFILE.md](PROFILE.md)；服务地址、去哪取 key → `asset/` 里的服务清单（文件名见 PROFILE「资产」）；本仓库的规则 → 本文件。规则（本文件、skill）直接改成现在的写法，不写谁哪天定的、以前是什么样、出过什么事，这些在每日日志的事件和 git 历史里；项目文件里的事实照旧标核实日期。
- **不用事先问，改了要说**：直接改，在回复里说明改了哪个文件、改了什么。
- **没有归宿才进 auto-memory**；之后有了归宿就迁进仓库，并删掉那条记忆。不在仓库里自建 `MEMORY.md`。

## 链接（Obsidian 图谱）

本仓库是 Obsidian vault，文件之间靠链接连成图谱：

- 提到仓库里的项目、skill、文档时，写成**相对路径的 Markdown 链接**（如 `[Demo](../projects/demo.md)`），不写成行内代码路径，也不用 `[[双链]]`；同一段里同一个目标链一次就够。例外：frontmatter 属性里只能写 `"[[文件名]]"`。
- **任务指向项目，项目不链回任务**，只有项目日志 `projects/<项目>/log.md` 可以链到任务。从任务里得出的、长期有效的结论写进项目文件（主文件、Design 或项目日志）。
- 移动或重命名文件后，用 `grep` 查一遍旧路径，把链接改过来。

## 敏感信息

- **资产清单**：`asset/` 放工作上用到的资产和参考资料（服务清单、账号名、组织架构等，各是哪个文件见 PROFILE「资产」）。除 `config.yaml` 以外的文件可以直接读，修改前要得到用户确认（脚本生成的文件重新跑脚本即可）。这些文件**不写密码**；涉及凭据的地方写成 `→ config.yaml: <键>`。
- **凭据文件**：`asset/config.yaml` 汇总了所有密码、token 和 API key，已 gitignore，权限 600。除非用户明确要求，否则禁止查看、输出或提交；也不要把里面的值复制到其它文件或命令行。结构模板见 `asset/config.example.yaml`。
- 搜索（grep、glob 等）时要排除 `asset/config.yaml`。
- 新增或修改外部服务时：地址写进服务清单，密码写进 `asset/config.yaml`。如果某个 skill 的 `config.json` 里也有这份凭据，两边都要改。
- **项目文件里的资源和凭据都指向 `asset/`**：资源链到服务清单里对应的小节，地址等信息项目里可以再写一份；凭据只能写存在哪（`→ config.yaml: <键>`、主机上的文件路径和变量名），不能写值。写法见 [project-docs](skills/project-docs/SKILL.md) 的「资源表」。

## 技能（skills/）

`skills/` 是本仓库 skill 的唯一来源，装成本仓库的项目 skill（`.claude/skills/`）后按名字和触发词调用。规则只在 [skills/sync-skill.md](skills/sync-skill.md) 里写，动 skill 前先读。最要紧的三条：

- 新增或修改 skill 只改 `skills/` 里的源文件，不改 `.claude/skills/` 里的入口；增删改名、改了 `name` / `description` 后跑 [bin/sync_skills.py](bin/README.md) 同步，并在回复里列出改了哪些。
- 目录名必须等于 `SKILL.md` 的 `name`。
- **凭据**：在各 skill 目录的 `config.json`（已 gitignore），`asset/config.yaml` 里也汇总了一份。不要读取、输出或提交这些文件。

## 检查

改完文档提交前跑 [bin/lint_vault.py](bin/README.md)，它查 frontmatter、链接、索引和日志格式；pre-commit 钩子也会跑（`git config core.hooksPath .githooks`）。规则写在本文件、[project-docs](skills/project-docs/SKILL.md) 和 [daily-log](skills/daily-log/SKILL.md) 里，lint 是它们的机器版，改规则时一起改。

## Git

- Claude 可以自己 commit 和 push
- 提交人（名字和邮箱）用 PROFILE「Git」里写的
