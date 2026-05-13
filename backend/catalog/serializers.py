from decimal import Decimal

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
from common.validators import validate_phone, validate_publish_date
from inventory.serializers import InventoryReadSerializer
from inventory.services import product_stock_total


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "supplier_id",
            "supplier_name",
            "contact_name",
            "phone",
            "email",
            "status",
        ]
        read_only_fields = ["supplier_id"]

    def validate_phone(self, value):
        return validate_phone(value)


class CategorySerializer(serializers.ModelSerializer):
    parent_category_id = serializers.PrimaryKeyRelatedField(
        source="parent_category",
        queryset=Category.objects.all(),
        required=False,
        allow_null=True,
    )
    parent_category_name = serializers.CharField(source="parent_category.category_name", read_only=True)

    class Meta:
        model = Category
        fields = [
            "category_id",
            "category_name",
            "parent_category_id",
            "parent_category_name",
        ]
        read_only_fields = ["category_id", "parent_category_name"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = [
            "publisher_id",
            "publisher_name",
            "contact_name",
            "phone",
            "email",
            "address",
            "country",
            "website",
        ]
        read_only_fields = ["publisher_id"]

    def validate_phone(self, value):
        return validate_phone(value)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["author_id", "author_name", "country"]
        read_only_fields = ["author_id"]


class TranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translator
        fields = ["translator_id", "translator_name", "country"]
        read_only_fields = ["translator_id"]


class SupplierLinkInputSerializer(serializers.Serializer):
    supplier_id = serializers.IntegerField()
    supply_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    min_order_qty = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    is_primary = serializers.BooleanField(required=False, default=False)


class SupplierLinkReadSerializer(serializers.ModelSerializer):
    supplier_id = serializers.IntegerField(source="supplier.supplier_id", read_only=True)
    supplier_name = serializers.CharField(source="supplier.supplier_name", read_only=True)

    class Meta:
        model = SupplierProduct
        fields = [
            "supplier_id",
            "supplier_name",
            "supply_price",
            "min_order_qty",
            "is_primary",
        ]


class ProductReadSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source="category.category_id", read_only=True)
    category_name = serializers.CharField(source="category.category_name", read_only=True)
    supplier_links = serializers.SerializerMethodField()
    is_book = serializers.SerializerMethodField()
    stock_qty = serializers.SerializerMethodField()
    inventory = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "category_id",
            "category_name",
            "unit",
            "unit_price",
            "cost_price",
            "stock_qty",
            "inventory",
            "barcode",
            "status",
            "created_at",
            "is_book",
            "supplier_links",
        ]

    def get_supplier_links(self, instance):
        links = instance.supplier_links.all()
        return SupplierLinkReadSerializer(links, many=True).data

    def get_is_book(self, instance):
        return hasattr(instance, "book")

    def get_stock_qty(self, instance):
        return product_stock_total(instance)

    def get_inventory(self, instance):
        rows = instance.inventories.select_related("store").all()
        return InventoryReadSerializer(rows, many=True).data


class ProductWriteSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=200)
    category_id = serializers.IntegerField()
    unit = serializers.CharField(max_length=20)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    cost_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
        default=Decimal("0.00"),
    )
    stock_qty = serializers.IntegerField(min_value=0, required=False)
    store_id = serializers.IntegerField(required=False)
    safety_stock_qty = serializers.IntegerField(min_value=0, required=False)
    barcode = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(choices=Product.STATUS_CHOICES)
    supplier_links = SupplierLinkInputSerializer(many=True, required=False, default=list)

    def validate_supplier_links(self, value):
        supplier_ids = [item["supplier_id"] for item in value]
        if len(supplier_ids) != len(set(supplier_ids)):
            raise serializers.ValidationError("供应商关联不能重复。")
        primary_count = sum(1 for item in value if item.get("is_primary"))
        if primary_count > 1:
            raise serializers.ValidationError("最多只能设置一个主供供应商。")
        return value


class BookReadSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    category_id = serializers.IntegerField(source="product.category.category_id", read_only=True)
    category_name = serializers.CharField(source="product.category.category_name", read_only=True)
    unit = serializers.CharField(source="product.unit", read_only=True)
    unit_price = serializers.DecimalField(source="product.unit_price", max_digits=10, decimal_places=2, read_only=True)
    cost_price = serializers.DecimalField(source="product.cost_price", max_digits=10, decimal_places=2, read_only=True)
    stock_qty = serializers.SerializerMethodField()
    inventory = serializers.SerializerMethodField()
    barcode = serializers.CharField(source="product.barcode", read_only=True)
    status = serializers.CharField(source="product.status", read_only=True)
    created_at = serializers.DateTimeField(source="product.created_at", read_only=True)
    publisher_id = serializers.IntegerField(source="publisher.publisher_id", read_only=True)
    publisher_name = serializers.CharField(source="publisher.publisher_name", read_only=True)
    supplier_links = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()
    translators = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "product_id",
            "product_name",
            "category_id",
            "category_name",
            "unit",
            "unit_price",
            "cost_price",
            "stock_qty",
            "inventory",
            "barcode",
            "status",
            "created_at",
            "isbn",
            "publisher_id",
            "publisher_name",
            "publish_date",
            "edition",
            "language",
            "page_count",
            "authors",
            "translators",
            "supplier_links",
        ]

    def get_supplier_links(self, instance):
        links = instance.product.supplier_links.all()
        return SupplierLinkReadSerializer(links, many=True).data

    def get_stock_qty(self, instance):
        return product_stock_total(instance.product)

    def get_inventory(self, instance):
        rows = instance.product.inventories.select_related("store").all()
        return InventoryReadSerializer(rows, many=True).data

    def get_authors(self, instance):
        links = instance.author_links.all()
        return [
            {
                "author_id": link.author.author_id,
                "author_name": link.author.author_name,
                "author_order": link.author_order,
            }
            for link in links
        ]

    def get_translators(self, instance):
        links = instance.translator_links.all()
        return [
            {
                "translator_id": link.translator.translator_id,
                "translator_name": link.translator.translator_name,
            }
            for link in links
        ]


class BookWriteSerializer(ProductWriteSerializer):
    isbn = serializers.CharField(max_length=20)
    publisher_id = serializers.IntegerField()
    publish_date = serializers.DateField(required=False, allow_null=True, validators=[validate_publish_date])
    edition = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)
    language = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)
    page_count = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    author_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=False)
    translator_ids = serializers.ListField(child=serializers.IntegerField(), required=False, allow_empty=True)


class BookAuthorReadSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.author_id", read_only=True)
    author_name = serializers.CharField(source="author.author_name", read_only=True)

    class Meta:
        model = BookAuthor
        fields = ["author_id", "author_name", "author_order"]


class BookTranslatorReadSerializer(serializers.ModelSerializer):
    translator_id = serializers.IntegerField(source="translator.translator_id", read_only=True)
    translator_name = serializers.CharField(source="translator.translator_name", read_only=True)

    class Meta:
        model = BookTranslator
        fields = ["translator_id", "translator_name"]
