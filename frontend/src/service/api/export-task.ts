import type { AxiosError } from 'axios';
import axios from 'axios';
import { localStg } from '@/utils/storage';
import { getServiceBaseURL } from '@/utils/service';
import { request } from '../request';

const isHttpProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
const { baseURL } = getServiceBaseURL(import.meta.env, isHttpProxy);

function getAuthHeader() {
  const token = localStg.get('token');
  return token || '';
}

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

/** download export file (Blob 直传，绕开 flat-request 的 responseType:'json' 限制，返回 {error,data} 兼容既有调用) */
export async function fetchDownloadExportFile(
  taskId: number
): Promise<{ data: Blob | null; error: AxiosError | null }> {
  try {
    const response = await axios.get(`${baseURL}/admin/sys/export/task/${taskId}/download`, {
      responseType: 'blob',
      headers: { Authorization: getAuthHeader() }
    });
    return { data: response.data, error: null };
  } catch (e) {
    return { data: null, error: e as AxiosError };
  }
}
