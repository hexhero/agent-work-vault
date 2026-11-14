# bin

工具脚本，都在仓库根目录下运行，只依赖 Python 3 标准库。

## setup.py

新克隆后跑一次：选语言（把 `i18n/<语言>/` 下的文档换到原位）、写 `vault.config.json`、启用 pre-commit 钩子、同步 skill 入口；`--examples` 把 `examples/<语言>/` 里的示例项目和每日日志装进来（已有的文件不覆盖）。

```bash
bin/setup.py --lang zh-CN --timezone Asia/Shanghai   # 中文文档，时区北京时间
bin/setup.py --lang en --examples                   # 英文文档，装上示例
```

## vault.py 和 vault.config.json

各脚本共用的约定，不单独运行：

- 每日日志的三个标题、项目主文件的固定小节、任务下的「项目：」行、「→ [详情]」链接，中文、英文两套写法都认（英文是 `## Tasks` / `## Log` / `## Events`、`Project:`、`→ [Details]`，项目小节见 `vault.py` 里的 `PROJECT_SECTIONS`）。一个文件里用同一套。
- 仓库根目录的 `vault.config.json` 配两项：`language`（`zh-CN` 或 `en`，`sync_skills.py` 生成的 skill 入口用哪种语言，默认 `zh-CN`）、`timezone`（IANA 时区名，`day_summary.py` 的「今天」和看板用它；环境变量 `VAULT_TZ` 优先，都没配就用本机时区）。

## unfinished_tasks.py

从 `task/YYYY-MM-DD.md` 每日任务日志里捞出未完成的任务，按日期分组列出，并标上状态和所在行号。

状态写在复选框里：`[ ]` 未开始、`[/]` 进行中、`[?]` Review（AI 做完或要人决定，等用户看）、`[!]` Block、`[x]` 已完成、`[-]` 已取消。除已完成和已取消以外都算未完成；Task Board 插件里的其他字符（如 `<`）归为「其他」，也算未完成。

- 只扫描文件名为 `YYYY-MM-DD.md` 的日志，不看 `task/details/` 和 `task/temp/`。
- 条目开头的 `HH:MM` 会被识别为开始时间；没写时间的条目也能列出。
- 嵌在子列表里的未完成子任务也会列出，前面标 `└`。

```bash
bin/unfinished_tasks.py                    # 列出所有未完成任务
bin/unfinished_tasks.py -d                 # 连同任务下面的补充说明一起列出
bin/unfinished_tasks.py -s blocked         # 只看 Block 的（可重复：-s todo -s doing）
bin/unfinished_tasks.py --since 2026-10-01 --until 2026-10-07   # 限定日志日期范围
bin/unfinished_tasks.py --json             # JSON 输出，方便其他脚本调用
bin/unfinished_tasks.py --ref PROJ-123     # 按工单号（ClickUp 风格的 PROJ-123 或 ClickUp 链接）反查条目（含已完成、已取消），可重复
bin/unfinished_tasks.py -p demo           # 只看链到某个项目文件的未完成任务（主题或「项目：」行里的链接），可重复
bin/unfinished_tasks.py --id T-8           # 按内部编号查条目（含已完成、已取消），可重复
bin/unfinished_tasks.py --next-id          # 下一个可用的内部编号（所有日志里最大的号加一）
bin/unfinished_tasks.py --reporter AliceChen   # 只看某个报告人派的未完成任务（任务行末尾的 #reporter/AliceChen），不分大小写，可重复
bin/unfinished_tasks.py --type message     # 只看某个类型（#type/message）的未完成任务，可重复
bin/unfinished_tasks.py -a --type message --reporter BobLi   # -a 连已完成、已取消的一起列（和其他筛选条件一起用）
```

输出示例：

```
== 2026-10-05  (task/2026-10-05.md)
  [/] 进行中  09:00 主题A → [详情](details/a.md)  :1
  [!] Block  12:00 主题B  :3
    └ [ ] 未开始  子任务  :6

共 3 条未完成（进行中 1，Block 1，未开始 1）
```

JSON 每项字段：`date`、`line`、`mark`（复选框字符）、`status`（`todo` / `doing` / `blocked` / `other`）、`status_label`（中文名）、`start`（开始时间，可能为 null）、`id`（内部编号 `T-N`，没有为 null；`title` 里不含它）、`title`、`reporter`（报告人，任务行上 `#reporter/` 后面的写法如 `AliceChen`，没有为 null；`title` 里不含这个标签）、`nested`（是否为子任务）、`detail`（补充说明行）、`refs`（标题和补充说明里提到的工单号，ClickUp 风格的自定义 ID 如 `PROJ-123` 或 ClickUp 链接里的原始 ID，标题里的排前面）。

## sync_skills.py

把 `skills/` 下的 skill 安装 / 同步成本仓库的项目 skill（`.claude/skills/`），规则见 [skills/sync-skill.md](../skills/sync-skill.md)。

- 以 `skills/` 为准：补装新增的、删除源里已没有的、覆盖内容不一致的入口；入口的 `name`、`description` 逐字照抄源文件，正文固定指回源文件。
- 目录名和 `name` 不一致、缺 frontmatter 的 skill 报错并跳过，不自动改名。
- 只删除本脚本生成的入口（正文带固定标记的）；`.claude/skills/` 里手工放的其他目录、入口目录里的多余文件只报警告，不动。

```bash
bin/sync_skills.py            # 安装 / 同步，并列出补装、更新、删除了哪些
bin/sync_skills.py --check    # 只检查不改，有差异或错误时退出码为 1
```

输出示例：

```
已补装  weekly-report
已更新  daily-log
已删除  old-one
共 7 个 skill：一致 5，补装 1，更新 1，删除 1，错误 0
```


## projects.py

列出 `projects/` 下的项目：读每个项目文件 frontmatter 里的 `name` 和 `description`，和读 skill 的方式一样。不用读正文就能知道有哪些项目、各是什么，再决定去读哪个项目文件。

```bash
bin/projects.py                 # 每个项目一行：name — description
bin/projects.py -v              # 加上别名、仓库、主机、文件路径、同名目录里的文件
bin/projects.py demo api        # 按关键词筛选（匹配 name、别名、description，满足任一个）
bin/projects.py --json          # JSON 输出
```

## day_summary.py

汇总某一天干了什么：各项目日志（`projects/<项目>/log.md`）当天的条目，加上每日日志里的任务、日志和非项目事件。项目相关的事只记在项目日志里，所以「今天干了什么」要用它把两边合起来看。

```bash
bin/day_summary.py                # 今天（时区见下面 vault.py）
bin/day_summary.py 2026-11-11     # 指定日期
bin/day_summary.py -p demo        # 只看某个项目
```

## board.py

任务看板：把 `projects/`、`task/` 和 `skills/` 渲染成一张实时刷新的关系图，只读，不改任何文件。页面在 `bin/board.html`。

- 上面是关系图：项目是文件卡，未完成的任务挂在所属项目旁边，skill 是中间大圆里的标签，已完成 / 已取消的任务是项目周围的小点。连线是任务 → 项目、任务 → skill（任务标题或补充说明里提到 skill 名）、skill → 项目（SKILL.md 里链到的项目）、项目 → 核心。
- 进行中、Review、Block 的任务是带状态色的卡片，它们到项目、skill、核心的连线和端点用状态色标出来，线上有光点在跑；其余元素是背景。
- 中间的核心圆是 Claude：中心是图标和字样，下面是近 5 小时和本周的订阅余量百分比、今天的 token、在跑的会话数。圆里两圈扇形表示余量（内圈近 5 小时，外圈本周，从 12 点方向顺时针，扇形越大剩得越多，低于 20% 变红）；圆环外圈是近 24 小时每小时输出 token 的柱状图；点核心打开明细（余量和重置时间、token 构成、近 7 天、各模型）。
- 余量的来源：`board.py` 每 15 分钟用 haiku 发一条最短的无头请求（`claude -p`，不存会话、不带工具和 MCP），从返回的限额信息里取已用比例和重置时间，每次约一万 haiku token；`--quota-interval 0` 关掉，关掉后核心只显示 token。token 数来自本机 `~/.claude/projects` 的会话记录，只读数字和模型名，不读对话内容，每 5 秒增量扫一次。不含费用。
- 图上方一排按钮（全部 / 进行中 / Review / Block / 未开始 / 项目 / Skill / 已完成，键盘 `0`～`7`）：点一个，把那一类调到前景，卡片放大排到核心周围并显示完整内容（「卡在」「待确认」、项目、报告人），相关的项目和 skill 提亮，其余变暗；再点一次或按 Esc 还原。
- 有新任务进来、或任务状态变了，自动把这些任务调到前景 20 秒（效果同上），顶部弹出变化清单（旧状态 → 新状态）；点任意处或按 Esc 提前还原。一次变化超过 8 条（比如批量改日志）不触发。
- 点任务看内容：报告人、补充说明、`task/details/` 详情文档、项目日志里提到同一个 ClickUp 编号的条目。点项目看介绍、未完成任务、相关 skill、项目日志（默认最近 3 天）、已完成任务。点 skill 看描述、链到的项目、提到它的任务。鼠标悬停在节点或下面列表的行上，会提亮它的连线和相邻节点。
- 下面四个面板：未完成任务列表、各项目任务量（未完成 / 全部）、跟进、事件流（每日日志「## 事件」里的条目，最新的在上面，最多 300 条；事件里的任务编号可点；新事件进来时对应的任务节点起一圈波纹）。
- 图底部的「收起面板」（键盘 `F`）把下面三个面板折叠起来，关系图占满整个窗口；再点展开，状态记在浏览器里。
- 默认青绿配色，右上角四个圆点切换（青绿 / 橙 / 冰蓝 / 青柠），记在浏览器里。系统开了「减少动态效果」时节点不漂浮、不跑光点。
- 数据复用 `projects.py` 和 `unfinished_tasks.py` 的解析，skill 读各 `SKILL.md` 的 frontmatter；每秒检查一次文件变化，变了经 SSE 推给页面。
- 默认只监听本机；`/api/doc` 只放行 `task/details/` 下的文档。
- 适配手机（节点缩成小卡，前景排成列表）；页面里的接口都是相对路径，可以挂在反向代理的子路径下。事件流被代理缓冲时页面自动退回每 5 秒轮询。

```bash
bin/board.py                    # http://127.0.0.1:8765
bin/board.py --port 9000
bin/board.py --host 0.0.0.0     # 让同网段的其他机器也能打开
```

## lint_vault.py

按 [CLAUDE.md](../CLAUDE.md)、[project-docs](../skills/project-docs/SKILL.md) 和 [daily-log](../skills/daily-log/SKILL.md) 的约定检查整个仓库的文档，是那些文字规则的机器版，规则改了两边一起改。不看 `task/temp/`、`.obsidian/`、`.claude/`、`examples/`、`i18n/`、`oss/`。

| 检查 | 内容 |
|---|---|
| frontmatter | 各目录文档的 `type` 和必填字段（项目 `name` / `description` / `aliases` / `repo` / `hosts`，`name` 等于文件名，详情 `project` / `log`，项目资料 `project`） |
| links | 相对路径链接和 frontmatter 里的 `[[双链]]` 能找到目标 |
| no-task-link | `projects/` 下的文件不链到 `task/`（项目日志 `log.md` 除外） |
| size | 项目主文件超过 16KB、Design（`design*.md`）和 `pitfalls.md` 超过 32KB、项目日志 `log.md` 超过 64KB 给警告 |
| sections | 已整理的项目主文件（有 `## 位置` 或 `## Location`）的二级标题只能是固定小节（位置、资源、按需读、去哪查、怎么做、红线、坑、相关，或对应的英文），按这个顺序；有同名目录的要有「按需读」；没整理的汇总警告一条 |
| project-log | 项目日志 `log.md`、`log-YYYYqN.md` 的二级标题只能是 `## YYYY-MM-DD`，按日期倒序 |
| index | docs 各 README 的索引列全了文件（`projects/` 没有索引文件，用 `bin/projects.py`） |
| filename | `projects/`、`task/details/` 的文件名 |
| daily-log | 每日日志：标题顺序（任务、日志、事件）、任务在「## 任务」下、日志和事件段没有复选框、事件每条一行「- HH:MM 做了什么」；任务下的子行超过 10 行给警告 |
| task-id | 未完成的顶层任务要有内部编号 `T-N`；编号在所有日志里不能重复；报告人标签只写在顶层任务行上，格式 `#reporter/AliceChen` |
| skills | 调 `sync_skills.py --check` |

```bash
bin/lint_vault.py       # 有错误时退出码为 1，警告不影响
bin/lint_vault.py -q    # 只输出错误
```

仓库自带 pre-commit 钩子（`.githooks/pre-commit`），有错误时拒绝提交。新克隆后启用一次：`git config core.hooksPath .githooks`。

