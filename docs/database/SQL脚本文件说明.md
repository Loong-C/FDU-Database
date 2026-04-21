# SQL 脚本文件说明
> 适用项目：网上综合书店销售数据库项目  
> 适用阶段：第 2 阶段（SQL 脚本实现）  
> 适用数据库：MySQL 8.x
---
## 1. 文档目的
本文档用于说明项目中各 SQL 脚本文件的作用、执行顺序、使用方法以及验证方式，便于组员协作、教师检查和后续系统开发。
---
## 2. 脚本文件组成
本项目当前包含以下 SQL 脚本文件：
| 文件名 | 作用说明 |
|---|---|
| `create_database.sql` | 创建项目数据库 |
| `create_tables.sql` | 创建项目所需的全部数据表及约束 |
| `insert_sample_data.sql` | 插入测试数据与演示数据 |
| `views_or_reports.sql` | 创建统计视图与基础报表查询对象 |
---
## 3. 各脚本功能说明
### 3.1 `create_database.sql`
该脚本用于创建数据库本身，是所有后续脚本执行的前提。
主要功能包括：
- 删除已有同名数据库（如存在）
- 创建新的项目数据库
- 设置数据库字符集与排序规则
示例：
```sql
DROP DATABASE IF EXISTS online_bookstore_db;
CREATE DATABASE online_bookstore_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
```
---
### 3.2 `create_tables.sql`
该脚本用于创建数据库中的全部表结构，是项目数据库设计的核心部分。
主要功能包括：
- 创建门店、供应商、分类、商品、图书、出版社、客户、会员、销售等核心表
- 创建多对多关系中间表
- 添加主键、外键、唯一约束、非空约束、检查约束
- 保证表之间的引用完整性
该脚本执行完成后，数据库结构应与前期需求分析、ER 图和表结构草案保持一致。
---
### 3.3 `insert_sample_data.sql`
该脚本用于向数据库中插入测试数据与演示数据。
主要作用包括：
- 验证表结构是否可正常插入数据
- 为后续页面开发提供基础测试数据
- 为统计视图与查询语句提供样例支撑
测试数据通常覆盖以下内容：
- 门店数据
- 供应商数据
- 商品与图书数据
- 客户与会员数据
- 销售主单与销售明细数据
---
### 3.4 `views_or_reports.sql`
该脚本用于创建统计分析所需的视图或报表查询。
主要作用包括：
- 汇总门店销售情况
- 统计商品销量与销售额
- 查看会员消费排行
- 统计分类销售表现
该脚本可为项目后续的数据分析页面、教师验收展示和演示 PPT 提供支持。
---
## 4. 推荐执行顺序
所有脚本应按以下顺序执行：
1. `create_database.sql`
2. `create_tables.sql`
3. `insert_sample_data.sql`
4. `views_or_reports.sql`
执行顺序不可颠倒，否则可能出现数据库不存在、表不存在、外键创建失败等问题。
---
## 5. 执行方式
### 5.1 命令行执行方式
如果使用 MySQL 命令行工具，可按以下方式依次执行：
```bash
mysql -u root -p < create_database.sql
mysql -u root -p < create_tables.sql
mysql -u root -p < insert_sample_data.sql
mysql -u root -p < views_or_reports.sql
```
> 如果数据库端口不是默认值，可增加 `-P 端口号`。  
> 如果数据库不在本机，可增加 `-h 主机地址`。
### 5.2 图形化工具执行方式
如果使用 Navicat、DataGrip、MySQL Workbench 等工具，可按以下步骤执行：
- 连接到 MySQL 8 数据库实例
- 按顺序打开各 SQL 文件
- 依次运行脚本
- 检查执行结果中是否存在报错信息
- 刷新数据库对象列表，确认表和视图已成功生成
---
## 6. 执行后验证方式
脚本执行完成后，建议从以下几个方面进行验证。
### 6.1 验证表是否创建成功
```sql
USE online_bookstore_db;
SHOW TABLES;
```
### 6.2 验证核心表是否已插入数据
```sql
SELECT 'store' AS table_name, COUNT(*) AS row_count FROM store
UNION ALL
SELECT 'supplier', COUNT(*) FROM supplier
UNION ALL
SELECT 'category', COUNT(*) FROM category
UNION ALL
SELECT 'product', COUNT(*) FROM product
UNION ALL
SELECT 'book', COUNT(*) FROM book
UNION ALL
SELECT 'customer', COUNT(*) FROM customer
UNION ALL
SELECT 'member', COUNT(*) FROM member
UNION ALL
SELECT 'sale', COUNT(*) FROM sale
UNION ALL
SELECT 'sale_item', COUNT(*) FROM sale_item;
```
### 6.3 验证统计视图是否可正常查询
```sql
SELECT * FROM v_store_sales_daily;
SELECT * FROM v_product_sales_rank;
SELECT * FROM v_member_spending_rank;
SELECT * FROM v_category_sales_summary;
```
---
## 7. 常见问题说明
### 7.1 数据库不存在
如果执行建表脚本时报错 `Unknown database`，通常说明还没有先执行 `create_database.sql`。
处理方式：
- 先执行 `create_database.sql`
- 再执行后续脚本
### 7.2 外键创建失败
如果建表过程中出现外键相关报错，通常有以下原因：
- 表创建顺序不正确
- 被引用表尚未创建
- 字段类型不一致
处理方式：
- 使用已整理好的 `create_tables.sql`
- 按顺序整体执行，不要随意拆分
### 7.3 重复插入数据
如果重复执行测试数据脚本，可能出现 `Duplicate entry` 错误。
处理方式：
- 重新执行 `create_database.sql` 重建数据库
- 再依次执行全部脚本
### 7.4 检查约束异常
如果发现 `CHECK` 约束未正常生效，通常与 MySQL 版本有关。
处理方式：
- 建议使用 MySQL 8.0.16 及以上版本
- 若版本较低，可考虑使用触发器进行补充校验
---
## 8. 建议的项目目录结构
为便于 GitHub 协作，建议采用如下目录结构：
```text
sql/
  create_database.sql
  create_tables.sql
  insert_sample_data.sql
  views_or_reports.sql
docs/
  需求分析.md
  ER图设计说明.md
  表结构草案.md
  SQL脚本文件说明.md
README.md
```
---
## 9. 小结
本项目的 SQL 脚本文件已经覆盖数据库创建、表结构落地、测试数据插入与统计视图构建等主要内容。  
通过这些脚本，可以将第一阶段的需求分析、ER 设计和表结构草案进一步转化为可执行、可验证、可演示的数据库实现成果。
