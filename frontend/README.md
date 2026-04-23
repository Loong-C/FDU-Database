# Bookstore 前端

基于 Vue 3 + TypeScript + Vite + Element Plus + Pinia + ECharts 构建的网上综合书店后台前端。

## 运行要求

- Node.js 20+
- 已启动后端（默认 `http://127.0.0.1:8000`）

## 启动开发服务器

```powershell
cd frontend
npm install
npm run dev
```

默认监听 `http://127.0.0.1:5173`，`/api/*` 自动代理到后端。

## 构建生产包

```powershell
npm run build
```

产物在 `dist/`，可托管到任意静态服务器。生产环境建议由反向代理把 `/api` 指向 Django 后端。

## 环境变量

- `VITE_API_BASE` ：后端 API 前缀，默认 `/api/v1`
- `VITE_API_PROXY_TARGET` ：开发期代理目标，默认 `http://127.0.0.1:8000`

## 演示账号

| 用户名 | 密码 | 角色 |
|---|---|---|
| `admin` | `Admin123!` | 管理员，所有模块可写 |
| `operator` | `Operator123!` | 操作员，可维护客户/会员/销售 |
| `viewer` | `Viewer123!` | 查询用户，仅数据分析 |

## 目录结构

```
src/
├── api/         所有后端接口封装（http.ts 为 axios + JWT 刷新队列）
├── components/  通用组件 + 图表组件
├── directives/  v-perm 权限指令
├── layouts/     主布局与空白布局
├── router/      路由与角色守卫
├── stores/      Pinia 状态（auth / ui / dicts）
├── styles/      全局 SCSS 与 Element 主题覆盖
├── utils/       格式化/下载/错误处理
└── views/       各业务页面
```
