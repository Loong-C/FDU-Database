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
