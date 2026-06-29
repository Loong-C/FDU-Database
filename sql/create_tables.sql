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

-- 5) 商品父表。库存按门店维度放入 inventory，不再放在 product。
CREATE TABLE product (
  product_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_name VARCHAR(200) NOT NULL,
  category_id BIGINT NOT NULL,
  unit VARCHAR(20) NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  cost_price DECIMAL(10,2) DEFAULT 0,
  barcode VARCHAR(50) UNIQUE,
  status VARCHAR(20) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_product_category
    FOREIGN KEY (category_id) REFERENCES category(category_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (unit_price > 0),
  CHECK (cost_price >= 0),
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
  INDEX idx_sale_store_time (store_id, sale_time),
  INDEX idx_sale_time (sale_time),
  INDEX idx_sale_customer_time (customer_id, sale_time),
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
  INDEX idx_sale_item_product (product_id),
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

-- 16) 系统用户（数据库设计层 RBAC）
CREATE TABLE system_user (
  user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  real_name VARCHAR(50) NOT NULL,
  phone VARCHAR(30) UNIQUE,
  email VARCHAR(100) UNIQUE,
  status VARCHAR(20) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK (status IN ('active', 'disabled'))
);

-- 17) 角色
CREATE TABLE role (
  role_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  role_name VARCHAR(50) NOT NULL UNIQUE,
  role_desc VARCHAR(255),
  CHECK (role_name IN ('admin', 'operator', 'viewer'))
);

-- 18) 权限点
CREATE TABLE permission (
  permission_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  permission_code VARCHAR(100) NOT NULL UNIQUE,
  permission_name VARCHAR(100) NOT NULL,
  module_name VARCHAR(50) NOT NULL
);

-- 19) 用户-角色中间表
CREATE TABLE user_role (
  user_id BIGINT NOT NULL,
  role_id BIGINT NOT NULL,
  PRIMARY KEY (user_id, role_id),
  CONSTRAINT fk_user_role_user
    FOREIGN KEY (user_id) REFERENCES system_user(user_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_user_role_role
    FOREIGN KEY (role_id) REFERENCES role(role_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 20) 角色-权限中间表
CREATE TABLE role_permission (
  role_id BIGINT NOT NULL,
  permission_id BIGINT NOT NULL,
  PRIMARY KEY (role_id, permission_id),
  CONSTRAINT fk_role_permission_role
    FOREIGN KEY (role_id) REFERENCES role(role_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_role_permission_permission
    FOREIGN KEY (permission_id) REFERENCES permission(permission_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 21) 采购单
CREATE TABLE purchase_order (
  purchase_order_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  supplier_id BIGINT NOT NULL,
  store_id BIGINT NOT NULL,
  created_by BIGINT NOT NULL,
  order_time DATETIME NOT NULL,
  status VARCHAR(20) NOT NULL,
  total_amount DECIMAL(12,2) NOT NULL,
  INDEX idx_purchase_order_store_time (store_id, order_time),
  INDEX idx_purchase_order_supplier_time (supplier_id, order_time),
  INDEX idx_purchase_order_status (status),
  CONSTRAINT fk_purchase_order_supplier
    FOREIGN KEY (supplier_id) REFERENCES supplier(supplier_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_purchase_order_store
    FOREIGN KEY (store_id) REFERENCES store(store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_purchase_order_user
    FOREIGN KEY (created_by) REFERENCES system_user(user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (status IN ('draft', 'submitted', 'approved', 'received', 'cancelled')),
  CHECK (total_amount >= 0)
);

-- 22) 采购明细
CREATE TABLE purchase_order_item (
  purchase_order_id BIGINT NOT NULL,
  line_no INT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  purchase_price DECIMAL(10,2) NOT NULL,
  line_amount DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (purchase_order_id, line_no),
  CONSTRAINT fk_purchase_order_item_order
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_order(purchase_order_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_purchase_order_item_product
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (line_no > 0),
  CHECK (quantity > 0),
  CHECK (purchase_price > 0),
  CHECK (line_amount = quantity * purchase_price)
);

-- 23) 入库单
CREATE TABLE stock_in (
  stock_in_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  purchase_order_id BIGINT NOT NULL,
  store_id BIGINT NOT NULL,
  operator_id BIGINT NOT NULL,
  inbound_time DATETIME NOT NULL,
  status VARCHAR(20) NOT NULL,
  INDEX idx_stock_in_store_time (store_id, inbound_time),
  INDEX idx_stock_in_status (status),
  CONSTRAINT fk_stock_in_purchase_order
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_order(purchase_order_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_stock_in_store
    FOREIGN KEY (store_id) REFERENCES store(store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_stock_in_operator
    FOREIGN KEY (operator_id) REFERENCES system_user(user_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (status IN ('pending', 'approved', 'rejected'))
);

-- 24) 入库明细
CREATE TABLE stock_in_item (
  stock_in_id BIGINT NOT NULL,
  line_no INT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL,
  unit_cost DECIMAL(10,2) NOT NULL,
  line_amount DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (stock_in_id, line_no),
  CONSTRAINT fk_stock_in_item_stock_in
    FOREIGN KEY (stock_in_id) REFERENCES stock_in(stock_in_id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_stock_in_item_product
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (line_no > 0),
  CHECK (quantity > 0),
  CHECK (unit_cost > 0),
  CHECK (line_amount = quantity * unit_cost)
);

-- 25) 门店库存
CREATE TABLE inventory (
  store_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  stock_qty INT NOT NULL DEFAULT 0,
  safety_stock_qty INT NOT NULL DEFAULT 0,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (store_id, product_id),
  CONSTRAINT fk_inventory_store
    FOREIGN KEY (store_id) REFERENCES store(store_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_inventory_product
    FOREIGN KEY (product_id) REFERENCES product(product_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CHECK (stock_qty >= 0),
  CHECK (safety_stock_qty >= 0)
);
