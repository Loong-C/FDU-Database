# CSV 初始化数据

后端命令 `python manage.py bootstrap_business_db --seed --views` 会创建业务表，并按外键依赖顺序将本目录中的 CSV 导入 MySQL。

维护规则：

- 每张业务表对应一个同名 CSV，例如 `product.csv`、`sale_item.csv`。
- CSV 表头必须与 `backend/common/sql.py` 中的 `CSV_SEED_FILES` 完全一致。
- 空字符串会作为 SQL `NULL` 导入。
- 修改外键数据时，同时检查依赖它的明细表。
- `sql/source/` 下保存分类、图书、非书商品的来源数据和历史业务单据，不会在初始化时直接导入。

导入顺序由后端统一维护，不需要手写 `INSERT` SQL。

需要从保留的来源数据重新生成整套 CSV 时，在仓库根目录执行：

```powershell
python sql/tools/align_mainland_legacy_data.py
python sql/tools/build_seed_data.py
python sql/tools/validate_seed_data.py
```

需要重新在线拉取中国大陆书店来源数据时，先执行：

```powershell
python sql/tools/fetch_mainland_catalog.py --book-target 12000 --nonbook-target 480
```

当前数据口径以新华书店网分类树为分类参照，并用当当网图书搜索结果补充 12000 条中文图书商品。非书商品来自新华书店网分类页，共 480 条，覆盖学习用品、家居/生活用品、3C 数码和礼品卡。
