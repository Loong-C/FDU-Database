# Bookstore 后端 API 接口文档

## 1. 基本信息
- 技术栈：Python 3.12 + Django 5.2 + Django REST Framework 3.17
- 基础路径：`/api/v1`
- 数据库：MySQL 8.x
- 鉴权方式：JWT Bearer Token
- 返回格式：JSON

统一成功响应：

```json
{
  "code": 0,
  "message": "Success",
  "data": {}
}
```

统一错误响应：

```json
{
  "code": 422,
  "message": "Validation failed",
  "data": null,
  "errors": {
    "field": ["error message"]
  }
}
```

错误码约定：

| HTTP 状态 | 说明 |
|---|---|
| `400` | 请求格式错误 |
| `401` | 未登录或令牌无效 |
| `403` | 权限不足 |
| `404` | 资源不存在 |
| `409` | 业务冲突，例如存在关联数据无法删除 |
| `422` | 参数校验失败 |

## 2. 角色权限

| 角色 | 权限 |
|---|---|
| `admin` | 全量 CRUD、统计分析、用户管理 |
| `operator` | 可读基础资料，可维护客户/会员/销售 |
| `viewer` | 仅可访问 `auth/me` 和统计分析接口 |

## 3. 鉴权与账号接口

### `POST /api/v1/auth/login`
- 说明：用户登录，返回访问令牌与刷新令牌。
- 请求体：

```json
{
  "username": "admin",
  "password": "Admin123!"
}
```

### `POST /api/v1/auth/refresh`
- 说明：使用刷新令牌换取新的访问令牌和刷新令牌。
- 请求体：

```json
{
  "refresh_token": "..."
}
```

### `POST /api/v1/auth/logout`
- 说明：注销当前刷新令牌，需带访问令牌。
- 请求体：

```json
{
  "refresh_token": "..."
}
```

### `GET /api/v1/auth/me`
- 说明：返回当前登录用户信息。

### `GET /api/v1/users`
### `POST /api/v1/users`
### `PATCH /api/v1/users/{id}`
- 说明：用户管理接口，仅 `admin` 可用。

## 4. 主资源 CRUD

所有列表接口支持分页参数：
- `page`
- `page_size`

所有列表接口的分页返回结构：

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20
  }
}
```

### 4.1 门店 `stores`

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/v1/stores` | 门店列表 |
| `GET` | `/api/v1/stores/{id}` | 门店详情 |
| `POST` | `/api/v1/stores` | 新增门店 |
| `PATCH` | `/api/v1/stores/{id}` | 修改门店 |
| `DELETE` | `/api/v1/stores/{id}` | 删除门店 |

可选查询参数：
- `search`
- `city`

### 4.2 供应商 `suppliers`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/suppliers` |
| `GET` | `/api/v1/suppliers/{id}` |
| `POST` | `/api/v1/suppliers` |
| `PATCH` | `/api/v1/suppliers/{id}` |
| `DELETE` | `/api/v1/suppliers/{id}` |

可选查询参数：
- `search`
- `status`

### 4.3 分类 `categories`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/categories` |
| `GET` | `/api/v1/categories/{id}` |
| `POST` | `/api/v1/categories` |
| `PATCH` | `/api/v1/categories/{id}` |
| `DELETE` | `/api/v1/categories/{id}` |

### 4.4 出版社 `publishers`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/publishers` |
| `GET` | `/api/v1/publishers/{id}` |
| `POST` | `/api/v1/publishers` |
| `PATCH` | `/api/v1/publishers/{id}` |
| `DELETE` | `/api/v1/publishers/{id}` |

### 4.5 作者 `authors`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/authors` |
| `GET` | `/api/v1/authors/{id}` |
| `POST` | `/api/v1/authors` |
| `PATCH` | `/api/v1/authors/{id}` |
| `DELETE` | `/api/v1/authors/{id}` |

### 4.6 译者 `translators`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/translators` |
| `GET` | `/api/v1/translators/{id}` |
| `POST` | `/api/v1/translators` |
| `PATCH` | `/api/v1/translators/{id}` |
| `DELETE` | `/api/v1/translators/{id}` |

### 4.7 商品 `products`

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/v1/products` | 商品列表，返回 `is_book`、汇总 `stock_qty` 和门店库存 `inventory` |
| `GET` | `/api/v1/products/{id}` | 商品详情 |
| `POST` | `/api/v1/products` | 新增普通商品 |
| `PATCH` | `/api/v1/products/{id}` | 修改普通商品 |
| `DELETE` | `/api/v1/products/{id}` | 删除普通商品 |

可选查询参数：
- `search`
- `category_id`
- `status`

商品写入请求体：

```json
{
  "product_name": "金属书签",
  "category_id": 4,
  "unit": "个",
  "unit_price": "9.90",
  "cost_price": "4.20",
  "store_id": 1,
  "stock_qty": 120,
  "safety_stock_qty": 10,
  "barcode": "690123450099",
  "status": "onsale",
  "supplier_links": [
    {
      "supplier_id": 1,
      "supply_price": "3.80",
      "min_order_qty": 10,
      "is_primary": true
    }
  ]
}
```

说明：`product` 表不再保存库存；请求中的 `stock_qty` 会写入默认门店或指定 `store_id` 的 `inventory`。返回中的 `stock_qty` 是该商品所有门店库存汇总。

### 4.8 图书 `books`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/books` |
| `GET` | `/api/v1/books/{product_id}` |
| `POST` | `/api/v1/books` |
| `PATCH` | `/api/v1/books/{product_id}` |
| `DELETE` | `/api/v1/books/{product_id}` |

可选查询参数：
- `search`
- `publisher_id`
- `category_id`

图书写入请求体：

```json
{
  "product_name": "Python Web 开发实战",
  "category_id": 3,
  "unit": "本",
  "unit_price": "98.00",
  "cost_price": "66.00",
  "store_id": 1,
  "stock_qty": 40,
  "safety_stock_qty": 5,
  "barcode": "9787111000999",
  "status": "onsale",
  "supplier_links": [
    {
      "supplier_id": 2,
      "supply_price": "60.00",
      "min_order_qty": 5,
      "is_primary": true
    }
  ],
  "isbn": "9787111000999",
  "publisher_id": 1,
  "publish_date": "2024-03-01",
  "edition": "第1版",
  "language": "中文",
  "page_count": 388,
  "author_ids": [1],
  "translator_ids": [2]
}
```

### 4.9 客户 `customers`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/customers` |
| `GET` | `/api/v1/customers/{id}` |
| `POST` | `/api/v1/customers` |
| `PATCH` | `/api/v1/customers/{id}` |
| `DELETE` | `/api/v1/customers/{id}` |

可选查询参数：
- `search`
- `status`

### 4.10 会员 `members`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/members` |
| `GET` | `/api/v1/members/{customer_id}` |
| `POST` | `/api/v1/members` |
| `PATCH` | `/api/v1/members/{customer_id}` |
| `DELETE` | `/api/v1/members/{customer_id}` |

会员创建请求体：

```json
{
  "customer_id": 1,
  "member_no": "M20250003",
  "level": "silver",
  "points": 120,
  "join_date": "2026-04-01"
}
```

### 4.11 销售单 `sales`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/sales` |
| `GET` | `/api/v1/sales/{id}` |
| `POST` | `/api/v1/sales` |
| `PATCH` | `/api/v1/sales/{id}` |
| `DELETE` | `/api/v1/sales/{id}` |

可选查询参数：
- `store_id`
- `customer_id`
- `payment_method`
- `date_from`
- `date_to`

销售创建请求体：

```json
{
  "store_id": 1,
  "customer_id": 1,
  "sale_time": "2026-04-21T10:15:00+08:00",
  "payment_method": "wechat",
  "discount_amount": "5.00",
  "items": [
    {
      "product_id": 4,
      "quantity": 20
    },
    {
      "product_id": 5,
      "quantity": 1
    }
  ]
}
```

服务端自动计算：
- `unit_price`
- `line_amount`
- `total_amount`
- `actual_amount`

库存规则：服务端按 `store_id + product_id` 扣减 `inventory.stock_qty`；修改销售单会先归还旧门店库存，再按新门店和新明细重新扣减；删除销售单会回滚对应门店库存。

### 4.12 门店库存 `inventory`

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/v1/inventory` | 库存列表 |
| `GET` | `/api/v1/inventory/warnings` | 库存预警列表 |
| `GET` | `/api/v1/inventory/{store_id}/{product_id}` | 单个门店商品库存 |
| `PATCH` | `/api/v1/inventory/{store_id}/{product_id}` | 调整库存或安全库存 |

可选查询参数：`store_id`、`product_id`、`warning=true`。

### 4.13 采购单 `purchase-orders`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/purchase-orders` |
| `GET` | `/api/v1/purchase-orders/{id}` |
| `POST` | `/api/v1/purchase-orders` |
| `PATCH` | `/api/v1/purchase-orders/{id}` |
| `DELETE` | `/api/v1/purchase-orders/{id}` |

采购创建请求体：

```json
{
  "supplier_id": 2,
  "store_id": 1,
  "order_time": "2026-04-21T09:00:00+08:00",
  "status": "approved",
  "items": [
    {
      "product_id": 2,
      "quantity": 5,
      "purchase_price": "78.00"
    }
  ]
}
```

### 4.14 入库单 `stock-ins`

| 方法 | 路径 |
|---|---|
| `GET` | `/api/v1/stock-ins` |
| `GET` | `/api/v1/stock-ins/{id}` |
| `POST` | `/api/v1/stock-ins` |
| `PATCH` | `/api/v1/stock-ins/{id}` |
| `DELETE` | `/api/v1/stock-ins/{id}` |

当入库单状态为 `approved` 时，服务端会增加对应 `inventory.stock_qty`。

## 5. 统计分析接口

### `GET /api/v1/analytics/stores/daily`
- 参数：`store_id`、`date_from`、`date_to`
- 说明：按门店和日期汇总销售单数、原始总额、折扣额、实付额。

### `GET /api/v1/analytics/products/rank`
- 参数：`store_id`、`category_id`、`date_from`、`date_to`、`limit`
- 说明：按销量和销售额排行商品。

### `GET /api/v1/analytics/members/rank`
- 参数：`level`、`date_from`、`date_to`、`limit`
- 说明：查看会员消费排行。

### `GET /api/v1/analytics/categories/summary`
- 参数：`date_from`、`date_to`
- 说明：按商品分类汇总销量与销售额。

## 6. 业务规则说明

- 图书类商品必须使用 `books` 接口创建和维护，普通商品使用 `products`。
- 会员只能基于已存在客户创建。
- 删除门店、供应商、分类、出版社、作者、译者、商品、客户时，若存在关联业务数据会返回 `409`。
- 删除销售单时会自动回滚对应门店商品库存。
- 修改销售单时会先归还旧库存，再按新明细重新扣减门店库存。
- 入库单审核通过后会增加对应门店商品库存。
- 数据库设计层保留 `system_user`、`role`、`permission` 等 RBAC 表；当前后端运行时继续使用 Django 自定义用户、JWT 和 `role` 字段实现权限控制。

## 7. 演示账号

执行 `python manage.py seed_demo_users` 后，会生成以下账号：

| 用户名 | 密码 | 角色 |
|---|---|---|
| `admin` | `Admin123!` | 管理员 |
| `operator` | `Operator123!` | 操作员 |
| `viewer` | `Viewer123!` | 查询用户 |
