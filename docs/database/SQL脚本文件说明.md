# SQL 脚本文件说明

> 适用项目：网上综合书店销售数据库项目  
> 适用数据库：MySQL 8.x
> 对齐来源：`pre/网上综合书店销售数据库_展示(6).pptx`

---

## 1. 文档目的

本文档说明 `sql/` 目录下各脚本的作用、执行顺序、验证方式和当前版本相对 PPTX 的对齐范围，便于组员协作、教师检查和后端初始化数据库。

---

## 2. 脚本文件组成

| 文件名 | 作用说明 |
|---|---|
| `create_database.sql` | 创建 `online_bookstore_db` 数据库 |
| `create_tables.sql` | 创建全部业务表及约束 |
| `insert_sample_data.sql` | 插入演示数据、权限样例、采购入库样例和库存样例 |
| `views_or_reports.sql` | 创建统计分析与库存预警视图 |

---

## 3. 执行顺序

1. `create_database.sql`
2. `create_tables.sql`
3. `insert_sample_data.sql`
4. `views_or_reports.sql`

执行顺序不可颠倒，否则可能出现数据库不存在、外键依赖缺失或视图来源表不存在等问题。

---

## 4. 脚本功能说明

### 4.1 `create_database.sql`

负责删除并重建项目数据库：

```sql
DROP DATABASE IF EXISTS online_bookstore_db;
CREATE DATABASE online_bookstore_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
```

### 4.2 `create_tables.sql`

负责创建 PPTX 中展示的 25 张表：

| 模块 | 表 |
|---|---|
| 核心业务 | `store`、`supplier`、`supplier_product`、`category`、`product`、`book`、`publisher`、`author`、`translator`、`book_author`、`book_translator`、`customer`、`member`、`sale`、`sale_item` |
| 权限控制 | `system_user`、`role`、`permission`、`user_role`、`role_permission` |
| 采购入库 | `purchase_order`、`purchase_order_item`、`stock_in`、`stock_in_item` |
| 门店库存 | `inventory` |

当前版本的重要设计点：

- `product` 不再保存 `stock_qty`。
- `inventory` 使用 `(store_id, product_id)` 作为复合主键。
- `sale_item` 与 `stock_in_item` 分别作为库存扣减和库存增加的业务来源。
- 权限、采购、入库、库存相关关系全部使用外键约束。

### 4.3 `insert_sample_data.sql`

插入覆盖主要业务链路的演示数据：

- 门店、供应商、分类、出版社、商品、图书、作者、译者；
- 客户、会员、销售主单、销售明细；
- `admin`、`operator`、`viewer` 三类权限样例；
- 采购单、采购明细、入库单、入库明细；
- 两个门店下的商品库存和安全库存。

### 4.4 `views_or_reports.sql`

创建以下统计视图：

| 视图 | 说明 |
|---|---|
| `v_store_sales_daily` | 门店日销售汇总 |
| `v_product_sales_rank` | 商品销量与销售额排行 |
| `v_member_spending_rank` | 会员消费排行 |
| `v_category_sales_summary` | 分类销售汇总 |
| `v_inventory_warning` | 门店库存预警 |
| `v_store_inventory_summary` | 门店库存汇总 |

---

## 5. 命令行执行方式

```bash
mysql -u root -p < sql/create_database.sql
mysql -u root -p < sql/create_tables.sql
mysql -u root -p < sql/insert_sample_data.sql
mysql -u root -p < sql/views_or_reports.sql
```

如果数据库端口或主机不是默认值，可追加 `-P` 和 `-h` 参数。

---

## 6. 执行后验证

### 6.1 验证表数量

```sql
USE online_bookstore_db;
SHOW TABLES;
```

应能看到 25 张基础表和 6 个视图。

### 6.2 验证核心表数据

```sql
SELECT 'store' AS table_name, COUNT(*) AS row_count FROM store
UNION ALL SELECT 'supplier', COUNT(*) FROM supplier
UNION ALL SELECT 'product', COUNT(*) FROM product
UNION ALL SELECT 'book', COUNT(*) FROM book
UNION ALL SELECT 'customer', COUNT(*) FROM customer
UNION ALL SELECT 'member', COUNT(*) FROM member
UNION ALL SELECT 'sale', COUNT(*) FROM sale
UNION ALL SELECT 'sale_item', COUNT(*) FROM sale_item
UNION ALL SELECT 'system_user', COUNT(*) FROM system_user
UNION ALL SELECT 'purchase_order', COUNT(*) FROM purchase_order
UNION ALL SELECT 'stock_in', COUNT(*) FROM stock_in
UNION ALL SELECT 'inventory', COUNT(*) FROM inventory;
```

### 6.3 验证统计视图

```sql
SELECT * FROM v_store_sales_daily;
SELECT * FROM v_product_sales_rank;
SELECT * FROM v_member_spending_rank;
SELECT * FROM v_category_sales_summary;
SELECT * FROM v_inventory_warning;
SELECT * FROM v_store_inventory_summary;
```

---

## 7. 常见问题

| 问题 | 处理方式 |
|---|---|
| `Unknown database` | 先执行 `create_database.sql` |
| 外键创建失败 | 确认整体执行 `create_tables.sql`，不要改变建表顺序 |
| 重复数据插入失败 | 重新执行 `create_database.sql` 后再按顺序执行全部脚本 |
| `CHECK` 不生效 | 建议使用 MySQL 8.0.16 及以上版本 |
| 后端仍引用 `product.stock_qty` | 后端需同步改为读取 `inventory.stock_qty` |

---

## 8. 小结

当前 SQL 脚本已经从原来的核心 15 表扩展为 PPTX 展示的 25 表设计，并将库存从商品基础表拆分为门店库存表。该版本可支撑后续后端按门店维度扣减库存、采购入库增加库存和库存预警查询。
