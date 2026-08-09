import { getServiceBaseURL } from '@/utils/service';
import { request } from '../request';

const isHttpProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
const { baseURL } = getServiceBaseURL(import.meta.env, isHttpProxy);


/** 上传单个文件 */
export function fetchUploadFile(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  return request<Api.FileManage.FileInfo>({
    url: '/admin/sys/file/upload',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}

/** 批量上传文件 */
export function fetchUploadFiles(files: File[]) {
  const formData = new FormData();
  files.forEach(f => formData.append('files', f));
  return request<Api.FileManage.FileInfo[]>({
    url: '/admin/sys/file/upload/batch',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}

/** 获取文件列表 */
export function fetchGetFileList(params?: Api.FileManage.FileSearchParams) {
  return request<Api.FileManage.FileList>({
    url: '/admin/sys/file/list',
    method: 'get',
    params
  });
}

/** 获取文件详情 */
export function fetchGetFile(fileId: number) {
  return request<Api.FileManage.FileListItem>({
    url: `/admin/sys/file/${fileId}`,
    method: 'get'
  });
}

/** 下载文件 (返回 Blob) */
export async function fetchDownloadFile(fileId: number): Promise<Blob> {
  const { data, error } = await request<Blob, 'blob'>({
    url: `/admin/sys/file/${fileId}/download`,
    method: 'get',
    responseType: 'blob'
  });
  if (error) throw error;
  return data;
}

/** 换取文件预览令牌（短期 5 分钟、绑定单文件，后端 POST /preview-token） */
export function fetchGetPreviewToken(fileId: number) {
  return request<{ preview_token: string; expires_in: number }>({
    url: `/admin/sys/file/${fileId}/preview-token`,
    method: 'post'
  });
}

/** 根据预览令牌构造预览 URL（用于 img/video src）
 *  不再直接使用 access token，避免令牌进入 URL 日志/Referer 造成泄露 */
export function getFilePreviewUrl(fileId: number, previewToken: string): string {
  const rawToken = previewToken.replace(/^Bearer\s+/i, '') || '';
  return `${baseURL}/admin/sys/file/${fileId}/preview?token=${rawToken}`;
}

/** 删除文件 */
export function fetchDeleteFile(fileId: number) {
  return request<void>({
    url: `/admin/sys/file/${fileId}`,
    method: 'delete'
  });
}

/** 批量删除文件 */
export function fetchBatchDeleteFiles(fileIds: number[]) {
  return request<void>({
    url: '/admin/sys/file/batch',
    method: 'delete',
    data: fileIds
  });
}
