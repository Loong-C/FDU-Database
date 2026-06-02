# SQL 与 CSV 初始化说明

> 适用数据库：MySQL 8.x

## 1. 目录结构

| 路径 | 作用 |
|---|---|
| `sql/create_database.sql` | 删除并重建 `online_bookstore_db` |
| `sql/create_tables.sql` | 创建 25 张业务表及约束 |
| `sql/views_or_reports.sql` | 创建 6 个统计分析视图 |
| `sql/data/*.csv` | 后端初始化时实际导入的演示数据，每张表一个同名 CSV |
| `sql/source/` | 抓取数据和合并前模拟 CSV 的来源备份 |
| `sql/tools/build_seed_data.py` | 从来源备份重新生成规范化 CSV |
| `sql/tools/validate_seed_data.py` | 校验主键、外键、金额和数据量 |

数据内容统一维护在 CSV 中，不再维护重复的 `INSERT` SQL。

## 2. 初始化方式

在仓库根目录准备虚拟环境和 `backend/.env` 后执行：

```powershell
cd backend
..\.venv\Scripts\python manage.py bootstrap_business_db --seed --views
..\.venv\Scripts\python manage.py migrate
..\.venv\Scripts\python manage.py seed_demo_users
```

`bootstrap_business_db` 会依次：

1. 执行 `create_database.sql`。
2. 执行 `create_tables.sql`。
3. 按外键依赖顺序导入 `sql/data/*.csv`。
4. 在指定 `--views` 时执行 `views_or_reports.sql`。

## 3. CSV 维护规则

- 每张业务表对应一个同名 CSV，例如 `product.csv`、`sale_item.csv`。
- 表头必须与 `backend/common/sql.py` 中的 `CSV_SEED_FILES` 完全一致。
- 空字符串会作为 SQL `NULL` 导入。
- 修改主表 ID 时，需要同步修改引用它的关联表和明细表。
- 修改销售或采购明细时，需要同步检查主单金额。

需要从保留的来源数据重新生成并校验整套 CSV 时执行：

```powershell
python sql/tools/build_seed_data.py
python sql/tools/validate_seed_data.py
```

## 4. 当前数据规模

规范化 CSV 当前包含 25 张业务表、933 行初始化数据，其中包括：

| 表 | 行数 |
|---|---:|
| `product` | 119 |
| `book` | 117 |
| `author` | 158 |
| `publisher` | 97 |
| `supplier` | 7 |
| `customer` | 15 |
| `sale` | 15 |
| `sale_item` | 31 |
| `inventory` | 58 |
| `purchase_order` | 6 |
| `stock_in` | 5 |

## 5. 视图

初始化可创建以下统计视图：

- `v_store_sales_daily`
- `v_product_sales_rank`
- `v_member_spending_rank`
- `v_category_sales_summary`
- `v_inventory_warning`
- `v_store_inventory_summary`
