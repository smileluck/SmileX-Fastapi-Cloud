import { request } from '../request';
import { enableStatusToBoolean } from '@/utils/status';

/** ==================== 任务管理 API ==================== */

/** get task list */
export function fetchGetTaskList(params?: Api.Task.TaskSearchParams) {
  return request<Api.Task.TaskList>({
    url: '/task/manage/list',
    method: 'get',
    params: {
      ...params,
      enabled: params?.enabled ? enableStatusToBoolean(params.enabled) : undefined
    }
  });
}

/** get task by id */
export function fetchGetTask(id: number) {
  return request<Api.Task.Task>({
    url: `/task/manage/${id}`,
    method: 'get'
  });
}

/** create task */
export function fetchCreateTask(data: Api.Task.TaskCreate) {
  return request<Api.Task.Task>({
    url: '/task/manage/add',
    method: 'post',
    data
  });
}

/** update task */
export function fetchUpdateTask(id: number, data: Api.Task.TaskUpdate) {
  return request<Api.Task.Task>({
    url: `/task/manage/${id}`,
    method: 'put',
    data
  });
}

/** delete task */
export function fetchDeleteTask(id: number) {
  return request<void>({
    url: `/task/manage/${id}`,
    method: 'delete'
  });
}

/** toggle task enabled */
export function fetchToggleTaskEnabled(id: number, enabled: boolean) {
  return request<Api.Task.Task>({
    url: `/task/manage/${id}/toggle`,
    method: 'put',
    data: { enabled }
  });
}

/** ==================== 任务执行 API ==================== */

/** start task execution */
export function fetchStartTaskExecution(taskId: number, robotIds: number[] = []) {
  return request<Api.Task.TaskExecution>({
    url: `/task/execution/${taskId}/start`,
    method: 'post',
    data: robotIds
  });
}

/** pause execution */
export function fetchPauseExecution(execId: number) {
  return request<Api.Task.TaskExecution>({
    url: `/task/execution/${execId}/pause`,
    method: 'post'
  });
}

/** resume execution */
export function fetchResumeExecution(execId: number) {
  return request<Api.Task.TaskExecution>({
    url: `/task/execution/${execId}/resume`,
    method: 'post'
  });
}

/** stop execution */
export function fetchStopExecution(execId: number) {
  return request<Api.Task.TaskExecution>({
    url: `/task/execution/${execId}/stop`,
    method: 'post'
  });
}

/** get active executions */
export function fetchGetActiveExecutions(params?: Api.Task.CommonSearchParams) {
  return request<Api.Task.TaskExecutionList>({
    url: '/task/execution/active',
    method: 'get',
    params
  });
}

/** get execution history */
export function fetchGetExecutionHistory(params?: Api.Task.TaskExecutionSearchParams) {
  return request<Api.Task.TaskExecutionList>({
    url: '/task/execution/history',
    method: 'get',
    params
  });
}

/** get execution detail */
export function fetchGetExecutionDetail(execId: number) {
  return request<Api.Task.TaskExecutionDetail>({
    url: `/task/execution/detail/${execId}`,
    method: 'get'
  });
}
