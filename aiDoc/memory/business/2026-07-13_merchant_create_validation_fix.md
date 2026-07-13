# 新建商户「数据校验错误」修复

## 需求描述

用户反馈：新建商户提交后提示「数据校验错误」（后端实际返回 `数据验证失败`），但商户实际已写入数据库。

## 状态

已完成

## 根因

`POST /admin/sys/merchant/add` 端点在 `MerchantService.create_merchant` 成功落库后，构造响应时执行：

```python
data = SysMerchantWithSecret.model_validate(merchant)
data.app_secret = plaintext_secret
```

`SysMerchantWithSecret.app_secret` 原为必填字段（`Field(...)`），而 `SysMerchant` ORM 只有 `app_secret_encrypted`、没有 `app_secret` 属性，`model_validate(merchant)` 因缺少必填字段抛 `pydantic.ValidationError` → 被全局 `pydantic_validation_error_handler` 捕获 → 返回 422 `数据验证失败`。

注意：商户在 `create_merchant` 内已 `commit`，所以报错时数据其实已落库，重试会产生重复商户。

## 修复

`schemas/sys/merchant.py` 的 `SysMerchantWithSecret.app_secret` 由 `Field(...)` 改为 `Field(default="", ...)`，使 `model_validate(merchant)` 通过；端点既有逻辑 `data.app_secret = plaintext_secret` 随即赋真实明文，响应恒为真实值。

未采用「先 `SysMerchantResponseData.model_validate` 再 `model_dump` 重建 `SysMerchantWithSecret`」的写法：`BaseRespEntity` 的 `status` 序列化器会把 bool 转成 `"1"/"2"`，重新校验 `bool` 字段时 Pydantic 拒绝 `"2"`，禁用商户会再次报错。保留默认值写法可使 `status` 全程保持 bool，不经历字符串往返。

## 涉及范围

### 后端

- `modules/admin/schemas/sys/merchant.py`：`SysMerchantWithSecret.app_secret` 加 `default=""` + 注释说明原因。

### 前端

无。前端 `fetchCreateMerchant` 已用 `enableStatusToBoolean` 把 `status` 转成 bool 再发送，`SysMerchantCreate.status: bool` 本身无问题（与 `SysMerchantUpdate.status: BoolField` 的差异不影响 create 路径）。

## 约束与备注

- `SysMerchant` 模型 `code` 字段仅 `index=True` 非唯一，重复编码由 service 层 `MERCHANT_CODE_EXIST` 兜底；`app_id` 唯一由 DB 约束 + 生成重试保证。
- 重置密钥端点用的是 `SysMerchantSecretResetResponse(app_id=..., app_secret=..., ...)` 关键字构造，不走 `model_validate(ORM)`，不受此 Bug 影响。

## 相关文件

- `backend/modules/admin/schemas/sys/merchant.py`
- `backend/modules/admin/endpoints/sys/merchant.py`（未改，仅依赖新默认值）
- `backend/modules/admin/services/sys/merchant_service.py`（未改）

## 记录日期

2026-07-13
