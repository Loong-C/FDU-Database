DROP DATABASE IF EXISTS online_bookstore_db;
CREATE DATABASE online_bookstore_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
create_tables.sql
USE online_bookstore_db;
-- 1) 门店
CREATE TABLE store (
  store_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  store_name VARCHAR(100) NOT NULL UNIQUE,
  city VARCHAR(50) NOT NULL,
  address VARCHAR(255) NOT NULL,
  phone VARCHAR(30) UNIQUE,
  manager_name VARCHAR(50),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- 2) 供应商
CREATE TABLE supplier (
  supplier_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  supplier_name VARCHAR(100) NOT NULL UNIQUE,
  contact_name VARCHAR(50),
  phone VARCHAR(30),
  email VARCHAR(100) UNIQUE,
  status VARCHAR(20) NOT NULL,
  CHECK (status IN ('active', 'inactive'))
);
-- 3) 分类（支持父分类）
CREATE TABLE category (
  category_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  category_name VARCHAR(100) NOT NULL UNIQUE,
  parent_category_id BIGINT NULL,
  CONSTRAINT fk_category_parent
    FOREIGN KEY (parent_category_id) REFERENCES category(category_id)
    ON UPDATE CASCADE ON DELETE SET NULL
);
-- 4) 出版社
CREATE TABLE publisher (
  publisher_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  publisher_name VARCHAR(150) NOT NULL UNIQUE,
  contact_name VARCHAR(50),
  phone VARCHAR(30),
  email VARCHAR(100),
  address VARCHAR(255),
  country VARCHAR(50),
  website VARCHAR(255)
);
-- 5) 商品父表
CREATE TABLE product (
  product_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_name VARCHAR(200) NOT NULL,
  category_id BIGINT NOT NULL,
  unit VARCHAR(20) NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  cost_price DECIMAL(10,2) DEFAULT 0,
  stock_qty INT NOT NULL DEFAULT 0,
  barcode VARCHAR(50) UNIQUE,
  status VARCHAR(20) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_product_category
    FOREIGN KEY (category_id) REFERENCES category(category_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (unit_price > 0),
  CHECK (cost_price >= 0),
  CHECK (stock_qty >= 0),
  CHECK (status IN ('onsale', 'offsale', 'discontinued'))
);
-- 6) 图书子表（与 product 1:1）
CREATE TABLE book (
  product_id BIGINT PRIMARY KEY,
  isbn VARCHAR(20) NOT NULL UNIQUE,
  publisher_id BIGINT NOT NULL,
  publish_date DATE,
  edition VARCHAR(20),
  language VARCHAR(30),
  page_count INT,
  CONSTRAINT fk_book_product
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_book_publisher
    FOREIGN KEY (publisher_id) REFERENCES publisher(publisher_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (page_count IS NULL OR page_count > 0)
);
-- 7) 作者
CREATE TABLE author (
  author_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  author_name VARCHAR(100) NOT NULL,
  country VARCHAR(50)
);
-- 8) 译者
CREATE TABLE translator (
  translator_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  translator_name VARCHAR(100) NOT NULL,
  country VARCHAR(50)
);
-- 9) 客户
CREATE TABLE customer (
  customer_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_name VARCHAR(100) NOT NULL,
  phone VARCHAR(30) UNIQUE,
  email VARCHAR(100) UNIQUE,
  address VARCHAR(255),
  register_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(20) NOT NULL,
  CHECK (status IN ('active', 'inactive'))
);
-- 10) 会员子表（与 customer 1:1）
CREATE TABLE member (
  customer_id BIGINT PRIMARY KEY,
  member_no VARCHAR(50) NOT NULL UNIQUE,
  level VARCHAR(20) NOT NULL,
  points INT NOT NULL DEFAULT 0,
  join_date DATE NOT NULL,
  CONSTRAINT fk_member_customer
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CHECK (points >= 0),
  CHECK (level IN ('bronze', 'silver', 'gold', 'platinum'))
);
-- 11) 销售主单
CREATE TABLE sale (
  sale_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  store_id BIGINT NOT NULL,
  customer_id BIGINT NULL,
  sale_time DATETIME NOT NULL,
  payment_method VARCHAR(30) NOT NULL,
  total_amount DECIMAL(12,2) NOT NULL,
  discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0,
  actual_amount DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_sale_store
    FOREIGN KEY (store_id) REFERENCES store(store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_sale_customer
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
    ON UPDATE CASCADE ON DELETE SET NULL,
  CHECK (payment_method IN ('cash', 'card', 'wechat', 'alipay', 'mixed')),
  CHECK (total_amount >= 0),
  CHECK (discount_amount >= 0),
  CHECK (actual_amount >= 0),
  CHECK (actual_amount = total_amount - discount_amount)
);
-- 12) 销售明细
CREATE TABLE sale_item (
  sale_id BIGINT NOT NULL,
  line_no INT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  line_amount DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (sale_id, line_no),
  CONSTRAINT fk_sale_item_sale
    FOREIGN KEY (sale_id) REFERENCES sale(sale_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_sale_item_product
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (line_no > 0),
  CHECK (quantity > 0),
  CHECK (unit_price > 0),
  CHECK (line_amount >= 0),
  CHECK (line_amount = quantity * unit_price)
);
-- 13) 供应商-商品中间表
CREATE TABLE supplier_product (
  supplier_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  supply_price DECIMAL(10,2) NOT NULL,
  min_order_qty INT,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY (supplier_id, product_id),
  CONSTRAINT fk_supplier_product_supplier
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_supplier_product_product
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (supply_price > 0),
  CHECK (min_order_qty IS NULL OR min_order_qty > 0)
);
-- 14) 图书-作者中间表
CREATE TABLE book_author (
  product_id BIGINT NOT NULL,
  author_id BIGINT NOT NULL,
  author_order INT,
  PRIMARY KEY (product_id, author_id),
  CONSTRAINT fk_book_author_book
    FOREIGN KEY (product_id) REFERENCES book(product_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_book_author_author
    FOREIGN KEY (author_id) REFERENCES author(author_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (author_order IS NULL OR author_order > 0)
);
-- 15) 图书-译者中间表
CREATE TABLE book_translator (
  product_id BIGINT NOT NULL,
  translator_id BIGINT NOT NULL,
  PRIMARY KEY (product_id, translator_id),
  CONSTRAINT fk_book_translator_book
    FOREIGN KEY (product_id) REFERENCES book(product_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_book_translator_translator
    FOREIGN KEY (translator_id) REFERENCES translator(translator_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);
insert_sample_data.sql
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
('译林出版社', '周编辑', '025-12340003', 'contact@yilin.com', '南京市鼓楼区C路3号', '中国', 'https://www.yilin.com');
-- 商品（含图书与非图书）
INSERT INTO product (product_name, category_id, unit, unit_price, cost_price, stock_qty, barcode, status) VALUES
('数据库系统概论（第6版）', 3, '本', 88.00, 55.00, 120, '9787111000001', 'onsale'), -- id=1
('深入理解计算机系统',       3, '本', 129.00, 80.00, 60, '9787111000002', 'onsale'), -- id=2
('百年孤独',                 2, '本', 59.00, 35.00, 90, '9787111000003', 'onsale'), -- id=3
('黑色中性笔',               4, '支', 3.50, 1.20, 500, '690123450001',  'onsale'), -- id=4
('A4笔记本',                 4, '本', 12.00, 6.00, 300, '690123450002',  'offsale'); -- id=5
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
views_or_reports.sql
USE online_bookstore_db;
-- 1) 门店日销售汇总
CREATE OR REPLACE VIEW v_store_sales_daily AS
SELECT
  s.store_id,
  st.store_name,
  DATE(s.sale_time) AS sale_date,
  COUNT(*) AS order_count,
  SUM(s.total_amount) AS total_amount_sum,
  SUM(s.discount_amount) AS discount_amount_sum,
  SUM(s.actual_amount) AS actual_amount_sum
FROM sale s
JOIN store st ON st.store_id = s.store_id
GROUP BY s.store_id, st.store_name, DATE(s.sale_time);
-- 2) 商品销量与销售额排行
CREATE OR REPLACE VIEW v_product_sales_rank AS
SELECT
  p.product_id,
  p.product_name,
  p.status,
  SUM(si.quantity) AS total_qty,
  SUM(si.line_amount) AS total_sales_amount
FROM sale_item si
JOIN product p ON p.product_id = si.product_id
GROUP BY p.product_id, p.product_name, p.status
ORDER BY total_sales_amount DESC, total_qty DESC;
-- 3) 会员消费排行
CREATE OR REPLACE VIEW v_member_spending_rank AS
SELECT
  c.customer_id,
  c.customer_name,
  m.member_no,
  m.level,
  COUNT(s.sale_id) AS order_count,
  COALESCE(SUM(s.actual_amount), 0) AS total_spending
FROM member m
JOIN customer c ON c.customer_id = m.customer_id
LEFT JOIN sale s ON s.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, m.member_no, m.level
ORDER BY total_spending DESC, order_count DESC;
-- 4) 分类销售汇总
CREATE OR REPLACE VIEW v_category_sales_summary AS
SELECT
  c.category_id,
  c.category_name,
  SUM(si.quantity) AS total_qty,
  SUM(si.line_amount) AS total_sales_amount
FROM sale_item si
JOIN product p ON p.product_id = si.product_id
JOIN category c ON c.category_id = p.category_id
GROUP BY c.category_id, c.category_name
ORDER BY total_sales_amount DESC;
