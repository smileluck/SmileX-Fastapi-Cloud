import { request } from '../request';

/** submit async export task */
export function fetchSubmitExportTask(data: Api.ExportTask.ExportTaskSubmit) {
  return request<Api.ExportTask.ExportTask>({
    url: '/admin/sys/export/task',
    method: 'post',
    data
  });
}

/** get current user's export task list */
export function fetchGetExportTaskList(params?: Api.ExportTask.ExportTaskSearchParams) {
  return request<Api.ExportTask.ExportTaskList>({
    url: '/admin/sys/export/task/list',
    method: 'get',
    params
  });
}

/** get export task detail/status */
export function fetchGetExportTask(taskId: number) {
  return request<Api.ExportTask.ExportTask>({
    url: `/admin/sys/export/task/${taskId}`,
    method: 'get'
  });
}

/** download export file */
export function fetchDownloadExportFile(taskId: number) {
  return request<Blob>({
    url: `/admin/sys/export/task/${taskId}/download`,
    method: 'get',
    responseType: 'blob'
  });
}
