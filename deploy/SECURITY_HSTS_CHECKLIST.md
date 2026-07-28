# HSTS 启用 Checklist

## 背景

HSTS（HTTP Strict-Transport-Security）强制浏览器始终通过 HTTPS 访问站点，防止 SSL 剥离/中间人降级攻击。

当前后端代码已内置 HSTS 下发逻辑（[SecurityHeadersMiddleware](../backend/core/middleware/security_middleware.py)），由配置项 `SECURITY.HSTS_ENABLED` 控制：

- 默认 `HSTS_ENABLED=False` —— **这是正确的**，因为生产 Nginx 当前仅监听 HTTP 80，HTTPS server 块还是注释模板（见 [nginx.conf](nginx.conf) 第 86-97 行）。
- **在站点真正启用 HTTPS 之前，绝不要打开 HSTS**：浏览器一旦缓存 HSTS，在 max-age 内会强制 HTTPS 访问，若站点无 HTTPS 将导致无法访问。

本文件是「HTTPS 就绪后开启 HSTS」的操作清单。

---

## 前置条件（必须先完成）

1. **申请并部署 TLS 证书**（域名证书，Let's Encrypt 或商业证书）。
2. **在 [nginx.conf](nginx.conf) 启用 HTTPS server 块**：取消第 86-97 行注释，配置 `ssl_certificate` / `ssl_certificate_key`，监听 443。
3. **开启 HTTP → HTTPS 重定向**：取消第 17 行 `return 301 https://$host$request_uri;` 注释，让 80 端口请求跳转到 443。
4. **确认后端能识别协议**：nginx 已设置 `X-Forwarded-Proto $scheme;`（第 40 行）；如后端需基于该头生成 HTTPS 链接，确认已正确读取（通常反代场景下无需后端改动）。
5. 用浏览器与 `curl -I https://<域名>/` 验证 HTTPS 可正常访问、证书可信。

---

## 开启 HSTS（二选一）

### 方式 A：应用层下发（推荐，与现有代码一致）

在 `.env.prod` 增加：

```env
SECURITY__HSTS_ENABLED=true
```

[SecurityHeadersMiddleware](../backend/core/middleware/security_middleware.py) 会自动在响应头下发：

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

`max-age` 与 `includeSubDomains` 取自 [settings_model.py](../backend/core/config/settings_model.py) 的 `HSTS_VALUE`（默认 `max-age=31536000; includeSubDomains`），可在 `.env.prod` 用 `SECURITY__HSTS_VALUE=...` 覆盖。

### 方式 B：Nginx 层下发

在 nginx HTTPS server 块内：

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

选这种方式时，保持 `SECURITY__HSTS_ENABLED=false`，避免重复下发。

---

## max-age 与 preload 建议

- **首次启用建议先用小 max-age**（如 `max-age=300` 或 `max-age=86400` 即 1 天）观察 1-2 天，确认无 HTTPS 可用性问题（子域名证书、混合内容等），再升到 `31536000`（1 年）。
- **`includeSubDomains` 风险**：仅在所有子域名都支持 HTTPS 时启用，否则会让未上 HTTPS 的子域不可访问。
- **`preload`**：如需提交到 [HSTS Preload List](https://hstspreload.org/)，值为 `max-age=31536000; includeSubDomains; preload`。提交前务必确认所有子域名长期 HTTPS 可用，**preload 几乎不可逆**，谨慎评估。

---

## 验证

```bash
curl -I https://<域名>/
# 期望响应头包含：
# Strict-Transport-Security: max-age=31536000; includeSubDomains
```

再用浏览器 DevTools → Network → Response Headers 确认。

---

## 回滚

- 应用层：把 `.env.prod` 的 `SECURITY__HSTS_ENABLED` 改回 `false`（或删除该行），重启服务。
- Nginx 层：删除 `add_header Strict-Transport-Security ...` 行，`nginx -s reload`。
- 注意：已被浏览器缓存的 HSTS 策略在原 max-age 到期前仍生效，回滚不会立即让 HTTP 重新可用。这就是先用小 max-age 验证的原因。
