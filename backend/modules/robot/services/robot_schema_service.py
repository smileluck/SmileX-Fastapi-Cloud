import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

logger = logging.getLogger(__name__)


class RobotSchemaService:
    _robot_map_binding_ready = False

    @classmethod
    async def ensure_robot_map_binding(cls, db: AsyncSession) -> None:
        if cls._robot_map_binding_ready:
            return

        if await cls._has_robot_map_id(db):
            cls._robot_map_binding_ready = True
            return

        try:
            if settings.DATABASE.type.value == "postgresql":
                await db.execute(text("alter table robot add column map_id bigint null"))
            else:
                await db.execute(text("alter table robot add column map_id bigint null comment '绑定场景地图ID'"))
            await cls._add_foreign_key(db)
            await db.commit()
        except SQLAlchemyError as exc:
            await db.rollback()
            if not await cls._has_robot_map_id(db):
                raise exc
            logger.info("robot.map_id 已由其他迁移或进程补齐")

        cls._robot_map_binding_ready = True

    @staticmethod
    async def _has_robot_map_id(db: AsyncSession) -> bool:
        if settings.DATABASE.type.value == "postgresql":
            result = await db.execute(
                text(
                    """
                    select 1
                    from information_schema.columns
                    where table_name = 'robot'
                      and column_name = 'map_id'
                    """
                )
            )
        else:
            result = await db.execute(
                text(
                    """
                    select 1
                    from information_schema.columns
                    where table_schema = database()
                      and table_name = 'robot'
                      and column_name = 'map_id'
                    """
                )
            )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def _add_foreign_key(db: AsyncSession) -> None:
        try:
            await db.execute(
                text(
                    """
                    alter table robot
                    add constraint fk_robot_map_id_scene_map
                    foreign key (map_id) references scene_map(id)
                    """
                )
            )
        except SQLAlchemyError:
            logger.info("robot.map_id 外键已存在或当前数据库不支持重复添加，跳过")
