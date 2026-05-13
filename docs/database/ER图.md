# 网上综合书店销售数据库项目
## ER 图设计说明（与 PPTX 对齐版）

> 本文档用 Mermaid 拆分展示核心销售、商品图书、权限、采购入库与门店库存关系。
> 对齐来源：`pre/网上综合书店销售数据库_展示(6).pptx` 第 13-19、23-24 页。

---

## 1. 图例说明

- 实体：矩形节点
- 联系：带文字的连线
- 基数：使用 `1`、`N`、`0..1` 表达
- 中间表：用于把多对多关系转为两个一对多关系

---

## 2. 子图 A：销售业务主链路

```mermaid
flowchart LR
    STORE[Store 门店]
    CUSTOMER[Customer 客户]
    MEMBER[Member 会员]
    SALE[Sale 销售单]
    SALE_ITEM[Sale_Item 销售明细]
    PRODUCT[Product 商品]

    STORE -- "1 产生 N" --> SALE
    CUSTOMER -- "1 可下 N；销售可空支持散客" --> SALE
    CUSTOMER -- "1 升级 0..1" --> MEMBER
    SALE -- "1 包含 N" --> SALE_ITEM
    PRODUCT -- "1 出现在 N" --> SALE_ITEM
```

---

## 3. 子图 B：商品与图书域

```mermaid
flowchart LR
    CATEGORY[Category 商品分类]
    PRODUCT[Product 商品]
    BOOK[Book 图书]
    PUBLISHER[Publisher 出版社]
    AUTHOR[Author 作者]
    TRANSLATOR[Translator 译者]
    BOOK_AUTHOR[Book_Author]
    BOOK_TRANSLATOR[Book_Translator]

    CATEGORY -- "1 分类 N" --> PRODUCT
    PRODUCT -- "1 对 0..1" --> BOOK
    PUBLISHER -- "1 出版 N" --> BOOK
    BOOK -- "1" --> BOOK_AUTHOR
    AUTHOR -- "1" --> BOOK_AUTHOR
    BOOK -- "1" --> BOOK_TRANSLATOR
    TRANSLATOR -- "1" --> BOOK_TRANSLATOR
```

---

## 4. 子图 C：供应关系

```mermaid
flowchart LR
    SUPPLIER[Supplier 供应商]
    PRODUCT[Product 商品]
    SUPPLIER_PRODUCT[Supplier_Product 供货关系]

    SUPPLIER -- "1" --> SUPPLIER_PRODUCT
    PRODUCT -- "1" --> SUPPLIER_PRODUCT
    SUPPLIER_PRODUCT -- "记录 supply_price / min_order_qty / is_primary" --> PRODUCT
```

---

## 5. 子图 D：分类自关联

```mermaid
flowchart LR
    CATEGORY[Category]
    CATEGORY -- "parent_category_id 0..1" --> CATEGORY
```

---

## 6. 子图 E：库存 + 销售 + 采购

```mermaid
flowchart LR
    STORE[Store 门店]
    PRODUCT[Product 商品]
    INVENTORY[Inventory 门店库存]
    SALE[Sale 销售单]
    SALE_ITEM[Sale_Item 销售明细]
    SUPPLIER[Supplier 供应商]
    PURCHASE_ORDER[Purchase_Order 采购单]
    PURCHASE_ORDER_ITEM[Purchase_Order_Item 采购明细]
    STOCK_IN[Stock_In 入库单]
    STOCK_IN_ITEM[Stock_In_Item 入库明细]

    STORE -- "1" --> INVENTORY
    PRODUCT -- "1" --> INVENTORY
    STORE -- "1" --> SALE
    SALE -- "1" --> SALE_ITEM
    SALE_ITEM -- "扣减 store_id + product_id 库存" --> INVENTORY
    SUPPLIER -- "1" --> PURCHASE_ORDER
    STORE -- "1" --> PURCHASE_ORDER
    PURCHASE_ORDER -- "1" --> PURCHASE_ORDER_ITEM
    PURCHASE_ORDER -- "1 到 0..N" --> STOCK_IN
    STOCK_IN -- "1" --> STOCK_IN_ITEM
    STOCK_IN_ITEM -- "增加 store_id + product_id 库存" --> INVENTORY
```

---

## 7. 子图 F：权限控制

```mermaid
flowchart LR
    SYSTEM_USER[System_User 用户]
    ROLE[Role 角色]
    PERMISSION[Permission 权限点]
    USER_ROLE[User_Role]
    ROLE_PERMISSION[Role_Permission]

    SYSTEM_USER -- "1" --> USER_ROLE
    ROLE -- "1" --> USER_ROLE
    ROLE -- "1" --> ROLE_PERMISSION
    PERMISSION -- "1" --> ROLE_PERMISSION
```

---

## 8. 关键设计说明

- `Product` 只保存商品通用信息，库存移动到 `Inventory`。
- `Inventory` 的主键为 `(store_id, product_id)`，支持连锁门店各自维护库存和安全库存。
- `Purchase_Order` 表示向供应商下单，`Stock_In` 表示到货验收；二者分离以保留采购和入库过程。
- `Sale_Item` 不直接存库存结果，只作为库存扣减来源；实际库存状态由 `Inventory` 保存。
- `System_User`、`Role`、`Permission` 与两个中间表组成数据库层面的 RBAC 模型。
