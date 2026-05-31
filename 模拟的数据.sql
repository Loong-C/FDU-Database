USE online_bookstore_db;

-- 模拟业务数据脚本
-- 建议执行顺序：create_database.sql -> create_tables.sql -> insert_sample_data.sql -> import_real_book_data.sql -> 本脚本
-- 说明：本脚本负责补充那些不适合直接从公开图书元数据中获取的业务数据

-- 1) 补充供应商（模拟生成）
INSERT IGNORE INTO supplier (supplier_id, supplier_name, contact_name, phone, email, status) VALUES (101, '国际科技图书供货商', '赵文博', '010-70010001', 'techbooks@example.com', 'active');
INSERT IGNORE INTO supplier (supplier_id, supplier_name, contact_name, phone, email, status) VALUES (102, '经典文学图书代理商', '林雅雯', '021-70010002', 'literaturehub@example.com', 'active');
INSERT IGNORE INTO supplier (supplier_id, supplier_name, contact_name, phone, email, status) VALUES (103, '学术资源联合供应中心', '周启航', '020-70010003', 'academicresource@example.com', 'active');
INSERT IGNORE INTO supplier (supplier_id, supplier_name, contact_name, phone, email, status) VALUES (104, '河畔图书分销公司', '沈嘉禾', '0571-70010004', 'riversidebook@example.com', 'inactive');

-- 2) 客户与会员（模拟生成）
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1001, '陈思远', '13810000001', 'chen.siyuan@example.com', '北京市海淀区中关村南大街1号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1002, '赵可欣', '13810000002', 'zhao.kexin@example.com', '上海市徐汇区漕溪北路18号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1003, '王嘉宁', '13810000003', 'wang.jianing@example.com', '南京市鼓楼区中央路66号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1004, '刘子墨', '13810000004', 'liu.zimo@example.com', '杭州市西湖区文三路88号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1005, '李安然', '13810000005', 'li.anran@example.com', '广州市天河区体育西路28号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1006, '周亦辰', '13810000006', 'zhou.yichen@example.com', '成都市高新区天府大道399号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1007, '徐若彤', '13810000007', 'xu.ruotong@example.com', '武汉市洪山区珞喻路77号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1008, '孙景行', '13810000008', 'sun.jingxing@example.com', '西安市雁塔区长安中路15号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1009, '郑雨桐', '13810000009', 'zheng.yutong@example.com', '苏州市工业园区星湖街9号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1010, '何沐阳', '13810000010', 'he.muyang@example.com', '天津市南开区白堤路56号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1011, '邵明哲', '13810000011', 'shao.mingzhe@example.com', '长沙市岳麓区麓山南路12号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO customer (customer_id, customer_name, phone, email, address, register_time, status) VALUES (1012, '彭语晴', '13810000012', 'peng.yuqing@example.com', '青岛市市南区香港中路30号', '2026-01-01 10:00:00', 'active');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1001, 'M20261001', 'gold', 1500, '2026-01-12');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1002, 'M20261002', 'silver', 820, '2026-01-20');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1003, 'M20261003', 'gold', 1360, '2026-02-03');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1004, 'M20261004', 'bronze', 260, '2026-02-15');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1005, 'M20261005', 'platinum', 2680, '2026-03-01');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1006, 'M20261006', 'silver', 640, '2026-03-18');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1007, 'M20261007', 'bronze', 180, '2026-04-02');
INSERT IGNORE INTO member (customer_id, member_no, level, points, join_date) VALUES (1008, 'M20261008', 'gold', 1100, '2026-04-16');

-- 3) 供应关系（基于真实图书池模拟生成）
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), 44.24, 10, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 101, (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), 47.78, 20, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), 46.61, 20, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 101, (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), 48.98, 30, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 102, (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), 51.35, 40, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), 55.46, 50, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 103, (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), 44.24, 50, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), 46.61, 10, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), 48.98, 20, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 102, (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), 52.90, 30, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 101, (SELECT product_id FROM product WHERE barcode = '9780760049044' LIMIT 1), 51.35, 30, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 102, (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), 44.24, 40, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 103, (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), 46.61, 50, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), 50.34, 60, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), 48.98, 10, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780072958867' LIMIT 1), 51.35, 20, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 101, (SELECT product_id FROM product WHERE barcode = '9780393034264' LIMIT 1), 27.44, 30, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 103, (SELECT product_id FROM product WHERE barcode = '9780393034264' LIMIT 1), 29.64, 40, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 102, (SELECT product_id FROM product WHERE barcode = '9781548127596' LIMIT 1), 28.91, 40, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 103, (SELECT product_id FROM product WHERE barcode = '9781539004950' LIMIT 1), 30.38, 50, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781977930231' LIMIT 1), 31.85, 10, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 101, (SELECT product_id FROM product WHERE barcode = '9781977930231' LIMIT 1), 34.40, 20, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781497354975' LIMIT 1), 27.44, 20, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 101, (SELECT product_id FROM product WHERE barcode = '9798681983439' LIMIT 1), 28.91, 30, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 102, (SELECT product_id FROM product WHERE barcode = '9781847498014' LIMIT 1), 30.38, 40, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781847498014' LIMIT 1), 32.81, 50, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 103, (SELECT product_id FROM product WHERE barcode = '9798461321680' LIMIT 1), 31.85, 50, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781507585559' LIMIT 1), 27.44, 10, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9798463083326' LIMIT 1), 28.91, 20, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 102, (SELECT product_id FROM product WHERE barcode = '9798463083326' LIMIT 1), 31.22, 30, FALSE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 101, (SELECT product_id FROM product WHERE barcode = '9782070586646' LIMIT 1), 30.38, 30, TRUE;
INSERT IGNORE INTO supplier_product (supplier_id, product_id, supply_price, min_order_qty, is_primary)
SELECT 102, (SELECT product_id FROM product WHERE barcode = '9780198600817' LIMIT 1), 31.85, 40, TRUE;

-- 4) 门店库存（基于真实图书池模拟生成）
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), 18, 5;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), 10, 4;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), 25, 6;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), 15, 4;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), 32, 8;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), 20, 5;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), 39, 9;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), 25, 6;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), 46, 11;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), 30, 7;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), 53, 13;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), 35, 8;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), 60, 15;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), 40, 10;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780760049044' LIMIT 1), 67, 16;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780760049044' LIMIT 1), 45, 11;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), 74, 18;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), 10, 4;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), 81, 20;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), 15, 4;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), 23, 5;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), 20, 5;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780072958867' LIMIT 1), 30, 7;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780072958867' LIMIT 1), 25, 6;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780393034264' LIMIT 1), 37, 9;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780393034264' LIMIT 1), 30, 7;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781548127596' LIMIT 1), 44, 11;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781548127596' LIMIT 1), 35, 8;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781539004950' LIMIT 1), 51, 12;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781539004950' LIMIT 1), 40, 10;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781977930231' LIMIT 1), 58, 14;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781977930231' LIMIT 1), 45, 11;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781497354975' LIMIT 1), 65, 16;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781497354975' LIMIT 1), 10, 4;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9798681983439' LIMIT 1), 72, 18;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9798681983439' LIMIT 1), 15, 4;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781847498014' LIMIT 1), 79, 19;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781847498014' LIMIT 1), 20, 5;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9798461321680' LIMIT 1), 21, 5;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9798461321680' LIMIT 1), 25, 6;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9781507585559' LIMIT 1), 28, 7;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9781507585559' LIMIT 1), 30, 7;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9798463083326' LIMIT 1), 35, 8;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9798463083326' LIMIT 1), 35, 8;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9782070586646' LIMIT 1), 42, 10;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9782070586646' LIMIT 1), 40, 10;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 1, (SELECT product_id FROM product WHERE barcode = '9780198600817' LIMIT 1), 49, 12;
INSERT IGNORE INTO inventory (store_id, product_id, stock_qty, safety_stock_qty)
SELECT 2, (SELECT product_id FROM product WHERE barcode = '9780198600817' LIMIT 1), 45, 11;

-- 5) 采购单与采购明细（模拟生成）
INSERT IGNORE INTO purchase_order (purchase_order_id, supplier_id, store_id, created_by, order_time, status, total_amount) VALUES (3001, 101, 1, 1, '2026-05-05 09:30:00', 'received', 4114.32);
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3001, 1, (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), 23, 48.98, 1126.54;
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3001, 2, (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), 28, 48.98, 1371.44;
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3001, 3, (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), 33, 48.98, 1616.34;
INSERT IGNORE INTO purchase_order (purchase_order_id, supplier_id, store_id, created_by, order_time, status, total_amount) VALUES (3002, 102, 2, 2, '2026-05-07 14:00:00', 'approved', 4555.14);
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3002, 1, (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), 26, 48.98, 1273.48;
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3002, 2, (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), 31, 48.98, 1518.38;
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3002, 3, (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), 36, 48.98, 1763.28;
INSERT IGNORE INTO purchase_order (purchase_order_id, supplier_id, store_id, created_by, order_time, status, total_amount) VALUES (3003, 103, 1, 2, '2026-05-10 11:15:00', 'submitted', 2204.10);
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3003, 1, (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), 20, 48.98, 979.60;
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3003, 2, (SELECT product_id FROM product WHERE barcode = '9780760049044' LIMIT 1), 25, 48.98, 1224.50;
INSERT IGNORE INTO purchase_order (purchase_order_id, supplier_id, store_id, created_by, order_time, status, total_amount) VALUES (3004, 1, 2, 1, '2026-05-12 16:40:00', 'received', 4114.32);
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3004, 1, (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), 23, 48.98, 1126.54;
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3004, 2, (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), 28, 48.98, 1371.44;
INSERT IGNORE INTO purchase_order_item (purchase_order_id, line_no, product_id, quantity, purchase_price, line_amount)
SELECT 3004, 3, (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), 33, 48.98, 1616.34;

-- 6) 入库单与入库明细（模拟生成）
INSERT IGNORE INTO stock_in (stock_in_id, purchase_order_id, store_id, operator_id, inbound_time, status) VALUES (4001, 3001, 1, 2, '2026-05-06 15:00:00', 'approved');
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4001, 1, (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), 26, 48.98, 1273.48;
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4001, 2, (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), 30, 48.98, 1469.40;
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4001, 3, (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), 34, 48.98, 1665.32;
INSERT IGNORE INTO stock_in (stock_in_id, purchase_order_id, store_id, operator_id, inbound_time, status) VALUES (4002, 3002, 2, 2, '2026-05-08 17:20:00', 'pending');
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4002, 1, (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), 24, 48.98, 1175.52;
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4002, 2, (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), 28, 48.98, 1371.44;
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4002, 3, (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), 32, 48.98, 1567.36;
INSERT IGNORE INTO stock_in (stock_in_id, purchase_order_id, store_id, operator_id, inbound_time, status) VALUES (4003, 3004, 2, 1, '2026-05-13 10:45:00', 'approved');
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4003, 1, (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), 26, 48.98, 1273.48;
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4003, 2, (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), 30, 48.98, 1469.40;
INSERT IGNORE INTO stock_in_item (stock_in_id, line_no, product_id, quantity, unit_cost, line_amount)
SELECT 4003, 3, (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), 34, 48.98, 1665.32;

-- 7) 销售主单与销售明细（模拟生成）
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5001, 1, 1001, '2026-05-14 10:05:00', 'wechat', 161.16, 8.06, 153.10);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5001, 1, (SELECT product_id FROM product WHERE barcode = '9780072283631' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5001, 2, (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), 1, 82.16, 82.16;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5002, 2, 1002, '2026-05-14 16:20:00', 'alipay', 331.80, 16.59, 315.21);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5002, 1, (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5002, 2, (SELECT product_id FROM product WHERE barcode = '9780357673034' LIMIT 1), 1, 82.16, 82.16;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5002, 3, (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), 2, 85.32, 170.64;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5003, 1, NULL, '2026-05-15 11:40:00', 'cash', 79.00, 0.00, 79.00);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5003, 1, (SELECT product_id FROM product WHERE barcode = '9780201144710' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5004, 2, 1003, '2026-05-15 18:10:00', 'card', 161.16, 8.06, 153.10);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5004, 1, (SELECT product_id FROM product WHERE barcode = '9781403916013' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5004, 2, (SELECT product_id FROM product WHERE barcode = '9780760049044' LIMIT 1), 1, 82.16, 82.16;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5005, 1, 1004, '2026-05-16 09:35:00', 'wechat', 331.80, 16.59, 315.21);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5005, 1, (SELECT product_id FROM product WHERE barcode = '9780131873254' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5005, 2, (SELECT product_id FROM product WHERE barcode = '9780071217620' LIMIT 1), 1, 82.16, 82.16;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5005, 3, (SELECT product_id FROM product WHERE barcode = '9780321210258' LIMIT 1), 2, 85.32, 170.64;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5006, 2, 1005, '2026-05-16 14:50:00', 'mixed', 129.96, 6.50, 123.46);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5006, 1, (SELECT product_id FROM product WHERE barcode = '9780072958867' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5006, 2, (SELECT product_id FROM product WHERE barcode = '9780393034264' LIMIT 1), 1, 50.96, 50.96;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5007, 1, 1006, '2026-05-17 10:25:00', 'wechat', 99.96, 5.00, 94.96);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5007, 1, (SELECT product_id FROM product WHERE barcode = '9781548127596' LIMIT 1), 1, 49.00, 49.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5007, 2, (SELECT product_id FROM product WHERE barcode = '9781539004950' LIMIT 1), 1, 50.96, 50.96;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5008, 2, NULL, '2026-05-17 19:05:00', 'cash', 49.00, 0.00, 49.00);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5008, 1, (SELECT product_id FROM product WHERE barcode = '9781977930231' LIMIT 1), 1, 49.00, 49.00;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5009, 1, 1007, '2026-05-18 13:15:00', 'alipay', 129.96, 6.50, 123.46);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5009, 1, (SELECT product_id FROM product WHERE barcode = '9780321369574' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5009, 2, (SELECT product_id FROM product WHERE barcode = '9781497354975' LIMIT 1), 1, 50.96, 50.96;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5010, 2, 1008, '2026-05-18 17:45:00', 'wechat', 235.80, 11.79, 224.01);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5010, 1, (SELECT product_id FROM product WHERE barcode = '9783030262532' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5010, 2, (SELECT product_id FROM product WHERE barcode = '9798681983439' LIMIT 1), 1, 50.96, 50.96;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5010, 3, (SELECT product_id FROM product WHERE barcode = '9781847498014' LIMIT 1), 2, 52.92, 105.84;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5011, 1, 1009, '2026-05-19 11:00:00', 'card', 99.96, 5.00, 94.96);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5011, 1, (SELECT product_id FROM product WHERE barcode = '9798461321680' LIMIT 1), 1, 49.00, 49.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5011, 2, (SELECT product_id FROM product WHERE barcode = '9781507585559' LIMIT 1), 1, 50.96, 50.96;
INSERT IGNORE INTO sale (sale_id, store_id, customer_id, sale_time, payment_method, total_amount, discount_amount, actual_amount) VALUES (5012, 2, 1010, '2026-05-19 15:25:00', 'wechat', 129.96, 6.50, 123.46);
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5012, 1, (SELECT product_id FROM product WHERE barcode = '9780131225206' LIMIT 1), 1, 79.00, 79.00;
INSERT IGNORE INTO sale_item (sale_id, line_no, product_id, quantity, unit_price, line_amount)
SELECT 5012, 2, (SELECT product_id FROM product WHERE barcode = '9798463083326' LIMIT 1), 1, 50.96, 50.96;
