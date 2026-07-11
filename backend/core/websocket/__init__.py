#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WebSocket 通信层模块
提供可插拔的实时通信连接管理抽象
"""

from typing import Optional

from .manager import ConnectionManager
from .connection import FastAPIConnectionManager

__all__ = ["ConnectionManager", "FastAPIConnectionManager", "get_connection_manager", "set_connection_manager"]

_connection_manager: Optional[ConnectionManager] = None


def set_connection_manager(manager: ConnectionManager) -> None:
    """设置全局连接管理器实例，通常在应用启动时调用"""
    global _connection_manager
    _connection_manager = manager


def get_connection_manager() -> Optional[ConnectionManager]:
    """获取全局连接管理器实例"""
    return _connection_manager
