import { request } from '../request';
import { enableStatusToBoolean } from '@/utils/status';

/** ==================== 机器人型号管理 API ==================== */

/** get robot model list */
export function fetchGetRobotModelList(params?: Api.Robot.RobotModelSearchParams) {
  return request<Api.Robot.RobotModelList>({
    url: '/robot/model/list',
    method: 'get',
    params
  });
}

/** get all robot models (for dropdown) */
export function fetchGetAllRobotModels() {
  return request<Api.Robot.AllRobotModel[]>({
    url: '/robot/model/all',
    method: 'get'
  });
}

/** get robot model by id */
export function fetchGetRobotModel(id: number) {
  return request<Api.Robot.RobotModel>({
    url: `/robot/model/${id}`,
    method: 'get'
  });
}

/** create robot model */
export function fetchCreateRobotModel(data: Api.Robot.RobotModelCreate) {
  return request<Api.Robot.RobotModel>({
    url: '/robot/model/add',
    method: 'post',
    data: {
      ...data,
      status: enableStatusToBoolean(data.status)
    }
  });
}

/** update robot model */
export function fetchUpdateRobotModel(id: number, data: Api.Robot.RobotModelUpdate) {
  return request<Api.Robot.RobotModel>({
    url: `/robot/model/${id}`,
    method: 'put',
    data: {
      ...data,
      ...(data.status !== undefined ? { status: enableStatusToBoolean(data.status) } : {})
    }
  });
}

/** delete robot model */
export function fetchDeleteRobotModel(id: number) {
  return request<void>({
    url: `/robot/model/${id}`,
    method: 'delete'
  });
}

/** ==================== 机器人管理 API ==================== */

/** get robot list */
export function fetchGetRobotList(params?: Api.Robot.RobotSearchParams) {
  return request<Api.Robot.RobotList>({
    url: '/robot/manage/list',
    method: 'get',
    params
  });
}

/** get robot by id */
export function fetchGetRobot(id: number) {
  return request<Api.Robot.Robot>({
    url: `/robot/manage/${id}`,
    method: 'get'
  });
}

/** create robot */
export function fetchCreateRobot(data: Api.Robot.RobotCreate) {
  return request<Api.Robot.Robot>({
    url: '/robot/manage/add',
    method: 'post',
    data
  });
}

/** update robot */
export function fetchUpdateRobot(id: number, data: Api.Robot.RobotUpdate) {
  return request<Api.Robot.Robot>({
    url: `/robot/manage/${id}`,
    method: 'put',
    data
  });
}

/** delete robot */
export function fetchDeleteRobot(id: number) {
  return request<void>({
    url: `/robot/manage/${id}`,
    method: 'delete'
  });
}

/** ==================== 机器人状态记录 API (只读) ==================== */

/** get robot status records */
export function fetchGetRobotStatusRecords(robotId: number, params?: Api.Robot.CommonSearchParams) {
  return request<Api.Robot.RobotStatusRecordList>({
    url: `/robot/manage/${robotId}/status/list`,
    method: 'get',
    params
  });
}

/** get latest robot status record */
export function fetchGetLatestRobotStatus(robotId: number) {
  return request<Api.Robot.RobotStatusRecord>({
    url: `/robot/manage/${robotId}/status/latest`,
    method: 'get'
  });
}
