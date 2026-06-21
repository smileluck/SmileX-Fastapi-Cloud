import { request } from '../request';

/** ==================== 定时任务 API ==================== */

export function fetchGetScheduledTaskList(params?: Api.Scheduler.ScheduledTaskSearchParams) {
  return request<Api.Scheduler.ScheduledTaskList>({
    url: '/admin/sys/scheduler-task/list',
    method: 'get',
    params
  });
}

export function fetchGetScheduledTask(taskId: number) {
  return request<Api.Scheduler.ScheduledTask>({
    url: `/admin/sys/scheduler-task/${taskId}`,
    method: 'get'
  });
}

export function fetchCreateScheduledTask(data: Api.Scheduler.ScheduledTaskCreate) {
  return request<Api.Scheduler.ScheduledTask>({
    url: '/admin/sys/scheduler-task/add',
    method: 'post',
    data
  });
}

export function fetchUpdateScheduledTask(taskId: number, data: Api.Scheduler.ScheduledTaskUpdate) {
  return request<Api.Scheduler.ScheduledTask>({
    url: `/admin/sys/scheduler-task/${taskId}`,
    method: 'put',
    data
  });
}

export function fetchDeleteScheduledTask(taskId: number) {
  return request<void>({
    url: `/admin/sys/scheduler-task/${taskId}`,
    method: 'delete'
  });
}

export function fetchBatchDeleteScheduledTask(taskIds: number[]) {
  return request<void>({
    url: '/admin/sys/scheduler-task/batch/delete',
    method: 'delete',
    data: taskIds
  });
}

export function fetchToggleScheduledTaskStatus(taskId: number, status: boolean) {
  return request<Api.Scheduler.ScheduledTask>({
    url: `/admin/sys/scheduler-task/${taskId}/status`,
    method: 'put',
    params: { status }
  });
}

export function fetchManualTriggerTask(taskId: number) {
  return request<void>({
    url: `/admin/sys/scheduler-task/${taskId}/trigger`,
    method: 'post'
  });
}

export function fetchCronPreview(cronExpression: string) {
  return request<Api.Scheduler.CronPreviewResponse>({
    url: '/admin/sys/scheduler-task/cron-preview',
    method: 'post',
    data: { cron_expression: cronExpression }
  });
}

export function fetchGetRegistryTasks() {
  return request<Api.Scheduler.RegistryTask[]>({
    url: '/admin/sys/scheduler-task/registry/list',
    method: 'get'
  });
}

export function fetchGetTaskParamsSchema(taskKey: string) {
  return request<Api.Scheduler.TaskParamsSchema | null>({
    url: `/admin/sys/scheduler-task/registry/${encodeURIComponent(taskKey)}/schema`,
    method: 'get'
  });
}

export function fetchSyncRegistry() {
  return request<{ synced: string[] }>({
    url: '/admin/sys/scheduler-task/sync-registry',
    method: 'post'
  });
}

/** ==================== 任务执行日志 API ==================== */

export function fetchGetTaskLogList(params?: Api.Scheduler.TaskLogSearchParams) {
  return request<Api.Scheduler.TaskLogList>({
    url: '/admin/sys/scheduler-log/list',
    method: 'get',
    params
  });
}

export function fetchGetTaskLogDetail(logId: number) {
  return request<Api.Scheduler.TaskLogDetail>({
    url: `/admin/sys/scheduler-log/${logId}`,
    method: 'get'
  });
}

export function fetchBatchDeleteTaskLog(logIds: number[]) {
  return request<void>({
    url: '/admin/sys/scheduler-log/batch/delete',
    method: 'delete',
    data: logIds
  });
}

export function fetchClearTaskLog(days?: number) {
  return request<void>({
    url: '/admin/sys/scheduler-log/clear',
    method: 'delete',
    params: { days }
  });
}
