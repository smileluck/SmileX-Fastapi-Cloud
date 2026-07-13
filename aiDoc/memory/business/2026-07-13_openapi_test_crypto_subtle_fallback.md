# 开放API测试页 crypto.subtle 报错修复

## 需求描述

用户反馈：在 `/proxy-default/open/demo/ping`（开放API 测试 demo 页）点发送时，前端报 `TypeError: Cannot read properties of undefined (reading 'importKey')`。

## 状态

已完成

## 根因

`views/demo/openapi-test/index.vue` 用浏览器原生 WebCrypto 计算签名：

- `crypto.subtle.digest('SHA-256', ...)`
- `crypto.subtle.importKey('raw', ..., {name:'HMAC', hash:'SHA-256'}, ...)`
- `crypto.subtle.sign('HMAC', ...)`

`crypto.subtle` **仅在安全上下文可用**（HTTPS 或 localhost）。用户经反向代理（`/proxy-default/...`）以 HTTP + 局域网 IP 访问，`window.crypto.subtle` 为 `undefined` → 访问 `.importKey` 即抛错。

注意：`crypto.getRandomValues`（生成 nonce）**不受**安全上下文限制，HTTP 下可用，故 `genNonce` 无需改。

## 修复

新增 `frontend/src/utils/hmac-sha256.ts`：

- 优先用原生 `crypto.subtle`（安全上下文，原生、快）；
- 不可用时回退到内置的纯 JS SHA-256 / HMAC-SHA256（FIPS 180-4 标准实现），保证 HTTP 局域网下也能算签名。
- 纯 JS 实现已用 3 个标准向量验证一致：
  - `SHA-256("")` = `e3b0c442...b855`
  - `SHA-256("abc")` = `ba7816bf...15ad`
  - `HMAC-SHA256("key","The quick brown fox jumps over the lazy dog")` = `f7bc83f4...3cd8`

`views/demo/openapi-test/index.vue` 改为 `import { sha256Hex, hmacSha256Hex } from '@/utils/hmac-sha256'`，删掉本地 `bufToHex / sha256Hex / hmacSha256Hex`（直接用 `crypto.subtle` 的版本）。其余（canonical 拼装、请求头、`genNonce`）不变。

签名结果与原生一致（算法确定），后端 HMAC 校验不受影响。

## 涉及范围

### 前端

- 新增 `utils/hmac-sha256.ts`：`sha256Hex` / `hmacSha256Hex`（原生优先 + 纯 JS 回退），并导出 `sha256Bytes` / `hmacSha256Bytes`。
- `views/demo/openapi-test/index.vue`：改用上述 util，移除本地 `crypto.subtle` 调用。

### 后端

无（后端 `core/security/openapi.py` 的 HMAC-SHA256 校验逻辑不变）。

## 约束与备注

- 选择「原生优先 + 纯 JS 回退」而非「检测后报错提示用 HTTPS」：该页是验证开放API 鉴权链路的工具，常在 HTTP 局域网部署里使用，要求能直接算出签名。纯 JS 实现仅用于与后端对齐签名（机密性由 app_secret 保证），不构成安全边界。
- 若后续前端引入了 `crypto-js`/`js-sha256` 等库，可替换纯 JS 回退实现；当前未引入新依赖。

## 相关文件

- `frontend/src/utils/hmac-sha256.ts`
- `frontend/src/views/demo/openapi-test/index.vue`

## 记录日期

2026-07-13
