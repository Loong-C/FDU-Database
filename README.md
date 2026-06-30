# 网上综合书店销售数据库系统

仓库地址：`https://github.com/Loong-C/FDU-Database.git`

线上系统已部署，可直接访问使用：

- `https://linkukai.com/bookstore/`
- `https://www.linkukai.com/bookstore/`

> 普通演示、验收和功能体验不需要在本机安装 Python、Node.js、MySQL，也不需要手动启动前端或后端。本文后续本地安装步骤主要用于开发、复现、测试或重新部署。

## 1. 项目简介

本项目是一个用于数据库课程作业与演示的网上综合书店销售数据库系统。系统围绕连锁书店的日常经营数据展开，提供门店、供应商、商品、图书、库存、客户、会员、销售、采购、入库、用户权限和数据分析等后台管理能力。

项目文档：

- Markdown 文档：`docs/项目文档.md`
- PDF 文档：`docs/项目文档.pdf`
- API 文档：`docs/api/API接口文档.md`
- 用户手册：`docs/用户手册.md`
- 测试记录：`docs/test/接口测试结果.md`

## 2. 功能概览

| 模块 | 功能 |
|---|---|
| 登录与权限 | JWT 登录、访问令牌刷新、管理员/操作员/查询用户三类角色 |
| 经营总览 | 今日销售额、订单数、会员消费、库存预警、近 7 日销售趋势、热销商品 |
| 统计分析 | 门店日报、商品排行、会员消费排行、分类销售汇总、CSV 导出 |
| 门店管理 | 维护门店名称、城市、地址、电话、店长等信息 |
| 供应商管理 | 维护供应商、联系人、电话、邮箱、合作状态 |
| 商品与图书 | 维护普通商品、图书 ISBN、出版社、作者、译者、分类、供货关系 |
| 库存管理 | 按门店和商品维护当前库存、安全库存、低库存预警 |
| 客户与会员 | 维护客户资料、会员编号、会员等级、积分和入会日期 |
| 销售管理 | 新开销售单、查看销售明细、服务端自动计算金额并扣减库存 |
| 采购与入库 | 创建采购单、入库单，入库审核通过后增加门店库存 |
| 用户管理 | 管理系统账号、角色、启停状态和密码 |

## 3. 技术栈

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
- Django 5.2
- Django REST Framework
- PyMySQL
- PyJWT
- Gunicorn

数据库与部署：

- MySQL 8
- Nginx
- Ubuntu VPS
- Let's Encrypt HTTPS
- GitHub 协作

## 4. 演示账号

线上系统和本地初始化后的演示账号一致：

| 用户名 | 密码 | 角色 | 权限说明 |
|---|---|---|---|
| `admin` | `Admin123!` | 管理员 | 可执行全部管理操作 |
| `operator` | `Operator123!` | 操作员 | 可维护客户、会员、销售、采购、入库等业务数据 |
| `viewer` | `Viewer123!` | 查询用户 | 可查看经营总览和统计分析 |

## 5. 线上使用说明

### 5.1 打开系统

浏览器访问：

```text
https://linkukai.com/bookstore/
```

备用地址：

```text
https://www.linkukai.com/bookstore/
```

### 5.2 登录与菜单

1. 使用演示账号登录。
2. 登录后系统按角色展示菜单。
3. 管理员可看到基础资料、商品中心、库存补货、客户会员、门店销售、采购入库、经营分析和系统权限。
4. 操作员主要用于销售、客户会员、采购入库等日常业务操作。
5. 查询用户主要用于查看经营总览和统计分析。

### 5.3 推荐功能验证流程

建议使用 `admin` 账号完成以下验收链路：

1. 进入“商品中心”或“图书档案”，新增普通商品或图书，设置门店初始库存和安全库存。
2. 进入“门店库存”，按门店和商品筛选，确认新增商品库存已写入。
3. 调整安全库存，使当前库存小于或等于安全库存，观察库存预警。
4. 进入“新开销售单”，选择门店，搜索商品，加入购物车并提交销售单。
5. 打开销售单详情，确认服务端自动计算原价、优惠和实付金额。
6. 回到“门店库存”，确认对应门店商品库存已扣减。
7. 进入“采购单”，为该商品创建采购记录。
8. 进入“入库单”，选择采购单，创建状态为“已审核”的入库单。
9. 再次查看“门店库存”和“经营总览”，确认库存增加、预警数量变化。
10. 进入“统计分析”，查看门店日报、商品排行、会员消费排行和分类销售汇总，并导出当前视图 CSV。

## 6. 本地开发安装与运行

本节用于本地开发、代码修改、问题复现和接口测试。只使用线上系统时可跳过。

### 6.1 环境要求

建议版本：

- Python 3.12 或更新版本
- Node.js 20+；推荐 Node.js 22 或更新版本
- MySQL 8
- Windows PowerShell 或等价终端

### 6.2 克隆项目

```powershell
git clone https://github.com/Loong-C/FDU-Database.git
cd FDU-Database
```

如果已经在当前工作区中，项目根目录为 `Bookstore/`。

### 6.3 创建后端虚拟环境

根目录脚本 `start-dev.cmd` 和 `start-backend.cmd` 期望虚拟环境位于仓库根目录 `.venv`，推荐：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

如果选择在 `backend/.venv` 下创建虚拟环境，也可以手动进入 `backend` 后运行 Django 命令，但根目录启动脚本不会自动使用 `backend/.venv`。

### 6.4 配置后端环境变量

```powershell
copy backend\.env.example backend\.env
```

按本机 MySQL 情况修改 `backend/.env`：

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

### 6.5 初始化本地数据库

确认 MySQL 服务已启动后执行：

```powershell
.\.venv\Scripts\python.exe backend\manage.py bootstrap_business_db --seed --views
.\.venv\Scripts\python.exe backend\manage.py migrate
.\.venv\Scripts\python.exe backend\manage.py seed_demo_users
```

说明：

- `bootstrap_business_db --seed --views` 会删除并重建 `online_bookstore_db`，创建业务表，导入 `sql/data` 中的 CSV 数据，并创建统计视图。
- `migrate` 会创建 Django 登录、权限、会话、刷新令牌等框架表。
- `seed_demo_users` 会创建或更新 `admin`、`operator`、`viewer` 三个演示账号。
- 该命令会重建数据库，不要在有重要数据的数据库或线上生产库上随意执行。

### 6.6 安装前端依赖

```powershell
cd frontend
npm ci
cd ..
```

### 6.7 启动本地开发服务

方式一：分别启动。

后端：

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

前端：

```powershell
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

开发地址：

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8000`

方式二：使用根目录脚本。

```powershell
.\start-dev.cmd
```

脚本会检查虚拟环境和前端依赖，并分别打开前端和后端窗口。

## 7. 测试与功能验证

### 7.1 后端配置检查

```powershell
.\.venv\Scripts\python.exe backend\manage.py check
```

### 7.2 后端接口集成测试

```powershell
.\.venv\Scripts\python.exe backend\manage.py test common
```

测试覆盖：

- 登录、刷新、登出、`auth/me`
- 管理员、操作员、查询用户权限矩阵
- 商品、图书、客户、会员创建和修改
- 销售单创建、修改、删除时库存扣减和回滚
- 采购单创建、入库单审核增加库存
- 库存预警接口
- 未来出版日期、缺失客户、关联删除等失败场景
- 门店、商品、会员、分类四组统计接口

### 7.3 Python 语法检查

```powershell
.\.venv\Scripts\python.exe -m compileall backend
```

### 7.4 前端类型检查与构建

```powershell
cd frontend
npm run type-check
npm run build
```

`npm run build` 会先执行 `vue-tsc --noEmit`，再执行 Vite 生产构建。

### 7.5 数据校验

```powershell
.\.venv\Scripts\python.exe sql\tools\validate_seed_data.py
```

如需从来源数据重新生成规范化 CSV：

```powershell
.\.venv\Scripts\python.exe sql\tools\build_seed_data.py
.\.venv\Scripts\python.exe sql\tools\validate_seed_data.py
```

### 7.6 手工功能验收

推荐先使用线上系统完成第 5.3 节的业务链路验证。若验证本地环境，则使用 `http://127.0.0.1:5173` 登录并执行相同流程。

## 8. 目录结构

```text
Bookstore/
├── backend/                 # Django 后端项目
│   ├── accounts/            # 登录、用户、JWT、演示账号
│   ├── analytics/           # 数据分析接口
│   ├── catalog/             # 商品、图书、分类、作者、译者、出版社、供应商
│   ├── common/              # 通用响应、分页、权限、异常、SQL 初始化、测试
│   ├── config/              # Django 配置与总路由
│   ├── customers/           # 客户与会员
│   ├── inventory/           # 门店库存与库存预警
│   ├── procurement/         # 采购单与入库单
│   ├── sales/               # 销售单与销售明细
│   └── stores/              # 门店
├── frontend/                # Vue 前端项目
│   ├── src/api/             # 前端 API 封装
│   ├── src/components/      # 通用组件与图表组件
│   ├── src/layouts/         # 页面布局
│   ├── src/router/          # 前端路由与角色守卫
│   ├── src/stores/          # Pinia 状态
│   ├── src/styles/          # 全局样式
│   ├── src/utils/           # 工具函数
│   └── src/views/           # 页面视图
├── sql/                     # 建库、建表、视图、CSV 数据和数据工具
│   ├── data/                # 实际导入的业务演示数据
│   ├── source/              # 来源数据
│   ├── tools/               # 数据生成、清洗、校验脚本
│   ├── create_database.sql
│   ├── create_tables.sql
│   └── views_or_reports.sql
├── docs/                    # 项目文档、API 文档、用户手册、测试记录
├── start-dev.cmd            # Windows 本地前后端启动脚本
├── start-backend.cmd
└── start-frontend.cmd
```

## 9. 数据库说明

当前数据库设计包含 25 张业务表：

- 门店：`store`
- 供应商：`supplier`、`supplier_product`
- 商品图书：`category`、`product`、`book`、`publisher`、`author`、`translator`、`book_author`、`book_translator`
- 客户会员：`customer`、`member`
- 销售：`sale`、`sale_item`
- 库存：`inventory`
- 采购入库：`purchase_order`、`purchase_order_item`、`stock_in`、`stock_in_item`
- 权限设计层：`system_user`、`role`、`permission`、`user_role`、`role_permission`

关键设计：

- `product` 是商品父表，不存门店库存。
- `book` 是图书子表，与 `product` 共享 `product_id` 主键。
- `inventory` 使用 `(store_id, product_id)` 复合主键维护门店库存。
- `sale_item` 保存成交单价快照；销售创建、修改、删除会同步维护库存。
- 入库单状态为 `approved` 时增加对应门店库存。

## 10. API 约定

后端基础路径：

```text
/api/v1
```

线上访问时由 Nginx 映射为：

```text
/bookstore/api/v1
```

统一成功响应：

```json
{
  "code": 0,
  "message": "Success",
  "data": {}
}
```

分页响应中的 `data`：

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

常见错误码：

| HTTP 状态 | 说明 |
|---|---|
| `401` | 未登录或令牌无效 |
| `403` | 权限不足 |
| `404` | 资源不存在 |
| `409` | 存在关联数据或业务冲突 |
| `422` | 参数校验失败 |

## 11. 线上部署与更新

当前 README 记录的生产部署方式：

- 代码目录：`/srv/bookstore`
- 后端服务：`bookstore.service`
- Web 服务器：Nginx
- 数据库：MySQL `online_bookstore_db`
- HTTPS：Let's Encrypt，证书自动续期
- 访问子路径：`/bookstore/`

前端生产环境配置位于 `frontend/.env.production`：

```env
VITE_APP_BASE=/bookstore/
VITE_API_BASE=/bookstore/api/v1
```

线上更新流程：

1. 本地修改代码或文档。
2. 运行必要检查，例如后端测试和前端构建。
3. 提交并推送到 GitHub。
4. 登录 VPS。
5. 执行部署脚本。

```bash
ssh root@187.77.136.20
deploy-bookstore
```

`deploy-bookstore` 会拉取 `main` 分支最新代码，安装或更新依赖，执行 Django migrations，刷新演示账号，收集静态文件，构建前端生产包，重启 Gunicorn 服务，并检查重载 Nginx。

## 12. 常见问题

### 12.1 是否必须本地安装才能使用系统？

不需要。系统已部署在 `https://linkukai.com/bookstore/`，普通使用和验收直接打开网站即可。

### 12.2 本地初始化报 `Unknown database 'online_bookstore_db'`

需要先执行业务库初始化，再执行 Django migration：

```powershell
.\.venv\Scripts\python.exe backend\manage.py bootstrap_business_db --seed --views
.\.venv\Scripts\python.exe backend\manage.py migrate
```

### 12.3 销售创建提示库存不足

销售扣减的是所选门店的 `inventory(store_id, product_id)` 库存，不是商品全局库存。请先检查该门店该商品的库存，或通过入库单增加库存。

### 12.4 删除数据返回 409

说明存在关联业务数据。比如供应商已关联商品、门店存在销售记录、出版社存在图书、商品存在销售明细等，系统会阻止直接删除。

## 13. 项目定位

本项目主要用于数据库课程作业与系统演示，重点展示：

- 关系型数据库建模
- 25 张业务表和统计视图设计
- 多表业务数据管理
- 前后端分离开发
- 后台管理系统交互
- JWT 登录与基础角色权限控制
- 事务性库存扣减与入库增加
- 统计分析与图表可视化
- 从 GitHub 到 VPS 的部署与协作流程
