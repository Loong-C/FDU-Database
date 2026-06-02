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

-- 5) 门店库存预警
CREATE OR REPLACE VIEW v_inventory_warning AS
SELECT
  i.store_id,
  st.store_name,
  i.product_id,
  p.product_name,
  i.stock_qty,
  i.safety_stock_qty,
  i.updated_at
FROM inventory i
JOIN store st ON st.store_id = i.store_id
JOIN product p ON p.product_id = i.product_id
WHERE i.stock_qty <= i.safety_stock_qty
ORDER BY st.store_name, i.stock_qty ASC, p.product_name;

-- 6) 门店库存汇总
CREATE OR REPLACE VIEW v_store_inventory_summary AS
SELECT
  i.store_id,
  st.store_name,
  COUNT(*) AS product_count,
  SUM(i.stock_qty) AS total_stock_qty,
  SUM(CASE WHEN i.stock_qty <= i.safety_stock_qty THEN 1 ELSE 0 END) AS warning_count
FROM inventory i
JOIN store st ON st.store_id = i.store_id
GROUP BY i.store_id, st.store_name
ORDER BY st.store_name;

-- 7) 供应商供货统计
CREATE OR REPLACE VIEW v_supplier_product_summary AS
SELECT
  s.supplier_id,
  s.supplier_name,
  s.status,
  COUNT(sp.product_id) AS supplied_product_count,
  SUM(CASE WHEN sp.is_primary THEN 1 ELSE 0 END) AS primary_product_count,
  MIN(sp.supply_price) AS min_supply_price,
  MAX(sp.supply_price) AS max_supply_price,
  ROUND(AVG(sp.supply_price), 2) AS avg_supply_price
FROM supplier s
LEFT JOIN supplier_product sp ON sp.supplier_id = s.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.status
ORDER BY supplied_product_count DESC, avg_supply_price ASC;

-- 8) 门店采购汇总
CREATE OR REPLACE VIEW v_store_purchase_summary AS
SELECT
  po.store_id,
  st.store_name,
  DATE(po.order_time) AS order_date,
  COUNT(*) AS purchase_order_count,
  SUM(po.total_amount) AS purchase_total_amount,
  SUM(CASE WHEN po.status = 'draft' THEN 1 ELSE 0 END) AS draft_count,
  SUM(CASE WHEN po.status = 'submitted' THEN 1 ELSE 0 END) AS submitted_count,
  SUM(CASE WHEN po.status = 'approved' THEN 1 ELSE 0 END) AS approved_count,
  SUM(CASE WHEN po.status = 'received' THEN 1 ELSE 0 END) AS received_count,
  SUM(CASE WHEN po.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled_count
FROM purchase_order po
JOIN store st ON st.store_id = po.store_id
GROUP BY po.store_id, st.store_name, DATE(po.order_time)
ORDER BY order_date DESC, purchase_total_amount DESC;

-- 9) 图书销量排行
CREATE OR REPLACE VIEW v_book_sales_rank AS
SELECT
  p.product_id,
  p.product_name,
  b.isbn,
  pub.publisher_name,
  COUNT(DISTINCT si.sale_id) AS order_count,
  SUM(si.quantity) AS total_qty,
  SUM(si.line_amount) AS total_sales_amount
FROM sale_item si
JOIN product p ON p.product_id = si.product_id
JOIN book b ON b.product_id = p.product_id
LEFT JOIN publisher pub ON pub.publisher_id = b.publisher_id
GROUP BY p.product_id, p.product_name, b.isbn, pub.publisher_name
ORDER BY total_sales_amount DESC, total_qty DESC, order_count DESC;

-- 10) 门店图书库存明细
CREATE OR REPLACE VIEW v_store_book_inventory_detail AS
SELECT
  i.store_id,
  st.store_name,
  p.product_id,
  p.product_name,
  b.isbn,
  pub.publisher_name,
  i.stock_qty,
  i.safety_stock_qty,
  i.updated_at,
  CASE
    WHEN i.stock_qty = 0 THEN 'out_of_stock'
    WHEN i.stock_qty <= i.safety_stock_qty THEN 'warning'
    ELSE 'normal'
  END AS stock_status
FROM inventory i
JOIN store st ON st.store_id = i.store_id
JOIN product p ON p.product_id = i.product_id
JOIN book b ON b.product_id = p.product_id
LEFT JOIN publisher pub ON pub.publisher_id = b.publisher_id
ORDER BY st.store_name, stock_status DESC, i.stock_qty ASC, p.product_name;

-- 11) 会员复购统计
CREATE OR REPLACE VIEW v_member_repurchase_summary AS
SELECT
  c.customer_id,
  c.customer_name,
  m.member_no,
  m.level,
  COUNT(s.sale_id) AS order_count,
  COUNT(DISTINCT DATE(s.sale_time)) AS active_days,
  COALESCE(SUM(s.actual_amount), 0) AS total_spending,
  COALESCE(ROUND(AVG(s.actual_amount), 2), 0) AS avg_order_amount,
  CASE
    WHEN COUNT(s.sale_id) >= 2 THEN 'yes'
    ELSE 'no'
  END AS repurchased
FROM member m
JOIN customer c ON c.customer_id = m.customer_id
LEFT JOIN sale s ON s.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, m.member_no, m.level
ORDER BY total_spending DESC, order_count DESC;
