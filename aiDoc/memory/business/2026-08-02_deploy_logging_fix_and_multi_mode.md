# deploy.sh 日志链修复 + 多模式部署

## 需求描述

两件事：

1. **日志链修复**：检查并修复生产部署/启动路径（`deploy/deploy.sh`、systemd 服务、`backend/gunicorn.conf.py`），确保日志记录正确生效、按日期目录滚动日志存在。
2. **多模式部署**：`deploy.sh` 支持不同的部署方式，不必每次都跑全量 `deploy`。

## 状态

已完成

## 修复要点（日志链）

1. **`error.log` 写入冲突**：`config/logging_prod.ini` 的应用根 logger `errorFileHandler` 与 `gunicorn.conf.py` 的 `error_file` handler 都写 `LOG_DIR/error.log`（两个独立 `DailyDirFileHandler` 实例同写一文件，滚动竞态 + 格式交错）。将 Gunicorn error 日志改名 `gunicorn-error.log`（`access.log` 无冲突，保留原名）。
2. **`deploy.env LOG_DIR` 不传导到运行态**：运行中应用/Gunicorn 经 `.env.prod` 的 `LOG__DIR`（Pydantic 嵌套字段 `LOG.DIR`，双下划线）读取日志目录，而部署脚本按 `deploy.env LOG_DIR`（单下划线）预置目录/权限/`ReadWritePaths`。改 `LOG_DIR` 后两者漂移，在 `ProtectSystem=strict` 下会静默写失败。`cmd_setup` 现把 `${LOG_DIR}` 同步写入 `.env.prod` 的 `LOG__DIR`。
3. **`.env.prod` 自拷贝死代码**：原 `cp backend/.env.prod backend/.env.prod`（源=目标，且 `.env.prod` 由 git 检出无独立模板）改为明确报错。
4. **`start_prod.sh` 不存在**：生产启动机制是 `deploy.sh setup` 安装的 systemd 服务 `smilex-cloud.service`（gunicorn + `gunicorn.conf.py`），仓库内无 `start_prod.sh`/`nohup`/`start.sh`。

## 多模式部署设计（deploy.sh）

- 新增原子子命令：`pull` / `deps` / `migrate` / `restart` / `reload`，各自只做一步，便于按需组合。
- `deploy` 改为**智能全量**：`git pull` 后用 `git diff before..after` 检测依赖文件（`uv.lock`/`pyproject.toml`/`requirements.txt`）与迁移目录（`alembic`/`alembic.ini`）是否变更，未变则跳过 `uv sync` / `alembic`；`--full` 强制全量。
- 提取共享步骤函数 `do_pull`/`do_deps`/`do_migrate`/`do_restart`/`do_health_check` 与检测函数 `deps_changed`/`migrations_changed`，被 `deploy` 与原子子命令复用，保证行为一致。
- `reload` = `systemctl reload`（gunicorn HUP，零停机刷新应用代码）；`restart` = 硬重启（`gunicorn.conf.py`/环境变量变更需用此）。原子子命令执行后用 `warn` 提示尚未重启/已跳过哪些步骤。
- 检测函数用 `git -C "${BACKEND_DIR}" diff --name-only ... | grep -q .`，路径相对 `BACKEND_DIR`；`set -euo pipefail` 下仅在 `if` 条件中使用（grep 无匹配返回非零不会触发退出）。

## 涉及范围

### 后端

- `backend/gunicorn.conf.py`：error 日志改 `gunicorn-error.log`，补冲突说明注释。
- `deploy/deploy.sh`：新增原子子命令 + 智能 `deploy` + 共享步骤函数；`cmd_setup` 同步 `LOG__DIR`、修 `.env.prod` 死代码。
- `deploy/deploy.env`：`LOG_DIR` 注释补充「由 setup 同步到 `.env.prod LOG__DIR`」。

### 前端

无（本次仅后端部署链；前端 dist 由别处服务，nginx 全量反代到后端）。

## 约束与备注

- 仅后端部署；未引入前端构建/部署子命令（用户明确「仅后端」）。
- 未改 `cmd_rollback`（仍全量 deps+migrate+restart，符合回滚语义）；其 `alembic upgrade head` 是否应改 downgrade 属既有问题，本次不动。
- systemd `ExecStart` 的 CLI 参数（`-w`/`-b`/`--timeout` 等）与 `gunicorn.conf.py` 进程参数冗余（CLI 覆盖配置文件），但因 `logconfig_dict` 必须保留，未做合并。
- 生效需重跑 `sudo ./deploy.sh setup`（或 `systemctl daemon-reload && systemctl restart smilex-cloud`）。

## 相关文件

- `deploy/deploy.sh`
- `deploy/deploy.env`
- `backend/gunicorn.conf.py`
- `backend/config/logging_prod.ini`（未改，仅作为冲突对照）
- `deploy/smilex-cloud.service`（未改）

## 记录日期

2026-08-02
