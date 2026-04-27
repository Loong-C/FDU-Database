from django.db import transaction
from rest_framework import serializers

from catalog.models import (
    Author,
    Book,
    BookAuthor,
    BookTranslator,
    Category,
    Product,
    Publisher,
    Supplier,
    SupplierProduct,
    Translator,
)
from common.exceptions import ConflictError


def _validate_related_ids(model, ids, field_name):
    existing = model.objects.in_bulk(ids)
    missing = [value for value in ids if value not in existing]
    if missing:
        raise serializers.ValidationError({field_name: f"以下ID不存在: {missing}"})
    return existing


def category_descendant_ids(category_id):
    """返回该分类自身及全部后代分类的 id 集合。
    用于"父分类筛选应包含其下子分类"的查询场景。category_id 不存在时返回 [category_id]
    本身（仍交由上层的过滤拿到空结果），保持 API 行为可预期。
    """
    try:
        root_id = int(category_id)
    except (TypeError, ValueError):
        return []
    collected = {root_id}
    pending = [root_id]
    while pending:
        next_level = list(
            Category.objects.filter(parent_category_id__in=pending)
            .values_list("category_id", flat=True)
        )
        new_ids = [cid for cid in next_level if cid not in collected]
        if not new_ids:
            break
        collected.update(new_ids)
        pending = new_ids
    return list(collected)


def replace_supplier_links(product, supplier_links):
    supplier_links = supplier_links or []
    supplier_ids = [item["supplier_id"] for item in supplier_links]
    if supplier_ids:
        suppliers = _validate_related_ids(Supplier, supplier_ids, "supplier_links")
    else:
        suppliers = {}

    product.supplier_links.all().delete()
    SupplierProduct.objects.bulk_create(
        [
            SupplierProduct(
                supplier=suppliers[item["supplier_id"]],
                product=product,
                supply_price=item["supply_price"],
                min_order_qty=item.get("min_order_qty"),
                is_primary=item.get("is_primary", False),
            )
            for item in supplier_links
        ]
    )


def create_product(validated_data):
    supplier_links = validated_data.pop("supplier_links", [])
    category_id = validated_data.pop("category_id")
    category = Category.objects.filter(pk=category_id).first()
    if not category:
        raise serializers.ValidationError({"category_id": "商品分类不存在。"})

    with transaction.atomic():
        product = Product.objects.create(category=category, **validated_data)
        replace_supplier_links(product, supplier_links)
        return product


def update_product(instance, validated_data):
    if hasattr(instance, "book"):
        raise ConflictError("图书类商品请使用 books 接口进行修改。")

    supplier_links = validated_data.pop("supplier_links", None)
    category_id = validated_data.pop("category_id", None)
    if category_id is not None:
        category = Category.objects.filter(pk=category_id).first()
        if not category:
            raise serializers.ValidationError({"category_id": "商品分类不存在。"})
        instance.category = category

    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    with transaction.atomic():
        instance.save()
        if supplier_links is not None:
            replace_supplier_links(instance, supplier_links)
        return instance


def _replace_book_authors(book, author_ids):
    if author_ids is None:
        return
    authors = _validate_related_ids(Author, author_ids, "author_ids")
    book.author_links.all().delete()
    BookAuthor.objects.bulk_create(
        [
            BookAuthor(product=book, author=authors[author_id], author_order=index)
            for index, author_id in enumerate(author_ids, start=1)
        ]
    )


def _replace_book_translators(book, translator_ids):
    if translator_ids is None:
        return
    translators = _validate_related_ids(Translator, translator_ids, "translator_ids")
    book.translator_links.all().delete()
    BookTranslator.objects.bulk_create(
        [
            BookTranslator(product=book, translator=translators[translator_id])
            for translator_id in translator_ids
        ]
    )


def create_book(validated_data):
    author_ids = validated_data.pop("author_ids", None)
    translator_ids = validated_data.pop("translator_ids", [])
    supplier_links = validated_data.pop("supplier_links", [])
    category_id = validated_data.pop("category_id")
    publisher_id = validated_data.pop("publisher_id")

    category = Category.objects.filter(pk=category_id).first()
    if not category:
        raise serializers.ValidationError({"category_id": "商品分类不存在。"})
    publisher = Publisher.objects.filter(pk=publisher_id).first()
    if not publisher:
        raise serializers.ValidationError({"publisher_id": "出版社不存在。"})
    if not author_ids:
        raise serializers.ValidationError({"author_ids": "图书至少需要一位作者。"})

    product_fields = {
        "product_name": validated_data.pop("product_name"),
        "unit": validated_data.pop("unit"),
        "unit_price": validated_data.pop("unit_price"),
        "cost_price": validated_data.pop("cost_price", 0),
        "stock_qty": validated_data.pop("stock_qty", 0),
        "barcode": validated_data.pop("barcode", None),
        "status": validated_data.pop("status"),
    }

    with transaction.atomic():
        product = Product.objects.create(category=category, **product_fields)
        book = Book.objects.create(product=product, publisher=publisher, **validated_data)
        replace_supplier_links(product, supplier_links)
        _replace_book_authors(book, author_ids)
        _replace_book_translators(book, translator_ids)
        return book


def update_book(instance, validated_data):
    author_ids = validated_data.pop("author_ids", None)
    translator_ids = validated_data.pop("translator_ids", None)
    supplier_links = validated_data.pop("supplier_links", None)
    category_id = validated_data.pop("category_id", None)
    publisher_id = validated_data.pop("publisher_id", None)

    product = instance.product
    if category_id is not None:
        category = Category.objects.filter(pk=category_id).first()
        if not category:
            raise serializers.ValidationError({"category_id": "商品分类不存在。"})
        product.category = category

    if publisher_id is not None:
        publisher = Publisher.objects.filter(pk=publisher_id).first()
        if not publisher:
            raise serializers.ValidationError({"publisher_id": "出版社不存在。"})
        instance.publisher = publisher

    product_fields = [
        "product_name",
        "unit",
        "unit_price",
        "cost_price",
        "stock_qty",
        "barcode",
        "status",
    ]
    book_fields = [
        "isbn",
        "publish_date",
        "edition",
        "language",
        "page_count",
    ]
    for field in product_fields:
        if field in validated_data:
            setattr(product, field, validated_data[field])
    for field in book_fields:
        if field in validated_data:
            setattr(instance, field, validated_data[field])

    with transaction.atomic():
        product.save()
        instance.save()
        if supplier_links is not None:
            replace_supplier_links(product, supplier_links)
        if author_ids is not None:
            if not author_ids:
                raise serializers.ValidationError({"author_ids": "图书至少需要一位作者。"})
            _replace_book_authors(instance, author_ids)
        if translator_ids is not None:
            _replace_book_translators(instance, translator_ids)
        return instance
