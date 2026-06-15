import { request } from '../request';
import { enableStatusToBoolean } from '@/utils/status';

/** ==================== 场景分组管理 API ==================== */

/** get scene group list */
export function fetchGetSceneGroupList(params?: Api.Scene.SceneGroupSearchParams) {
  return request<Api.Scene.SceneGroupList>({
    url: '/scene/group/list',
    method: 'get',
    params
  });
}

/** get scene group tree */
export function fetchGetSceneGroupTree() {
  return request<Api.Scene.SceneGroupTreeNode[]>({
    url: '/scene/group/tree',
    method: 'get'
  });
}

/** get scene group by id */
export function fetchGetSceneGroup(id: number) {
  return request<Api.Scene.SceneGroup>({
    url: `/scene/group/${id}`,
    method: 'get'
  });
}

/** create scene group */
export function fetchCreateSceneGroup(data: Api.Scene.SceneGroupCreate) {
  return request<Api.Scene.SceneGroup>({
    url: '/scene/group/add',
    method: 'post',
    data: {
      ...data,
      ...(data.status !== undefined ? { status: enableStatusToBoolean(data.status) } : {})
    }
  });
}

/** update scene group */
export function fetchUpdateSceneGroup(id: number, data: Api.Scene.SceneGroupUpdate) {
  return request<Api.Scene.SceneGroup>({
    url: `/scene/group/${id}`,
    method: 'put',
    data: {
      ...data,
      ...(data.status !== undefined ? { status: enableStatusToBoolean(data.status) } : {})
    }
  });
}

/** delete scene group */
export function fetchDeleteSceneGroup(id: number) {
  return request<void>({
    url: `/scene/group/${id}`,
    method: 'delete'
  });
}

/** ==================== 场景地图管理 API ==================== */

/** get scene map list */
export function fetchGetSceneMapList(params?: Api.Scene.SceneMapSearchParams) {
  return request<Api.Scene.SceneMapList>({
    url: '/scene/map/list',
    method: 'get',
    params
  });
}

/** get scene map by id */
export function fetchGetSceneMap(id: number) {
  return request<Api.Scene.SceneMap>({
    url: `/scene/map/${id}`,
    method: 'get'
  });
}

/** create scene map */
export function fetchCreateSceneMap(data: Api.Scene.SceneMapCreate) {
  return request<Api.Scene.SceneMap>({
    url: '/scene/map/add',
    method: 'post',
    data: {
      ...data,
      ...(data.status !== undefined ? { status: enableStatusToBoolean(data.status) } : {})
    }
  });
}

/** update scene map */
export function fetchUpdateSceneMap(id: number, data: Api.Scene.SceneMapUpdate) {
  return request<Api.Scene.SceneMap>({
    url: `/scene/map/${id}`,
    method: 'put',
    data: {
      ...data,
      ...(data.status !== undefined ? { status: enableStatusToBoolean(data.status) } : {})
    }
  });
}

/** delete scene map */
export function fetchDeleteSceneMap(id: number) {
  return request<void>({
    url: `/scene/map/${id}`,
    method: 'delete'
  });
}

/** ==================== 场景地图标注 API ==================== */

/** get map annotations */
export function fetchGetMapAnnotations(mapId: number, params?: Api.Scene.CommonSearchParams) {
  return request<Api.Scene.SceneMapAnnotationList>({
    url: `/scene/map/${mapId}/annotation/list`,
    method: 'get',
    params
  });
}

/** create map annotation */
export function fetchCreateMapAnnotation(data: Api.Scene.SceneMapAnnotationCreate) {
  return request<Api.Scene.SceneMapAnnotation>({
    url: `/scene/map/${data.map_id}/annotation/add`,
    method: 'post',
    data
  });
}

/** update map annotation */
export function fetchUpdateMapAnnotation(mapId: number, id: number, data: Api.Scene.SceneMapAnnotationUpdate) {
  return request<Api.Scene.SceneMapAnnotation>({
    url: `/scene/map/${mapId}/annotation/${id}`,
    method: 'put',
    data
  });
}

/** delete map annotation */
export function fetchDeleteMapAnnotation(mapId: number, id: number) {
  return request<void>({
    url: `/scene/map/${mapId}/annotation/${id}`,
    method: 'delete'
  });
}

/** ==================== 场景地图物体 API ==================== */

/** get map objects */
export function fetchGetMapObjects(mapId: number, params?: Api.Scene.CommonSearchParams) {
  return request<Api.Scene.SceneMapObjectList>({
    url: `/scene/map/${mapId}/object/list`,
    method: 'get',
    params
  });
}

/** create map object */
export function fetchCreateMapObject(data: Api.Scene.SceneMapObjectCreate) {
  return request<Api.Scene.SceneMapObject>({
    url: `/scene/map/${data.map_id}/object/add`,
    method: 'post',
    data
  });
}

/** update map object */
export function fetchUpdateMapObject(mapId: number, id: number, data: Api.Scene.SceneMapObjectUpdate) {
  return request<Api.Scene.SceneMapObject>({
    url: `/scene/map/${mapId}/object/${id}`,
    method: 'put',
    data
  });
}

/** delete map object */
export function fetchDeleteMapObject(mapId: number, id: number) {
  return request<void>({
    url: `/scene/map/${mapId}/object/${id}`,
    method: 'delete'
  });
}

/** ==================== 场景地图路径 API ==================== */

/** get map paths */
export function fetchGetMapPaths(mapId: number, params?: Api.Scene.CommonSearchParams) {
  return request<Api.Scene.SceneMapPath[]>({
    url: `/scene/map/${mapId}/path/list`,
    method: 'get',
    params
  });
}

/** create map path */
export function fetchCreateMapPath(data: Api.Scene.SceneMapPathCreate) {
  return request<Api.Scene.SceneMapPath>({
    url: `/scene/map/${data.map_id}/path/add`,
    method: 'post',
    data
  });
}

/** update map path */
export function fetchUpdateMapPath(mapId: number, id: number, data: Api.Scene.SceneMapPathUpdate) {
  return request<Api.Scene.SceneMapPath>({
    url: `/scene/map/${mapId}/path/${id}`,
    method: 'put',
    data
  });
}

/** delete map path */
export function fetchDeleteMapPath(mapId: number, id: number) {
  return request<void>({
    url: `/scene/map/${mapId}/path/${id}`,
    method: 'delete'
  });
}

/** ==================== 地图编辑器 API ==================== */

/** get editor full data */
export function fetchGetEditorMapData(mapId: number) {
  return request<Api.Scene.EditorMapData>({
    url: `/scene/map/${mapId}/editor/data`,
    method: 'get'
  });
}

/** save editor data */
export function fetchSaveEditorData(mapId: number, data: Api.Scene.EditorSaveRequest) {
  return request<void>({
    url: `/scene/map/${mapId}/editor/save`,
    method: 'post',
    data
  });
}
