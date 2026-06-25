# 网上综合书店销售数据库系统

这是一个用于课程演示的网上综合书店销售数据库系统。项目围绕连锁书店的日常经营数据展开，提供门店、商品、图书、库存、客户、会员、销售、采购和数据分析等后台管理能力。

当前线上演示地址：

- https://linkukai.com/bookstore/
- https://www.linkukai.com/bookstore/

## 功能概览

- 登录与角色权限：管理员、操作员、查询用户三类演示角色。
- 门店管理：维护门店名称、城市、地址、电话、店长等信息。
- 商品与图书管理：维护商品基础信息、图书 ISBN、出版社、作者、译者、分类、供应商关系。
- 库存管理：按门店和商品查看库存、安全库存、低库存预警，并支持库存调整。
- 客户与会员管理：维护客户资料、会员等级、积分和会员编号。
- 销售管理：创建销售单、查看销售明细、统计订单与销售金额。
- 采购与入库：维护采购单、入库单及相关明细。
- 数据分析：查看门店销售趋势、热销商品排行、会员消费排行、分类销售占比和库存预警。

## 技术栈

前端：

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Element Plus
- Axios
- ECharts

后端：

- Python 3
- Django 5
- Django REST Framework
- PyMySQL
- JWT 登录认证
- Gunicorn

数据库与部署：

- MySQL 8
- Nginx
- Ubuntu 24.04 VPS
- Let's Encrypt HTTPS
- GitHub 协作

## 目录结构

```text
Bookstore/
├── backend/                 # Django 后端项目
│   ├── accounts/            # 登录、用户、JWT、演示账号
│   ├── analytics/           # 数据分析接口
│   ├── catalog/             # 商品、图书、分类、作者、出版社、供应商
│   ├── customers/           # 客户与会员
│   ├── inventory/           # 库存与库存预警
│   ├── procurement/         # 采购单与入库单
│   ├── sales/               # 销售单与销售明细
│   ├── stores/              # 门店
│   ├── common/              # 通用响应、分页、权限、异常处理
│   └── config/              # Django 配置与路由
├── frontend/                # Vue 前端项目
│   ├── src/api/             # 前端 API 封装
│   ├── src/components/      # 通用组件
│   ├── src/layouts/         # 页面布局
│   ├── src/router/          # 前端路由
│   ├── src/stores/          # Pinia 状态
│   └── src/views/           # 页面视图
├── sql/                     # 数据库建表脚本、视图脚本和 CSV 种子数据
│   ├── data/                # 可导入的业务演示数据
│   ├── tools/               # 数据生成与校验脚本
│   ├── create_database.sql
│   ├── create_tables.sql
│   └── views_or_reports.sql
└── docs/                    # 项目文档资料
```

## 演示账号

执行后端命令 `python manage.py seed_demo_users` 后会创建或更新以下账号：

| 用户名 | 密码 | 角色 |
| --- | --- | --- |
| `admin` | `Admin123!` | 管理员，可执行全部操作 |
| `operator` | `Operator123!` | 操作员，可维护客户、销售、采购等业务数据 |
| `viewer` | `Viewer123!` | 查询用户，仅可查看分析和基础数据 |

## 本地开发

### 1. 准备环境

建议版本：

- Python 3.12 或更新版本
- Node.js 22 或更新版本
- MySQL 8

### 2. 配置后端环境变量

复制示例文件：

```powershell
cd backend
copy .env.example .env
```

根据本机 MySQL 情况修改 `backend/.env`：

```env
DEBUG=True
SECRET_KEY=change-me-in-local-dev
ALLOWED_HOSTS=127.0.0.1,localhost

DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=online_bookstore_db
DB_USER=root
DB_PASSWORD=
DB_CHARSET=utf8mb4

JWT_SECRET_KEY=change-me-too
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7
```

### 3. 安装后端依赖并初始化数据库

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py bootstrap_business_db --seed --views
python manage.py migrate
python manage.py seed_demo_users
python manage.py runserver
```

说明：

- `bootstrap_business_db --seed --views` 会重建业务数据库、建表、导入 `sql/data` 中的 CSV 数据，并创建分析视图。
- `migrate` 会创建 Django 登录、权限、会话等框架表。
- `seed_demo_users` 会创建演示账号。

### 4. 安装前端依赖并启动开发服务

```powershell
cd frontend
npm ci
npm run dev
```

默认开发地址：

- 前端：http://127.0.0.1:5173
- 后端：http://127.0.0.1:8000

前端开发环境会通过 Vite 代理把 `/api` 请求转发到后端。

## 常用命令

前端：

```powershell
cd frontend
npm run dev
npm run build
npm run type-check
```

后端：

```powershell
cd backend
.\.venv\Scripts\activate
python manage.py check
python manage.py migrate
python manage.py seed_demo_users
python manage.py runserver
```

数据库数据重新生成与校验：

```powershell
python sql/tools/build_seed_data.py
python sql/tools/validate_seed_data.py
```

## 线上部署说明

当前生产部署方式：

- 代码目录：`/srv/bookstore`
- 后端服务：`bookstore.service`
- Web 服务器：Nginx
- 数据库：MySQL `online_bookstore_db`
- HTTPS：Let's Encrypt，证书自动续期
- 访问子路径：`/bookstore/`

前端生产环境配置位于 `frontend/.env.production`，其中：

```env
VITE_APP_BASE=/bookstore/
VITE_API_BASE=/bookstore/api/v1
```

这表示前端资源、前端路由和 API 请求都部署在域名的 `/bookstore/` 子路径下。

## GitHub 协作与线上更新

远端仓库：

```text
https://github.com/Loong-C/FDU-Database.git
```

推荐协作流程：

1. 本地修改代码。
2. 运行相关检查，例如 `npm run build`、`python manage.py check`。
3. 提交并推送到 GitHub。
4. 登录 VPS。
5. 执行一键更新脚本。

```bash
ssh root@187.77.136.20
deploy-bookstore
```

`deploy-bookstore` 会自动执行：

- 拉取 GitHub `main` 分支最新代码
- 安装或更新后端依赖
- 执行 Django migrations
- 刷新演示账号
- 收集后端静态文件
- 安装前端依赖
- 构建前端生产包
- 重启 Gunicorn 后端服务
- 检查并重载 Nginx

## 数据库注意事项

- `sql/data` 中的数据是课程演示数据，适合直接导入演示环境。
- `bootstrap_business_db --seed --views` 会重建业务数据库，请不要在有重要线上数据时随意执行。
- 普通代码更新通常只需要执行 `deploy-bookstore`，不需要重新导入全部 CSV。
- 如果修改了 Django 自有模型，需要提交 migration 文件并在部署时执行 `python manage.py migrate`。

## API 约定

后端统一返回结构：

```json
{
  "code": 0,
  "message": "OK",
  "data": {}
}
```

分页接口统一返回：

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

前端 API 封装位于 `frontend/src/api`，后端接口路由统一挂载在 `/api/v1/` 下。线上访问时由 Nginx 映射为 `/bookstore/api/v1/`。

## 项目定位

本项目主要用于数据库课程作业与演示，重点展示：

- 关系型数据库建模
- 多表业务数据管理
- 前后端分离开发
- 后台管理系统交互
- 基础权限控制
- 统计视图与可视化分析
- 从 GitHub 到 VPS 的部署与协作流程
