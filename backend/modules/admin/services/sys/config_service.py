#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统配置服务
处理系统配置相关的业务逻辑
"""
import logging
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, and_, update, Select
from typing import List, Optional, Tuple, Any

from database.models.sys.config import SysConfig, ConfigType, ConfigGroup
from core.security.rate_limit_config import RateLimitConfigProvider
from core.exception.errors import (
    NotFoundError,
    ConflictError,
    ForbiddenError,
    ValidationError,
)
from core.i18n import t
from modules.admin.schemas.sys.config import (
    SysConfigCreate,
    SysConfigUpdate,
    SysConfigQueryParams,
    SysConfigBatchUpdate,
    SysConfigReset,
    SysConfigByGroupQuery,
)

# 获取logger
logger = logging.getLogger(__name__)


def _invalidate_rate_limit_cache(key: str) -> None:
    """若 key 属于限流配置，清空 RateLimitConfigProvider 缓存。"""
    if key.startswith("rate_limit."):
        RateLimitConfigProvider.invalidate()


class ConfigService:
    """
    系统配置服务类
    """

    @staticmethod
    def build_config_query(
        query_params: SysConfigQueryParams,
    ) -> Select:
        """
        构建配置查询对象

        Args:
            query_params: 查询参数

        Returns:
            SQLAlchemy查询对象
        """
        # 构建基础查询
        query = select(SysConfig)

        # 构建筛选条件
        conditions = []
        if query_params.key:
            conditions.append(SysConfig.key.contains(query_params.key))
        if query_params.description:
            conditions.append(SysConfig.description.contains(query_params.description))
        if query_params.type:
            conditions.append(SysConfig.type == query_params.type)
        if query_params.group:
            conditions.append(SysConfig.group == query_params.group)

        if query_params.is_system is not None:
            conditions.append(SysConfig.is_system == query_params.is_system)

        if conditions:
            query = query.where(and_(*conditions))

        # 排序
        query = query.order_by(SysConfig.id.desc())

        return query

    @staticmethod
    async def get_config_list(
        db: AsyncSession, query_params: SysConfigQueryParams
    ) -> Tuple[List[SysConfig], int]:
        """
        获取配置列表（分页）

        Args:
            db: 数据库会话
            query_params: 查询参数

        Returns:
            (配置列表, 总数)
        """
        try:
            logger.info(
                "获取配置列表，查询参数: %s", query_params.model_dump(exclude_none=True)
            )

            # 构建查询
            base_query = ConfigService.build_config_query(query_params)

            # 先查询总数
            count_result = await db.execute(
                select(SysConfig.id).select_from(base_query.subquery())
            )
            total = len(count_result.scalars().all())

            # 分页查询
            query = base_query
            if query_params.page and query_params.page_size:
                offset = (query_params.page - 1) * query_params.page_size
                query = query.offset(offset).limit(query_params.page_size)

            result = await db.execute(query)
            configs = result.scalars().all()

            logger.info("获取配置列表成功，共 %d 条记录", total)
            return configs, total

        except Exception as e:
            logger.error("获取配置列表失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_config_by_id(db: AsyncSession, config_id: int) -> SysConfig:
        """
        通过ID获取单个配置

        Args:
            db: 数据库会话
            config_id: 配置ID

        Returns:
            配置对象

        Raises:
            NotFoundError: 配置不存在
        """
        try:
            logger.info("获取配置详情，配置ID: %d", config_id)

            result = await db.execute(
                select(SysConfig).where(SysConfig.id == config_id)
            )
            config = result.scalar_one_or_none()

            if not config:
                logger.warning("配置不存在，配置ID: %d", config_id)
                raise NotFoundError(msg=t("config.not_found", id=config_id))

            logger.info("获取配置详情成功，配置ID: %d", config_id)
            return config

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取配置详情失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_config_by_key(db: AsyncSession, config_key: str) -> SysConfig:
        """
        通过键名获取单个配置

        Args:
            db: 数据库会话
            config_key: 配置键名

        Returns:
            配置对象

        Raises:
            NotFoundError: 配置不存在
        """
        try:
            logger.info("获取配置详情，配置键名: %s", config_key)

            result = await db.execute(
                select(SysConfig).where(SysConfig.key == config_key)
            )
            config = result.scalar_one_or_none()

            if not config:
                logger.warning("配置不存在，配置键名: %s", config_key)
                raise NotFoundError(msg=t("config.not_found_by_key", key=config_key))

            logger.info("获取配置详情成功，配置键名: %s", config_key)
            return config

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取配置详情失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_configs_by_group(
        db: AsyncSession, query: SysConfigByGroupQuery
    ) -> List[SysConfig]:
        """
        按分组获取配置列表

        Args:
            db: 数据库会话
            query: 查询参数

        Returns:
            配置列表
        """
        try:
            logger.info(
                "按分组获取配置，分组: %s, 仅可编辑: %s",
                query.group,
                query.editable_only,
            )

            stmt = select(SysConfig).where(SysConfig.group == query.group)

            stmt = stmt.order_by(SysConfig.id.desc())
            result = await db.execute(stmt)
            configs = result.scalars().all()

            logger.info("按分组获取配置成功，共 %d 条记录", len(configs))
            return configs

        except Exception as e:
            logger.error("按分组获取配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_config_value(
        db: AsyncSession, config_key: str, default: Any = None
    ) -> Any:
        """
        获取配置值，并根据配置类型进行转换

        Args:
            db: 数据库会话
            config_key: 配置键名
            default: 默认值

        Returns:
            转换后的配置值
        """
        try:
            config = await ConfigService.get_config_by_key(db, config_key)
            return ConfigService._convert_value(config.value, config.type, default)
        except NotFoundError:
            return default
        except Exception as e:
            logger.error(
                "获取配置值失败，配置键名: %s: %s", config_key, str(e), exc_info=True
            )
            return default

    @staticmethod
    def _convert_value(value: str, config_type: ConfigType, default: Any = None) -> Any:
        """
        根据配置类型转换值

        Args:
            value: 字符串值
            config_type: 配置类型
            default: 默认值

        Returns:
            转换后的值
        """
        try:
            if value is None or value == "":
                return default

            if config_type == ConfigType.STRING:
                return value
            elif config_type == ConfigType.NUMBER:
                try:
                    if "." in value:
                        return float(value)
                    return int(value)
                except (ValueError, TypeError):
                    return default
            elif config_type == ConfigType.BOOLEAN:
                return value.lower() in ("true", "1", "yes", "on")
            elif config_type == ConfigType.JSON:
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return default
            elif config_type == ConfigType.ARRAY:
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return parsed
                    return [parsed]
                except (json.JSONDecodeError, TypeError):
                    return default
            return value
        except Exception:
            return default

    @staticmethod
    def _validate_value(value: str, config_type: ConfigType) -> bool:
        """
        验证配置值是否符合指定类型

        Args:
            value: 配置值
            config_type: 配置类型

        Returns:
            是否有效
        """
        try:
            if value is None:
                return False

            if config_type == ConfigType.STRING:
                return True
            elif config_type == ConfigType.NUMBER:
                try:
                    float(value)
                    return True
                except (ValueError, TypeError):
                    return False
            elif config_type == ConfigType.BOOLEAN:
                return value.lower() in (
                    "true",
                    "false",
                    "1",
                    "0",
                    "yes",
                    "no",
                    "on",
                    "off",
                )
            elif config_type == ConfigType.JSON:
                try:
                    json.loads(value)
                    return True
                except (json.JSONDecodeError, TypeError):
                    return False
            elif config_type == ConfigType.ARRAY:
                try:
                    parsed = json.loads(value)
                    return isinstance(parsed, (list, tuple))
                except (json.JSONDecodeError, TypeError):
                    return False
            return True
        except Exception:
            return False

    @staticmethod
    async def create_config(
        db: AsyncSession, config_in: SysConfigCreate, *, is_superuser: bool = False
    ) -> SysConfig:
        """
        创建配置

        Args:
            db: 数据库会话
            config_in: 配置创建请求

        Returns:
            创建后的配置对象

        Raises:
            ConflictError: 配置键已存在
            ValidationError: 配置值无效
        """
        try:
            logger.info(
                "创建配置，请求数据: %s", config_in.model_dump(exclude_none=True)
            )

            # 验证配置值
            if not ConfigService._validate_value(config_in.value, config_in.type):
                logger.warning(
                    "配置值无效，类型: %s, 值: %s", config_in.type, config_in.value
                )
                raise ValidationError(
                    msg=t("config.type_mismatch", type=config_in.type.value)
                )

            # 非超级管理员不能创建系统内置配置
            if config_in.is_system and not is_superuser:
                logger.warning("非超级管理员不能创建系统内置配置")
                raise ForbiddenError(msg=t("config.cannot_create_builtin"))

            # 检查配置键是否已存在
            result = await db.execute(
                select(SysConfig).where(SysConfig.key == config_in.key)
            )
            if result.scalar_one_or_none():
                logger.warning("配置键已存在，键名: %s", config_in.key)
                raise ConflictError(msg=t("config.key_exist"))

            # 创建配置对象
            config = SysConfig(
                key=config_in.key,
                value=config_in.value,
                default_value=config_in.default_value,
                validation_rule=config_in.validation_rule,
                description=config_in.description,
                type=config_in.type,
                group=config_in.group,
                is_system=config_in.is_system,
            )

            db.add(config)
            await db.commit()
            await db.refresh(config)

            logger.info("创建配置成功，配置ID: %d", config.id)
            return config

        except (ConflictError, ValidationError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("创建配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def update_config(
        db: AsyncSession,
        config_id: int,
        config_in: SysConfigUpdate,
        *,
        is_superuser: bool = False,
    ) -> SysConfig:
        """
        更新配置

        Args:
            db: 数据库会话
            config_id: 配置ID
            config_in: 配置更新请求

        Returns:
            更新后的配置对象

        Raises:
            NotFoundError: 配置不存在
            ForbiddenError: 配置不可编辑
            ValidationError: 配置值无效
        """
        try:
            logger.info(
                "更新配置，配置ID: %d，请求数据: %s",
                config_id,
                config_in.model_dump(exclude_none=True),
            )

            # 查询配置
            result = await db.execute(
                select(SysConfig).where(SysConfig.id == config_id)
            )
            existing_config = result.scalar_one_or_none()

            if not existing_config:
                logger.warning("配置不存在，配置ID: %d", config_id)
                raise NotFoundError(msg=t("config.not_found", id=config_id))

            # 非超级管理员不能修改系统内置配置
            if existing_config.is_system and not is_superuser:
                logger.warning("系统内置配置禁止修改，配置ID: %d", config_id)
                raise ForbiddenError(msg=t("config.cannot_modify_builtin"))

            # 验证值（如果提供了新值）
            update_data = config_in.model_dump(exclude_unset=True)
            if "value" in update_data:
                config_type = update_data.get("type", existing_config.type)
                if not ConfigService._validate_value(update_data["value"], config_type):
                    logger.warning(
                        "配置值无效，类型: %s, 值: %s",
                        config_type,
                        update_data["value"],
                    )
                    raise ValidationError(
                        msg=t("config.type_mismatch", type=config_type.value)
                    )

            # 更新字段
            for field, value in update_data.items():
                setattr(existing_config, field, value)

            await db.commit()
            await db.refresh(existing_config)

            _invalidate_rate_limit_cache(existing_config.key)

            logger.info("更新配置成功，配置ID: %d", config_id)
            return existing_config

        except (NotFoundError, ForbiddenError, ValidationError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("更新配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def batch_update_configs(
        db: AsyncSession, batch_in: SysConfigBatchUpdate, *, is_superuser: bool = False
    ) -> int:
        """
        批量更新配置

        Args:
            db: 数据库会话
            batch_in: 批量更新请求

        Returns:
            更新的数量
        """
        try:
            logger.info("批量更新配置，配置数量: %d", len(batch_in.configs))

            updated_count = 0
            updated_keys: list[str] = []
            for config_data in batch_in.configs:
                config_id = config_data.get("id")
                value = config_data.get("value")

                if not config_id or value is None:
                    continue

                result = await db.execute(
                    select(SysConfig).where(SysConfig.id == config_id)
                )
                config = result.scalar_one_or_none()

                if config:
                    # 非超级管理员跳过系统内置配置
                    if config.is_system and not is_superuser:
                        continue
                    if ConfigService._validate_value(value, config.type):
                        config.value = value
                        updated_count += 1
                        updated_keys.append(config.key)

            await db.commit()

            for key in updated_keys:
                _invalidate_rate_limit_cache(key)

            logger.info("批量更新配置成功，更新数量: %d", updated_count)
            return updated_count

        except Exception as e:
            await db.rollback()
            logger.error("批量更新配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def reset_configs(
        db: AsyncSession, reset_in: SysConfigReset, *, is_superuser: bool = False
    ) -> int:
        """
        重置配置为默认值

        Args:
            db: 数据库会话
            reset_in: 重置请求

        Returns:
            重置的数量
        """
        try:
            logger.info("重置配置，配置ID列表: %s", reset_in.ids)

            reset_count = 0
            reset_keys: list[str] = []
            for config_id in reset_in.ids:
                result = await db.execute(
                    select(SysConfig).where(SysConfig.id == config_id)
                )
                config = result.scalar_one_or_none()

                if config and config.default_value is not None:
                    # 非超级管理员跳过系统内置配置
                    if config.is_system and not is_superuser:
                        continue
                    config.value = config.default_value
                    reset_count += 1
                    reset_keys.append(config.key)

            await db.commit()

            for key in reset_keys:
                _invalidate_rate_limit_cache(key)

            logger.info("重置配置成功，重置数量: %d", reset_count)
            return reset_count

        except Exception as e:
            await db.rollback()
            logger.error("重置配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def delete_config(
        db: AsyncSession, config_id: int, *, is_superuser: bool = False
    ) -> bool:
        """
        删除配置

        Args:
            db: 数据库会话
            config_id: 配置ID

        Returns:
            是否删除成功

        Raises:
            NotFoundError: 配置不存在
            ForbiddenError: 系统内置配置禁止删除
        """
        try:
            logger.info("删除配置，配置ID: %d", config_id)

            # 查询配置
            result = await db.execute(
                select(SysConfig).where(SysConfig.id == config_id)
            )
            config = result.scalar_one_or_none()

            if not config:
                logger.warning("配置不存在，配置ID: %d", config_id)
                raise NotFoundError(msg=t("config.not_found", id=config_id))

            # 非超级管理员不能删除系统内置配置
            if config.is_system and not is_superuser:
                logger.warning("系统内置配置禁止删除，配置ID: %d", config_id)
                raise ForbiddenError(msg=t("config.cannot_delete_builtin"))

            await db.delete(config)
            await db.commit()

            logger.info("删除配置成功，配置ID: %d", config_id)
            return True

        except (NotFoundError, ForbiddenError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("删除配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def batch_delete_configs(
        db: AsyncSession, config_ids: List[int], *, is_superuser: bool = False
    ) -> int:
        """
        批量删除配置

        Args:
            db: 数据库会话
            config_ids: 配置ID列表

        Returns:
            删除的配置数量

        Raises:
            NotFoundError: 配置不存在
            ForbiddenError: 系统内置配置禁止删除
        """
        try:
            logger.info("批量删除配置，配置ID列表: %s", config_ids)

            delete_count = 0
            for config_id in config_ids:
                try:
                    await ConfigService.delete_config(
                        db, config_id, is_superuser=is_superuser
                    )
                    delete_count += 1
                except Exception as e:
                    logger.error(
                        "删除配置失败，配置ID: %d, 错误: %s", config_id, str(e)
                    )
                    raise e

            logger.info("批量删除配置成功，共删除 %d 个配置", delete_count)
            return delete_count

        except Exception as e:
            await db.rollback()
            logger.error("批量删除配置失败: %s", str(e), exc_info=True)
            raise
