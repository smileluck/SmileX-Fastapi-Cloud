#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建默认超级管理用户脚本
用于在数据库初始化后创建默认的超级管理员账号
"""
from datetime import datetime, timezone
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
import sys
import os

# 添加当前目录到 Python 搜索路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models.base import Base
from database.models.sys.user import SysUser
from core.config import settings
from core.security.password import PasswordHasher


def create_superuser():
    """
    创建默认超级管理用户
    """
    # 创建同步引擎
    # 直接使用固定的数据库 URL，避免编码问题
    sync_url = "postgresql+psycopg2://postgres:123456@localhost:5432/smilex_cloud"
    engine = create_engine(
        sync_url,
        echo=False,
    )

    # 创建会话工厂
    Session = sessionmaker(bind=engine)

    with Session() as session:
        try:
            # 检查是否已存在超级管理员
            stmt = select(SysUser).where(SysUser.is_superuser == True)
            result = session.execute(stmt)
            existing_superuser = result.scalar_one_or_none()

            if existing_superuser:
                print("超级管理员已存在，跳过创建")
                return

            # 生成密码哈希（bcrypt）
            password = "admin123"  # 默认密码
            password_hash = PasswordHasher.hash(password)

            # 创建超级管理员用户
            superuser = SysUser(
                username="admin",
                password=password_hash,
                nickname="超级管理员",
                email="admin@example.com",
                phone="13800138000",
                avatar="",
                last_login_at=datetime.now(timezone.utc),
                last_login_ip="127.0.0.1",
                roles=[],
                status=True,
                is_superuser=True
            )

            # 添加到会话
            session.add(superuser)
            session.commit()
            session.refresh(superuser)

            print(f"超级管理员创建成功！")
            print(f"用户名: {superuser.username}")
            print(f"密码: {password}")
            print(f"用户ID: {superuser.id}")

        except Exception as e:
            print(f"创建超级管理员失败: {str(e)}")
            session.rollback()
        finally:
            engine.dispose()


if __name__ == "__main__":
    create_superuser()
