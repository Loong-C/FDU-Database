# 网上综合书店销售数据库项目  
## 第一阶段：ER 图（标准表达 + 分子图）
> 说明：本版 ER 图已结合最新需求分析结果更新，采用“实体-属性-联系”表达；  
> 通过多个子图拆分展示，便于后续表设计与答辩讲解。
---
## 1. 图例说明（统一规范）
- **实体（Entity）**：矩形框  
- **属性（Attribute）**：椭圆（本图用圆角节点近似）  
- **联系（Relationship）**：菱形  
- **基数（Cardinality）**：连线旁标注 `1`、`N`、`0..1`
---
## 2. 子图 A：门店、客户、会员、销售
```mermaid
flowchart LR
    %% 实体
    STORE[Store]
    CUSTOMER[Customer]
    MEMBER[Member]
    SALE[Sale]
    SALE_ITEM[Sale_Item]
    PRODUCT[Product]
    %% 联系（菱形）
    R1{发生于}
    R2{下单}
    R3{包含}
    R4{购买}
    R5{升级为}
    %% 关系
    STORE -- "1" --> R1
    R1 -- "N" --> SALE
    CUSTOMER -- "1" --> R2
    R2 -- "N" --> SALE
    SALE -- "1" --> R3
    R3 -- "N" --> SALE_ITEM
    PRODUCT -- "1" --> R4
    R4 -- "N" --> SALE_ITEM
    CUSTOMER -- "1" --> R5
    R5 -- "0..1" --> MEMBER
    %% 属性（椭圆近似）
    store_name([store_name])
    city([city])
    address_store([address])
    phone_store([phone])
    manager_name([manager_name])
    customer_name([customer_name])
    phone_customer([phone])
    email_customer([email])
    address_customer([address])
    member_no([member_no])
    level([level])
    points([points])
    sale_time([sale_time])
    payment_method([payment_method])
    actual_amount([actual_amount])
    quantity([quantity])
    unit_price_snapshot([unit_price])
    line_amount([line_amount])
    STORE --- store_name
    STORE --- city
    STORE --- address_store
    STORE --- phone_store
    STORE --- manager_name
    CUSTOMER --- customer_name
    CUSTOMER --- phone_customer
    CUSTOMER --- email_customer
    CUSTOMER --- address_customer
    MEMBER --- member_no
    MEMBER --- level
    MEMBER --- points
    SALE --- sale_time
    SALE --- payment_method
    SALE --- actual_amount
    SALE_ITEM --- quantity
    SALE_ITEM --- unit_price_snapshot
    SALE_ITEM --- line_amount
