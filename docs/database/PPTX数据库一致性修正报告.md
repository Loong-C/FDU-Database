# PPTX 数据库一致性修正报告

> 对比来源：`pre/网上综合书店销售数据库_展示(6).pptx`  
> 对比范围：`sql/`、`docs/database/` 以及后续后端数据库访问约定。

---

## 1. 检查结论

原仓库数据库材料与 PPTX 的核心 15 张业务表基本一致，但 PPTX 第 21、23、24、42-51 页还包含权限控制、采购入库和门店库存设计。原仓库缺少这 10 张表，并且库存位置与 PPTX 不一致：原仓库使用 `product.stock_qty`，PPTX 使用 `inventory(store_id, product_id, stock_qty, safety_stock_qty, updated_at)`。

本次修正后，SQL 和数据库文档已统一到 PPTX 展示的 25 张表设计。

---

## 2. 原仓库缺失内容

| PPTX 内容 | 原仓库状态 | 修正方式 |
|---|---|---|
| `system_user` | 缺失 | 新增 SQL 表结构与样例数据 |
| `role` | 缺失 | 新增 SQL 表结构与 `admin/operator/viewer` 样例 |
| `permission` | 缺失 | 新增权限点表和样例权限 |
| `user_role` | 缺失 | 新增用户角色中间表 |
| `role_permission` | 缺失 | 新增角色权限中间表 |
| `purchase_order` | 缺失 | 新增采购单表 |
| `purchase_order_item` | 缺失 | 新增采购明细表 |
| `stock_in` | 缺失 | 新增入库单表 |
| `stock_in_item` | 缺失 | 新增入库明细表 |
| `inventory` | 缺失 | 新增门店库存表和库存预警视图 |

---

## 3. 原仓库不符内容

### 3.1 库存字段位置不符

- 原仓库：`product.stock_qty`
- PPTX：`inventory.stock_qty`
- 修正：从 SQL 与文档中移除 `product.stock_qty`，新增 `inventory` 表，库存以 `(store_id, product_id)` 为唯一定位。

### 3.2 统计视图缺少库存预警

- 原仓库：仅包含门店日销售、商品排行、会员消费排行、分类销售汇总。
- PPTX：统计分析包括库存预警。
- 修正：新增 `v_inventory_warning` 和 `v_store_inventory_summary`。

### 3.3 文档范围小于 PPTX

- 原仓库数据库文档主要描述核心 15 表。
- PPTX 附录展示 25 表。
- 修正：重写需求分析、ER 图、表结构草案和 SQL 脚本说明，补充权限、采购、入库和门店库存。

---

## 4. 修正文件清单

| 文件 | 修正内容 |
|---|---|
| `sql/create_tables.sql` | 扩展到 25 张表，库存迁移到 `inventory` |
| `sql/insert_sample_data.sql` | 补充权限、采购入库、门店库存样例数据 |
| `sql/views_or_reports.sql` | 新增库存预警和库存汇总视图 |
| `docs/database/需求分析.md` | 补充业务范围、实体、关系、规则 |
| `docs/database/ER图.md` | 补充权限、采购、库存关系图 |
| `docs/database/表结构草案.md` | 按 25 张表更新结构说明 |
| `docs/database/SQL脚本文件说明.md` | 更新脚本说明、验证方式和常见问题 |
| `docs/database/相关说明.md` | 记录本次数据库文档修正摘要 |
| `pre/网上综合书店销售数据库_展示(6).pptx` | 纳入版本控制，作为修正依据 |

---

## 5. 后端衔接说明

数据库层已按 PPTX 补齐 RBAC 物理表，但后端当前使用 Django 自定义用户、JWT 和 `role` 字段实现运行时权限。后端适配时保持现有认证方式不破坏，同时在接口和文档中说明其与 PPTX 权限表设计的对应关系：

- `accounts.User.role = admin/operator/viewer` 对应 PPTX 的 `role.role_name`。
- 现有 DRF 权限类对应 `permission` 与 `role_permission` 的运行时简化实现。
- 业务 SQL 仍保留 PPTX 的权限表，满足数据库设计展示与审查要求。

---

## 6. 验证建议

1. 按顺序执行 `create_database.sql`、`create_tables.sql`、`insert_sample_data.sql`、`views_or_reports.sql`。
2. 使用 `SHOW TABLES;` 确认 25 张基础表已创建。
3. 查询 `inventory` 确认库存按门店和商品组合保存。
4. 查询 `v_inventory_warning` 确认低库存预警可用。
5. 后端适配后运行自动化测试，确认销售扣减和入库增加均作用于 `inventory`。

---

## 7. 结论

本次修正已解决仓库数据库材料与 PPTX 相比的缺失和不符问题。数据库设计已从“核心销售模型”扩展为“权限控制 + 采购入库 + 门店库存 + 销售统计”的完整展示版本。
