#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# core/loader.py
from typing import Type, Dict, Optional
from pydantic_settings import BaseSettings
import os
import importlib
from pathlib import Path
from .settings import GlobalSetting
# from core.log import logger
# ------------------------------
# 核心配置：环境标识与配置类的映射
# ------------------------------
# 支持的环境（可根据需求扩展，如增加 staging 预发布环境）
SUPPORTED_ENVS = ["dev", "test", "prod"]
# 默认环境（本地开发用）
DEFAULT_ENV = "dev"
# 环境与配置类的映射规则：
# 环境标识 → (配置模块路径, 配置类名)
# （默认从 core.settings 导入，可根据项目结构调整）
ENV_CONFIG_MAP: Dict[str, Type[GlobalSetting]] = {
    # "dev": DevSetting,  # 开发环境配置类
    # "test": TestingSetting,  # 测试环境配置类
    # "prod": ProductionSetting,  # 生产环境配置类
}
# ------------------------------
# 工具函数：获取当前环境标识
# ------------------------------
def get_current_env() -> str:
    """
    从系统环境变量获取当前环境标识，优先顺序：
    1. 系统环境变量 ENVIR / APP_ENV（优先级最高）
    2. 默认环境 DEFAULT_ENV（优先级最低）
    若获取的环境不在 SUPPORTED_ENVS 中，返回默认环境
    """
    # 从系统环境变量读取（支持 ENV 或 APP_ENV 两种键名）
    current_env = os.getenv("ENVIR") or os.getenv("APP_ENV")
    # 校验环境合法性，非法环境返回默认值
    if current_env and current_env.strip() in SUPPORTED_ENVS:
        print(f"当前环境：{current_env.strip()}")
        return current_env.strip()
    global DEFAULT_ENV
    print(
        f"警告：未设置合法环境变量（支持 {SUPPORTED_ENVS}），使用默认环境 {DEFAULT_ENV}"
    )
    return DEFAULT_ENV
# ------------------------------
# 工具函数：动态导入配置类
# ------------------------------
def import_config_class(env: str) -> Type[BaseSettings]:
    """
    根据环境标识动态导入对应的配置类：
    1. 从 ENV_CONFIG_MAP 获取配置模块和类名
    2. 动态导入模块并返回配置类
    若导入失败，抛出异常
    """
    try:
        # 获取配置模块路径和类名
        module_path, class_name = ENV_CONFIG_MAP[env]
        # 动态导入配置模块（如 import core.settings）
        config_module = importlib.import_module(module_path)
        # 从模块中获取配置类（如 DevSettings）
        config_class = getattr(config_module, class_name)
        # 校验配置类是否继承自 BaseSettings
        if not issubclass(config_class, BaseSettings):
            raise TypeError(
                f"配置类 {class_name} 必须继承自 pydantic_settings.BaseSettings"
            )
        return config_class
    except KeyError:
        raise ValueError(f"环境 {env} 未在 ENV_CONFIG_MAP 中配置，请检查映射关系")
    except ImportError:
        raise ImportError(f"配置模块 {module_path} 导入失败，请检查模块路径是否正确")
    except AttributeError:
        raise AttributeError(
            f"配置模块 {module_path} 中未找到类 {class_name}，请检查类名是否正确"
        )
# ------------------------------
# 工具函数：获取环境对应的 .env 文件路径
# ------------------------------
def get_env_file_path(env: str) -> Optional[Path]:
    """
    根据环境标识返回对应的 .env 文件路径：
    - 优先查找项目根目录下的 .env.{env}（如 .env.dev）
    - 若文件不存在，返回 None（配置类将仅从系统环境变量加载）
    """
    # 项目根目录（loader.py 所在目录的父目录，可根据实际结构调整）
    project_root = Path(__file__).parent.parent
    # .env 文件路径（如 project_root/.env.dev）
    env_file = project_root / f".env.{env}"
    # 检查文件是否存在且可读
    if env_file.exists() and env_file.is_file():
        print(f"加载环境变量文件：{env_file}")
        return env_file
    print(f"警告：环境 {env} 的配置文件 {env_file} 不存在，仅从系统环境变量加载配置")
    return None
# ------------------------------
# 核心函数：加载并实例化配置
# ------------------------------
def load_config() -> BaseSettings:
    """
    加载多环境配置的核心入口：
    1. 获取当前环境标识
    2. 动态导入对应的配置类
    3. 配置 .env 文件路径（若存在）
    4. 实例化配置类并返回（自动加载环境变量）
    """
    # 步骤1：获取当前环境
    current_env = get_current_env()
    # 步骤2：动态导入配置类
    # config_class = import_config_class(current_env)
    # 步骤3：获取 .env 文件路径
    # env_file = get_env_file_path(current_env)
    # 步骤4：实例化配置类（根据是否有 .env 文件调整参数）
    # if current_env:
    # 若有 .env 文件，传递 env_file 参数（适配 pydantic-settings v2+）
    # return GlobalSetting(_env_file=env_file, _env_file_encoding="utf-8")
    # else:
    # 若无 .env 文件，直接实例化（仅从系统环境变量加载）
    # 先加载公共 .env，再用环境专属 .env.{env} 覆盖（后者优先级更高）
    # pydantic-settings 对元组内的文件按顺序读取，靠后的文件覆盖靠前的
    return GlobalSetting(
        _env_file=(".env", f".env.{current_env}"),
        _env_file_encoding="utf-8",
    )
# ------------------------------
# 单例配置对象：全局唯一，项目中直接导入使用
# ------------------------------
# 加载配置（应用启动时执行一次）
settings: GlobalSetting = load_config()
# print(settings.model_dump())
# 打印加载结果（便于调试，生产环境可注释）
print(
    f"[OK] 配置加载完成 | 当前环境: {settings.ENVIR} | 服务名称: {settings.SERVICE.NAME}"
)