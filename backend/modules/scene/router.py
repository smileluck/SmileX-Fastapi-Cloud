#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
场景管理路由
"""
from fastapi import APIRouter

from .endpoints.scene_group import scene_group_router
from .endpoints.scene_map import scene_map_router
from .endpoints.scene_map_annotation import scene_map_annotation_router
from .endpoints.scene_map_object import scene_map_object_router
from .endpoints.scene_map_path import scene_map_path_router
from .endpoints.scene_map_editor import scene_map_editor_router

router = APIRouter(prefix="/scene")

router.include_router(scene_group_router)           # /scene/group
router.include_router(scene_map_router)             # /scene/map
router.include_router(scene_map_annotation_router)  # /scene/map/{map_id}/annotation
router.include_router(scene_map_object_router)      # /scene/map/{map_id}/object
router.include_router(scene_map_path_router)        # /scene/map/{map_id}/path
router.include_router(scene_map_editor_router)      # /scene/map/{map_id}/editor
