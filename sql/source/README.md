# 数据来源

本目录保存重新构建 `sql/data/` 所需的来源数据和保留业务单据。

- `categories_xhsd.csv`：从新华书店网首页分类树读取的原始分类。
- `categories_dangdang.csv`：从当当网分类脚本读取的原始分类，用于交叉核对。
- `categories_mainland.csv`：本项目采用的分类树，以新华书店网分类为参照，拆分为“图书”和“非书商品”两棵根分类。
- `books_mainland.csv`：按新华书店网分类词在当当网图书搜索页抓取的中文图书商品卡片，当前 12000 行。
- `nonbook_mainland.csv`：从新华书店网非书商品分类页抓取的文具、生活文创、数码学习设备、礼品卡等商品卡片，当前 480 行。
- `legacy/`：保留的历史业务 CSV。它们仍保存冗余商品名称和条码，需通过脚本与新的中文商品目录保持一致。

重新在线拉取来源数据时，在仓库根目录执行：

```powershell
python sql/tools/fetch_mainland_catalog.py --book-target 12000 --nonbook-target 480
```

重新生成正式导入数据前，先对齐 legacy 冗余商品列，再构建并校验：

```powershell
python sql/tools/align_mainland_legacy_data.py
python sql/tools/build_seed_data.py
python sql/tools/validate_seed_data.py
```

说明：当当网搜索结果页不批量暴露 ISBN，`books_mainland.csv` 的 `isbn` 使用 `DD{当当商品ID}` 作为可追溯内部编码；新华书店网非书商品条码使用 `XHSD{商品ID}`。如需真实 ISBN，可后续对部分图书详情页做增量补采。
