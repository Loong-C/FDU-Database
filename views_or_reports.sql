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
