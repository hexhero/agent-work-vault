---
type: project
name: demo
description: "Demo API：给财务导出发票（JSON、CSV）的内部 HTTP 服务，也叫发票导出服务。容器跑在 app01 上，打 tag 发布。"
aliases:
  - Demo
  - Demo API
  - 发票导出服务
repo:
  - https://github.com/example/demo-api
hosts:
  - 192.0.2.10
---
# Demo API

- **简介**：内部 HTTP 服务（Python + FastAPI），从只读库导出发票，格式有 JSON 和 CSV，财务做月结报表用。
- **当前状态**（2026-01-06）：线上运行，CSV 导出在做，见 [Design](demo/design.md) 的「阶段和进度」。

## 位置

| | 测试 | 生产 |
| --- | --- | --- |
| 主机 | app01（`192.0.2.10`） | app01（`192.0.2.10`） |
| 目录 | `/srv/demo-staging` | `/srv/demo` |
| 容器 | `demo-staging-api-1` | `demo-api-1` |
| 地址 | `https://staging.demo.example.com` | `https://demo.example.com` |
| 发布 | 打 `v*-rc*` tag | 打 `v*` tag |

## 资源

| 类别 | 资源 | 拿来干什么 |
| --- | --- | --- |
| 服务器 | app01，见[服务清单](../asset/services.md#服务器) | 两个环境都在上面 |
| 数据库和存储 | example_db，见[服务清单](../asset/services.md#数据库) | 发票数据来源（只读） |
| 外部服务 | GitHub Actions | 打 tag 时构建镜像并部署 |
| 账号和凭据 | 数据库用户 `readonly` → config.yaml: `example_db`；部署用户 → config.yaml: `ssh.app01` | |
| 下游 | 财务的月结表格 | 读 `/export/invoices.csv`；改列之前先问 Alice Chen |

## 按需读

| 文件 | 什么时候读 |
| --- | --- |
| [design.md](demo/design.md) | 改接口或导出格式之前；阶段和进度 |
| [log.md](demo/log.md) | 想知道哪天定了什么、上了什么 |

## 去哪查

- 线上版本：`curl https://demo.example.com/version`
- 配置：仓库里的 `.env.example`；真正的 `.env` 在 app01 的 `/srv/demo` 下

## 怎么做

- **发布**：合到 `main`，打 `vX.Y.Z-rc1` tag，测试环境验过后再打 `vX.Y.Z`。
- **回滚**：把上一版的 tag 再推一次。

## 红线

- 改 CSV 的列顺序前先问：财务表格是按位置读列的。

## 坑

- 库里的时间是 UTC，只在导出时转成客户的时区（2026-01-05 核实）。

## 相关

- [daily-log](../skills/daily-log/SKILL.md)、[project-docs](../skills/project-docs/SKILL.md)
