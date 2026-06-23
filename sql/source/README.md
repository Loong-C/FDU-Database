# 数据来源

`books_openlibrary.csv` 保存扩展图书数据的原始元数据，供追溯和后续重新整理使用。

该文件来自 Open Library Search API 的结构化 JSON 结果，不抓取 HTML 页面。需要重新在线拉取至少 10000 条图书来源数据时，在仓库根目录执行：

```powershell
python sql/tools/fetch_openlibrary_books.py --target 10000
```

脚本默认保留已有来源行，再追加缺口数据。这可以保持 `legacy/` 业务单据依赖的早期图书 `product_id` 映射稳定；如需完全重抓，可增加 `--replace`。

数据库初始化不会直接读取本目录；实际导入文件位于 `sql/data/`。

`legacy/` 保存合并前的模拟业务 CSV。它们保留了商品名称和条码等辅助列，供重新构建及校验正式数据集使用。
