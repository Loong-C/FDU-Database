USE online_bookstore_db;

-- 门店
INSERT INTO store (store_name, city, address, phone, manager_name) VALUES
('北京朝阳店', '北京', '朝阳区建国路88号', '010-88880001', '王丽'),
('上海浦东店', '上海', '浦东新区世纪大道200号', '021-88880002', '张强');

-- 供应商
INSERT INTO supplier (supplier_name, contact_name, phone, email, status) VALUES
('华北图书供应链', '刘洋', '010-60010001', 'hb_supplier@example.com', 'active'),
('华东文化供货商', '陈晨', '021-60020002', 'hd_supplier@example.com', 'active'),
('旧版图书清仓商', '赵宁', '0755-60030003', 'oldbooks@example.com', 'inactive');

-- 分类
INSERT INTO category (category_name, parent_category_id) VALUES
('图书', NULL),            -- id=1
('文学', 1),               -- id=2
('计算机', 1),             -- id=3
('文具', NULL);            -- id=4

-- 出版社
INSERT INTO publisher (publisher_name, contact_name, phone, email, address, country, website) VALUES
('人民邮电出版社', '李编辑', '010-12340001', 'contact@ptpress.com.cn', '北京市丰台区A路1号', '中国', 'https://www.ptpress.com.cn'),
('机械工业出版社', '王编辑', '010-12340002', 'contact@cmpbook.com', '北京市西城区B路2号', '中国', 'https://www.cmpbook.com'),
('译林出版社', '周编辑', '025-12340003', 'contact@yilinpress.com', '南京市鼓楼区C路3号', '中国', 'https://www.yilinpress.com');

-- 商品（库存已迁移到 inventory）
INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, barcode, status) VALUES
('数据库系统概论（第6版）', 3, '本', 88.00, 55.00, '9787111000001', 'onsale'), -- id=1
('深入理解计算机系统',       3, '本', 129.00, 80.00, '9787111000002', 'onsale'), -- id=2
('百年孤独',                 2, '本', 59.00, 35.00, '9787111000003', 'onsale'), -- id=3
('黑色中性笔',               4, '支', 3.50, 1.20, '690123450001',  'onsale'), -- id=4
('A4笔记本',                 4, '本', 12.00, 6.00, '690123450002',  'offsale'); -- id=5

-- 图书子表（仅商品1~3）
INSERT INTO book (product_id, isbn, publisher_id, publish_date, edition, language, page_count) VALUES
(1, '9787111000001', 1, '2023-08-01', '第6版', '中文', 420),
(2, '9787111000002', 2, '2022-05-15', '第1版', '中文', 720),
(3, '9787111000003', 3, '2021-11-20', '第1版', '中文', 360);

-- 作者
INSERT INTO author (author_name, country) VALUES
('王珊', '中国'),
('托马斯·科尔曼', '美国'),
('加西亚·马尔克斯', '哥伦比亚');

-- 译者
INSERT INTO translator (translator_name, country) VALUES
('裴小龙', '中国'),
('范晔', '中国');

-- 图书-作者
INSERT INTO book_author (product_id, author_id, author_order) VALUES
(1, 1, 1),
(2, 2, 1),
(3, 3, 1);

-- 图书-译者
INSERT INTO book_translator (product_id, translator_id) VALUES
(2, 1),
(3, 2);

-- 供应关系
INSERT INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary) VALUES
(1, 1, 54.00, 20, TRUE),
(1, 4, 1.10, 100, TRUE),
(2, 2, 78.00, 15, TRUE),
(2, 3, 33.00, 30, TRUE),
(2, 5, 5.50, 80, FALSE),
(3, 3, 25.00, 100, FALSE);

-- 客户
INSERT INTO customer (customer_name, phone, email, address, register_time, status) VALUES
('李明', '13800000001', 'liming@example.com', '北京市海淀区学院路1号', '2025-10-01 10:00:00', 'active'),
('韩梅梅', '13800000002', 'hanmeimei@example.com', '上海市浦东新区花木路8号', '2025-10-03 15:30:00', 'active'),
('Tom', '13800000003', 'tom@example.com', '北京市朝阳区望京路9号', '2025-11-10 09:20:00', 'inactive');

-- 会员（客户1、2）
INSERT INTO member (customer_id, member_no, level, points, join_date) VALUES
(1, 'M20250001', 'gold', 1200, '2025-10-02'),
(2, 'M20250002', 'silver', 450, '2025-10-04');

-- 权限控制样例
INSERT INTO system_user (username, password_hash, real_name, phone, email, status) VALUES
('admin', 'pbkdf2_sha256$demo$admin', '系统管理员', '13900000001', 'admin@example.com', 'active'),
('operator', 'pbkdf2_sha256$demo$operator', '门店操作员', '13900000002', 'operator@example.com', 'active'),
('viewer', 'pbkdf2_sha256$demo$viewer', '查询用户', '13900000003', 'viewer@example.com', 'active');

INSERT INTO role (role_name, role_desc) VALUES
('admin', '全局维护与审核'),
('operator', '门店销售、客户维护、采购入库操作'),
('viewer', '只读统计分析');

INSERT INTO permission (permission_code, permission_name, module_name) VALUES
('store.manage', '门店维护', 'store'),
('catalog.manage', '商品与图书维护', 'catalog'),
('customer.manage', '客户会员维护', 'customer'),
('sale.write', '销售录入', 'sale'),
('purchase.write', '采购入库', 'purchase'),
('analytics.read', '统计分析查看', 'analytics'),
('inventory.read', '库存查看', 'inventory');

INSERT INTO user_role (user_id, role_id) VALUES
(1, 1),
(2, 2),
(3, 3);

INSERT INTO role_permission (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
(2, 3), (2, 4), (2, 5), (2, 6), (2, 7),
(3, 6), (3, 7);

-- 采购单与采购明细
INSERT INTO purchase_order (supplier_id, store_id, created_by, order_time, status, total_amount) VALUES
(1, 1, 1, '2026-04-08 09:00:00', 'received', 1080.00),
(2, 2, 2, '2026-04-09 10:30:00', 'approved', 2340.00);

INSERT INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount) VALUES
(1, 1, 1, 20, 54.00, 1080.00),
(2, 1, 2, 30, 78.00, 2340.00);

-- 入库单与入库明细
INSERT INTO stock_in (purchase_order_id, store_id, operator_id, inbound_time, status) VALUES
(1, 1, 2, '2026-04-09 16:00:00', 'approved'),
(2, 2, 2, '2026-04-10 15:30:00', 'pending');

INSERT INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount) VALUES
(1, 1, 1, 20, 54.00, 1080.00),
(2, 1, 2, 30, 78.00, 2340.00);

-- 门店库存（按 store_id + product_id 维护）
INSERT INTO inventory (store_id, product_id, stock_qty, safety_stock_qty) VALUES
(1, 1, 120, 20),
(1, 2, 35, 10),
(1, 3, 25, 10),
(1, 4, 500, 50),
(1, 5, 300, 30),
(2, 1, 30, 10),
(2, 2, 60, 15),
(2, 3, 90, 20),
(2, 4, 80, 20),
(2, 5, 8, 10);

-- 销售主单
INSERT INTO sale (store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES
(1, 1, '2026-04-10 10:15:00', 'wechat', 147.00, 10.00, 137.00), -- sale_id=1
(1, NULL, '2026-04-10 14:20:00', 'cash',   35.00, 0.00, 35.00),  -- sale_id=2
(2, 2, '2026-04-11 16:05:00', 'alipay', 188.00, 20.00, 168.00);  -- sale_id=3

-- 销售明细（line_amount = quantity * unit_price）
INSERT INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount) VALUES
(1, 1, 1, 1, 88.00, 88.00),
(1, 2, 4, 10, 3.50, 35.00),
(1, 3, 5, 2, 12.00, 24.00),
(2, 1, 4, 10, 3.50, 35.00),
(3, 1, 2, 1, 129.00, 129.00),
(3, 2, 3, 1, 59.00, 59.00);
