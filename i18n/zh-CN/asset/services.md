# 服务清单

工作上用到的服务器、数据库、服务的地址，以及凭据放在哪。**这里不写密码**，写成 `→ config.yaml: <键>`。项目文件链到下面对应的小节。

## 服务器

| 名称 | 地址 | 上面跑着什么 | 登录 |
| --- | --- | --- | --- |
| app01 | 192.0.2.10 | Demo API（见示例项目 demo） | `deploy` 用户，→ config.yaml: `ssh.app01` |

## 数据库

| 名称 | 地址 | 说明 |
| --- | --- | --- |
| example_db | 192.0.2.20:5432 | 只读从库，→ config.yaml: `example_db` |

## 外部服务

| 服务 | 地址 | 账号 |
| --- | --- | --- |
| GitHub | https://github.com | → config.yaml: `github.token` |
