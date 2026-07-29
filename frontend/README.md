# SmileX Cloud · Frontend

SmileX 云服务平台的前端，基于 [SoybeanAdmin](https://github.com/soybeanjs/soybean-admin)（Vue 3 + Vite + TypeScript + Naive UI + Pinia + UnoCSS）二次开发，对接 [`../backend`](../backend) 的 FastAPI 接口。

> 感谢 SoybeanAdmin 提供的优秀后台管理模板。本仓库在其基础上做了业务化改造：菜单 / 权限 / 请求层对接 SmileX 后端、新增业务页面、组件级主题配置、中英文 i18n 等。

## 技术栈

| 类别 | 选型 |
|---|---|
| 框架 / 语言 | Vue 3 / TypeScript |
| 构建 / 包管理 | Vite / pnpm（monorepo） |
| UI 库 | Naive UI |
| 状态管理 | Pinia |
| 路由 | Vue Router + Elegant Router（文件路由） |
| 样式 | UnoCSS |
| 国际化 | vue-i18n（中 / 英） |
| 请求 | Axios（封装于 `@sa/axios`） |
| 图表 | ECharts |

## 环境要求

- **Node.js**：>= 20.19.0
- **pnpm**：>= 10.5.0
- **git**

> 采用 pnpm monorepo，请勿使用 npm / yarn 安装依赖。

## 快速开始

```bash
cd frontend
pnpm install            # 安装依赖
cp .env .env.local      # 复制并修改 API 地址等配置
pnpm dev                # 启动开发服务器（默认 test 模式）
```

开发服务器默认指向后端 `http://localhost:8000`，请先启动后端（见 [`../backend/README.md`](../backend/README.md)）。

## 常用脚本

| 命令 | 说明 |
|---|---|
| `pnpm dev` | 开发模式（`--mode test`） |
| `pnpm dev:prod` | 以生产环境变量启动开发服务器 |
| `pnpm build` | 构建生产产物 |
| `pnpm build:test` | 构建测试环境产物 |
| `pnpm preview` | 预览构建产物 |
| `pnpm typecheck` | TypeScript 类型检查（vue-tsc） |
| `pnpm lint` | ESLint 检查并自动修复 |
| `pnpm gen-route` | 重新生成路由声明 |
| `pnpm gen-theme-catalog` | 生成主题组件目录（主题抽屉用） |
| `pnpm commit` | 生成符合 Conventional Commits 的提交信息 |

## 目录结构

```
frontend/
├── src/
│   ├── views/             # 页面（按业务模块组织）
│   ├── components/        # 公共组件
│   ├── layouts/           # 布局
│   ├── router/            # 路由（动态权限路由 + Elegant Router 生成）
│   ├── store/             # Pinia 状态（auth / tab / theme …）
│   ├── service/           # 请求层 + API 封装（api/）
│   ├── locales/           # i18n 文案（langs/zh-cn.ts、en-us.ts）
│   ├── theme/             # 主题（含组件级主题配置）
│   ├── hooks/             # 组合式函数
│   ├── utils/             # 工具函数
│   ├── typings/           # 类型定义
│   └── ...
├── packages/              # monorepo 子包（@sa/*）
│   ├── axios/             #   请求封装
│   ├── alova/             #   alova 封装
│   ├── materials/         #   物料
│   ├── hooks/             #   通用 hooks
│   ├── color/  uno-preset/  utils/  scripts/
├── public/                # 静态资源
├── build/                 # 构建配置
├── index.html
├── vite.config.ts
├── uno.config.ts
└── package.json
```

## 与后端的集成要点

- **请求层**：`src/service/request/index.ts` 统一注入 `Authorization` 与 `Accept-Language`（取自 vue-i18n 当前 locale），后端按语言返回 `msg`，前端原样展示
- **响应契约**：统一结构 `{ code, msg, data, request_id, err_code }` + 分页 `{ records, page, page_size, total, total_pages }`；`status` 字段 `bool ↔ "1"/"2"` 桥接。详见 [`../aiDoc/frontend-backend/boundary.md`](../aiDoc/frontend-backend/boundary.md)
- **动态菜单 / 权限**：登录后拉取后端权限生成路由与菜单
- **国际化**：`src/locales/langs/` 维护中英文，新增 key 需同步 `zh-cn.ts` 与 `en-us.ts`

## 构建与部署

```bash
pnpm build         # 产物输出到 dist/
```

将 `dist/` 部署到 Nginx 等静态服务器，并配置反向代理将 API 请求转发到后端。

## 浏览器支持

推荐使用最新版 Chrome / Edge / Firefox 开发。

## 许可证

MIT，详见 [LICENSE](LICENSE)。前端基于 [SoybeanAdmin](https://github.com/soybeanjs/soybean-admin)（MIT © Soybean）二次开发，商业使用请保留作者版权信息。
