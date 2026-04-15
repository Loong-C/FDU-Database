## 1. ER 设计目标
本次 ER 设计围绕“网上综合书店销售”核心业务，确保模型具备：
- **业务完整性**：覆盖门店、商品、图书、供应链、客户会员、销售全过程；
- **结构规范性**：满足第三范式（3NF）导向，减少冗余；
- **可实现性**：可直接映射到关系型数据库表结构；
- **可扩展性**：支持后续增加库存、促销、退货等模块。
---
## 2. 实体清单（用于 ER 图）
### 2.1 主实体
| 实体名 | 中文含义 | 说明 |
|---|---|---|
| `Store` | 门店 | 销售发生地点 |
| `Supplier` | 供应商 | 商品供货主体 |
| `Category` | 商品分类 | 商品归类 |
| `Product` | 商品 | 所有可销售商品的父实体 |
| `Book` | 图书 | `Product` 子实体 |
| `Publisher` | 出版社 | 图书出版主体 |
| `Customer` | 客户 | 购买行为主体 |
| `Member` | 会员 | `Customer` 子实体 |
| `Sale` | 销售单 | 交易主表 |
| `Sale_Item` | 销售明细 | 交易明细表 |
| `Author` | 作者 | 图书作者 |
| `Translator` | 译者 | 图书译者 |
### 2.2 关系实体（中间表）
| 实体名 | 用途 | 关联对象 |
|---|---|---|
| `Supplier_Product` | 供货关系 | `Supplier` ↔ `Product` |
| `Book_Author` | 作者关系 | `Book` ↔ `Author` |
| `Book_Translator` | 译者关系 | `Book` ↔ `Translator` |
---
## 3. 实体关系与基数说明
### 3.1 核心关系表
| 关系 | 基数 | 含义 |
|---|---|---|
| `Store` -> `Sale` | 1 : N | 一个门店可产生多笔销售 |
| `Customer` -> `Sale` | 1 : N（可空） | 一个客户可有多笔销售，销售可支持散客 |
| `Sale` -> `Sale_Item` | 1 : N | 一笔销售由多条明细组成 |
| `Product` -> `Sale_Item` | 1 : N | 一个商品可出现在多条销售明细中 |
| `Category` -> `Product` | 1 : N | 一个分类包含多个商品 |
| `Supplier` <-> `Product` | N : N | 一个供应商供多个商品，一个商品可多供应商供货 |
| `Product` -> `Book` | 1 : 0..1 | 仅图书类商品在 `Book` 中有记录 |
| `Publisher` -> `Book` | 1 : N | 一个出版社可对应多本图书 |
| `Book` <-> `Author` | N : N | 一本书可有多位作者 |
| `Book` <-> `Translator` | N : N | 一本书可有多位译者（也可无译者） |
| `Customer` -> `Member` | 1 : 0..1 | 客户可升级为会员 |
---
## 4. 子类实体建模说明
### 4.1 `Product` 与 `Book`
- `Book` 采用 `Product` 的子类模型（1:1，主键继承）。
- 原因：只有图书有 ISBN、出版社、页数等字段，拆分后避免在 `Product` 中出现大量空字段。
### 4.2 `Customer` 与 `Member`
- `Member` 采用 `Customer` 子类模型（1:1，可选）。
- 原因：会员一定是客户，但客户不一定是会员，分离后结构更清晰。
---
## 5. 多对多关系建模说明
### 5.1 供应商与商品：`Supplier_Product`
除外键外，关系本身还携带业务属性：
- `supply_price`（供货价）
- `min_order_qty`（最小起订量）
- `is_primary`（是否主供）
> 结论：必须独立为中间实体，不能简单用数组或重复字段表示。
### 5.2 图书与作者/译者：`Book_Author`、`Book_Translator`
- 一本书常有多作者、多译者；
- 一位作者/译者也可参与多本图书；
- 可在中间表扩展排序字段（如 `author_order`）。
---
## 6. ER 图绘制建议（展示规范）
为保证课程答辩可读性，建议 ER 图遵循以下规范：
- 主实体与中间实体视觉区分（颜色或分区）；
- 子类关系明确标注（`Product`-`Book`、`Customer`-`Member`）；
- 每条关系标注基数（1、N、0..1）；
- 仅展示核心属性（主键/外键/业务关键字段），避免图面过密；
- 图右下角加图例（PK、FK、UK 含义）。
---
## 7. Mermaid 版 ER 图（可直接粘贴到 Markdown）
```mermaid
erDiagram
    STORE ||--o{ SALE : has
    CUSTOMER ||--o{ SALE : places
    SALE ||--|{ SALE_ITEM : contains
    PRODUCT ||--o{ SALE_ITEM : appears_in
    CATEGORY ||--o{ PRODUCT : classifies
    SUPPLIER ||--o{ SUPPLIER_PRODUCT : supplies
    PRODUCT ||--o{ SUPPLIER_PRODUCT : sourced_by
    PRODUCT ||--o| BOOK : extends
    PUBLISHER ||--o{ BOOK : publishes
    BOOK ||--o{ BOOK_AUTHOR : has
    AUTHOR ||--o{ BOOK_AUTHOR : writes
    BOOK ||--o{ BOOK_TRANSLATOR : has
    TRANSLATOR ||--o{ BOOK_TRANSLATOR : translates
    CUSTOMER ||--o| MEMBER : upgrades_to
