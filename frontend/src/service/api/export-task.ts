import type { AxiosError } from '@sa/axios';
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

/** download export file (Blob 直传，返回 {data, error} 兼容既有调用) */
export async function fetchDownloadExportFile(
  taskId: number
): Promise<{ data: Blob | null; error: AxiosError | null }> {
  return request<Blob, 'blob'>({
    url: `/admin/sys/export/task/${taskId}/download`,
    method: 'get',
    responseType: 'blob'
  });
}
