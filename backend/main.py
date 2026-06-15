#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目入口文件
初始化FastAPI应用并注册各个模块
"""
from contextlib import asynccontextmanager
from typing import Union
import asyncio
from fastapi import FastAPI
from core.config import settings  # 导入配置
from logging import getLogger
from database.db_manager import init_pool, close_pool
from database.manager.async_manager import get_session
from core.redis import RedisPool

from modules.app.router import router as app_app_router
from modules.admin.router import router as admin_app_router
from modules.robot.router import router as robot_router
from modules.scene.router import router as scene_router
from modules.task.router import router as task_router
from core.registry.setup_registry import setup_app
from core.websocket import FastAPIConnectionManager

logger = getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    # 初始化数据库连接池
    logger.info("初始化数据库连接池")
    await init_pool()
    logger.info("数据库连接池初始化完成")
    # 初始化 Redis 连接池
    logger.info("初始化 Redis 连接池")
    await RedisPool.init_pool()
    logger.info("Redis 连接池初始化完成")
    # 初始化 WebSocket 连接管理器
    logger.info("初始化 WebSocket 连接管理器")
    app.state.connection_manager = FastAPIConnectionManager()
    logger.info("WebSocket 连接管理器初始化完成")
    # 预热 IP 黑名单到 Redis
    try:
        from modules.admin.services.sys.rate_limit_service import RateLimitService
        count = await RateLimitService.warmup_blacklist()
        logger.info("IP 黑名单预热数量: %s", count)
    except Exception as exc:
        logger.error("IP 黑名单预热异常: %s", exc)
    try:
        from modules.robot.services.robot_schema_service import RobotSchemaService
        async for db_schema in get_session():
            await RobotSchemaService.ensure_robot_map_binding(db_schema)
        logger.info("机器人场景绑定字段检查完成")
    except Exception as exc:
        logger.error("机器人场景绑定字段检查异常: %s", exc)
    # 启动定时任务调度器
    try:
        from modules.scheduler.core.scheduler import SchedulerManager
        import modules.scheduler.tasks.builtin  # noqa: F401
        import modules.scheduler.tasks.rate_limit_config  # noqa: F401

        manager = SchedulerManager.get_instance()
        manager.start()
        app.state.scheduler_manager = manager
        async for db_sync in get_session():
            await manager.sync_jobs_from_db(db_sync)
        logger.info("定时任务同步完成")
    except Exception as exc:
        logger.error("定时任务同步异常: %s", exc)
    # 种子数据：菜单 + 同步装饰器注册的任务
    try:
        from modules.scheduler.seed import seed_scheduler
        async for db_seed in get_session():
            await seed_scheduler(db_seed)
    except Exception as exc:
        logger.error("定时任务种子数据异常: %s", exc)
    yield
    # 停止定时任务调度器
    try:
        from modules.scheduler.core.scheduler import SchedulerManager
        SchedulerManager.get_instance().stop()
    except Exception as exc:
        logger.error("定时任务调度器停止异常: %s", exc)
    # 关闭 Redis 连接池
    logger.info("关闭 Redis 连接池")
    await RedisPool.close_pool()
    logger.info("Redis 连接池已关闭")
    # 关闭数据库连接池
    logger.info("关闭数据库连接池")
    await close_pool()
    logger.info("数据库连接池已关闭")


app = FastAPI(
    title=settings.SERVICE.NAME,
    description="这是一个使用FastAPI构建的示例API",
    version="1.0.0",
    contact={
        "name": "SpatialtemporalAI",
        "url": "https://github.com/orgs/SpatialtemporalAI/dashboard",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url=None if settings.ENVIR == "prod" and not settings.SERVICE.OPENAPI_ENABLE_IN_PROD else "/docs",
    redoc_url=None if settings.ENVIR == "prod" and not settings.SERVICE.OPENAPI_ENABLE_IN_PROD else "/redoc",
    openapi_url=None if settings.ENVIR == "prod" and not settings.SERVICE.OPENAPI_ENABLE_IN_PROD else "/openapi.json",
)
# 配置app
setup_app(app, settings=settings)
logger.info("配置文件初始化完成")

# 挂载子应用
# app.mount("/admin", admin_app)
# app.mount("/app", app_app)
# 挂载认证路由
app.include_router(app_app_router)
app.include_router(admin_app_router)
app.include_router(robot_router)
app.include_router(scene_router)
app.include_router(task_router)


if __name__ == "__main__":
    """
    主函数，用于直接运行应用
    添加Ctrl+C监听，实现优雅退出
    """
    import signal
    import uvicorn

    # 定义信号处理函数
    def signal_handler(signum, frame):
        """
        信号处理函数，用于处理Ctrl+C信号
        """
        logger.info("收到退出信号，正在优雅关闭应用...")
        # 这里不需要手动调用关闭函数，因为lifespan会处理
        # 我们只需要记录日志，让uvicorn正常关闭即可

    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)  # 处理Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # 处理kill命令

    # 运行应用
    logger.info("启动应用...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
