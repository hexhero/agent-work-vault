# 工作档案

> 模板：把占位内容换成你自己的。CLAUDE.md 会在每次会话自动加载本文件，写短一点。

## 公司

**Example Corp**，一句话说公司是做什么的。团队在哪里办公。

## 我

- 姓名：你的名字
- 邮箱：you@example.com
- 职位：
- 部门：
- 汇报线：直属上级 → 上级的上级

## 偏好

- **时区**：如 Asia/Shanghai。我说的「今天」「昨天」「下午 6 点」都按这个时区算，回复里的时间、每日日志的日期和时间也用它。机器时钟是别的时区时，取时间用 `TZ=Asia/Shanghai date`；脚本的时区在 `vault.config.json` 里配。
- **语言**：和我对话用什么语言，什么时候产出物（文档、消息草稿）用别的语言。
- 对外怎么称呼产品、哪些东西不能发出去，这类规矩。

## 资产

- 服务清单：[asset/services.md](asset/services.md)（服务器、数据库、内部服务的地址，去哪取 key）
- 组织架构：可选，如 `asset/org-chart.md`；任务的 `#reporter/` 名字按这里写
- 凭据：`asset/config.yaml`（已 gitignore），模板 `asset/config.example.yaml`

## Git

- 本仓库的提交人：`claude`，邮箱 `claude@example.com`（用 `git config user.name` / `user.email` 设好）

## 开发机

- 主机、代码仓库克隆到哪、值得知道的工具怪癖。

## 技术栈

- 常用的语言、数据库、框架。
