# CSV 初始化数据

后端命令 `python manage.py bootstrap_business_db --seed --views` 会创建业务表，并按外键依赖顺序将本目录中的 CSV 导入 MySQL。

当前数据口径已经重建为“出版社书目 + 官方网页”的干净图书体系，并补充“得力办公文具专区”：

- 来源为 `data/` 中的出版社书目文件，以及中国出版集团好书榜、三联书店官网的公开图书页面。
- 当当网数据、由当当数据派生的分类、以及旧非书商品数据均不进入本目录。
- `book.csv` 只包含图书；`product.csv` 同时包含图书商品和得力集实办公文具商品。
- 非图书商品只保留“办公文具”分类树，来源为得力集实商品列表；单位为“箱”的商品已剔除。
- `publisher.csv`、`author.csv`、`translator.csv` 均从本轮图书源数据重新去重生成。
- `生活书店`、`生活书店出版有限公司` 归并到 `生活·读书·新知三联书店` 这一出版社口径。
- 缺少作者的图书候选会被拒绝，不进入最终 `product.csv`、`book.csv` 和关系表。
- `supplier.csv` 不再与出版社一一相同；图书供应商按“重点出版社直供 + 区域/馆配批发商”建模，得力办公文具统一由“得力集实”独家供货。
- `customer`、`member`、`sale`、`purchase_order`、`stock_in` 及其明细表已清空为表头，避免旧脏商品和低质量排行/交易数据继续参与演示。

维护规则：

- 每张业务表对应一个同名 CSV，例如 `product.csv`、`book_author.csv`。
- CSV 表头必须与 `backend/common/sql.py` 中的 `CSV_SEED_FILES` 完全一致。
- 空字符串会作为 SQL `NULL` 导入。
- 修改外键数据时，同时检查依赖它的关系表和明细表。

重建整套 CSV：

```powershell
python sql/tools/rebuild_clean_book_data.py --crawl-web --sanlian-pages 323 --sanlian-workers 12 --sanlian-cache-only --crawl-deli
python sql/tools/validate_seed_data.py
```

如需继续从三联书店网站在线补齐未缓存页面，去掉 `--sanlian-cache-only` 后重跑；脚本会复用 `data/raw/web_catalog/` 中已有缓存。得力集实页面缓存位于 `data/raw/deli_jslink/`，已有缓存时可用 `--deli-cache-only` 复现数据。

中间结果和质量报告位于 `data/clean/`：

- `book_source.csv`：清洗后的源图书候选。
- `books_accepted.csv`：按 ISBN 去重并通过校验的最终图书源数据。
- `books_rejected.csv`：被拒绝或重复替换的记录及原因。
- `category_mapping_audit.csv`：分类映射依据。
- `deli_stationery_source.csv`：清洗后的得力办公文具源商品。
- `deli_stationery_audit.csv`：得力分类和商品爬取统计。
- `clean_data_report.md`：来源、数量、分类、缺失率和 SQL CSV 行数统计。
