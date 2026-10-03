<!-- last-updated: 2026-05-18 -->
# 前端工具函数使用示例

## 用途

展示前端开发中工具函数的典型使用场景。

## Status 字段转换

```typescript
import { enableStatusToBoolean, booleanToEnableStatus } from '@/utils/status';

// 前端 → 后端：发送请求前转换
const params = {
  username: 'admin',
  status: enableStatusToBoolean(formData.status),  // "1" → true, "2" → false
};
await fetchGetUserList(params);

// 后端 → 前端：响应中已经是 "1"/"2" 字符串，可直接使用
const statusText = userInfo.status === '1' ? '启用' : '禁用';

// 前端表单默认值
const defaultStatus = booleanToEnableStatus(true);  // true → "1"
```

## 本地存储

```typescript
import { localStg } from '@/utils/storage';

// 存储
localStg.set('token', 'xxx');
localStg.set('userInfo', { id: 1, username: 'admin' });

// 读取
const token = localStg.get('token');
const userInfo = localStg.get('userInfo');

// 删除
localStg.remove('token');
```

## 深拷贝

```typescript
import { klona } from '@sa/utils';

// 深拷贝对象（解耦引用）
const original = { list: [1, 2, 3], nested: { key: 'value' } };
const copy = klona(original);
copy.list.push(4);  // 不影响 original
```

## 唯一 ID 生成

```typescript
import { nanoid } from '@sa/utils';

// 生成前端唯一标识
const tempId = nanoid();
```

## HTTP 请求

```typescript
import { request } from '@/service/request';

// GET 请求
const result = await request<Api.UserInfo>({
  url: '/admin/sys/user/1',
  method: 'get',
});

// POST 请求
const result = await request<boolean>({
  url: '/admin/sys/user',
  method: 'post',
  data: { username: 'newuser', password: '123456' },
});
```

## 关键点

- 所有工具函数**必须**通过上述方式引入，禁止在组件中重新实现
- Status 字段转换是前后端协作中最容易出错的地方，务必按照 `boundary.md` 中的流程处理
- `localStg` 提供类型安全的存储操作，优于直接使用 `localStorage`
