<!-- last-updated: 2026-10-02 -->
# 前端 API 封装示例

## 用途

展示如何封装前端 API 调用函数。

## 核心原则

- 函数名使用 `fetch` 前缀
- 使用 `@sa/axios` 封装的请求方法
- Status 字段使用 `enableStatusToBoolean()` 转换
- 类型定义在 `frontend/src/typings/api/` 中

## 示例

### 类型定义 `frontend/src/typings/api/system-manage.d.ts`

```typescript
declare namespace Api {
  namespace SystemManage {
    /** 用户信息 */
    interface UserInfo {
      id: number;
      username: string;
      nickname: string;
      email: string | null;
      phone: string | null;
      avatar: string | null;
      status: EnableStatus;  // "1" | "2"
      is_system: EnableStatus;
      created_at: string;
      updated_at: string;
    }

    /** 用户列表查询参数 */
    interface UserListParams {
      username?: string;
      phone?: string;
      status?: EnableStatus;
      page: number;
      page_size: number;
    }
  }
}
```

### API 封装 `frontend/src/service/api/system-manage.ts`

```typescript
import { request } from '@/service/request';
import { enableStatusToBoolean } from '@/utils/status';

/** 获取用户列表 */
export function fetchGetUserList(params: Api.SystemManage.UserListParams) {
  return request<Api.Common.PaginatingQueryRecord<Api.SystemManage.UserInfo>>({
    url: '/admin/sys/user/list',
    method: 'get',
    params: {
      ...params,
      status: params.status ? enableStatusToBoolean(params.status) : undefined,
    },
  });
}

/** 获取用户详情 */
export function fetchGetUserDetail(userId: number) {
  return request<Api.SystemManage.UserInfo>({
    url: `/admin/sys/user/${userId}`,
    method: 'get',
  });
}

/** 创建用户 */
export function fetchCreateUser(data: Omit<Api.SystemManage.UserInfo, 'id'>) {
  return request<boolean>({
    url: '/admin/sys/user',
    method: 'post',
    data,
  });
}

/** 删除用户 */
export function fetchDeleteUser(userId: number) {
  return request<boolean>({
    url: `/admin/sys/user/${userId}`,
    method: 'delete',
  });
}
```

## 关键点

- 发送请求时，`status` 字段**必须**使用 `enableStatusToBoolean()` 转换
- 接收响应时，后端已自动将 `status` 序列化为 `"1"`/`"2"` 字符串
- URL 前缀 `/admin/` 对应后端模块路由前缀
- 返回类型使用 `Api.Common.PaginatingQueryRecord<T>` 包装分页数据

## 真实参考文件

- `frontend/src/service/api/system-manage.ts`
- `frontend/src/typings/api/`
