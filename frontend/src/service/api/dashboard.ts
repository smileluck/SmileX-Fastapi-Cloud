import { request } from '../request';

/** 获取首页仪表盘汇总数据 */
export function fetchDashboardSummary() {
  return request<Api.Dashboard.Summary>({
    url: '/admin/sys/dashboard/summary',
    method: 'get'
  });
}
