from django.db import models
from django.utils import timezone


class Supplier(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    supplier_id = models.BigAutoField(primary_key=True)
    supplier_name = models.CharField(max_length=100, unique=True)
    contact_name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        managed = False
        db_table = "supplier"
        ordering = ["supplier_id"]

    def __str__(self) -> str:
        return self.supplier_name


class Category(models.Model):
    category_id = models.BigAutoField(primary_key=True)
    category_name = models.CharField(max_length=100, unique=True)
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        db_column="parent_category_id",
        related_name="children",
        null=True,
        blank=True,
    )

    class Meta:
        managed = False
        db_table = "category"
        ordering = ["category_id"]

    def __str__(self) -> str:
        return self.category_name


class Publisher(models.Model):
    publisher_id = models.BigAutoField(primary_key=True)
    publisher_name = models.CharField(max_length=150, unique=True)
    contact_name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    website = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "publisher"
        ordering = ["publisher_id"]

    def __str__(self) -> str:
        return self.publisher_name


class Product(models.Model):
    STATUS_ONSALE = "onsale"
    STATUS_OFFSALE = "offsale"
    STATUS_DISCONTINUED = "discontinued"
    STATUS_CHOICES = [
        (STATUS_ONSALE, "On sale"),
        (STATUS_OFFSALE, "Off sale"),
        (STATUS_DISCONTINUED, "Discontinued"),
    ]

    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        db_column="category_id",
        related_name="products",
    )
    unit = models.CharField(max_length=20)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    barcode = models.CharField(max_length=50, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "product"
        ordering = ["product_id"]

    def __str__(self) -> str:
        return self.product_name


class Book(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        db_column="product_id",
        primary_key=True,
        related_name="book",
    )
    isbn = models.CharField(max_length=20, unique=True)
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.RESTRICT,
        db_column="publisher_id",
        related_name="books",
    )
    publish_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=20, null=True, blank=True)
    language = models.CharField(max_length=30, null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "book"
        ordering = ["product_id"]

    def __str__(self) -> str:
        return self.product.product_name


class Author(models.Model):
    author_id = models.BigAutoField(primary_key=True)
    author_name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "author"
        ordering = ["author_id"]

    def __str__(self) -> str:
        return self.author_name


class Translator(models.Model):
    translator_id = models.BigAutoField(primary_key=True)
    translator_name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        managed = False
        db_table = "translator"
        ordering = ["translator_id"]

    def __str__(self) -> str:
        return self.translator_name


class SupplierProduct(models.Model):
    pk = models.CompositePrimaryKey("supplier", "product")
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.RESTRICT,
        db_column="supplier_id",
        related_name="supplier_links",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.RESTRICT,
        db_column="product_id",
        related_name="supplier_links",
    )
    supply_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_qty = models.IntegerField(null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "supplier_product"
        ordering = ["supplier_id", "product_id"]


class BookAuthor(models.Model):
    pk = models.CompositePrimaryKey("product", "author")
    product = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        db_column="product_id",
        related_name="author_links",
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.RESTRICT,
        db_column="author_id",
        related_name="book_links",
    )
    author_order = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "book_author"
        ordering = ["product_id", "author_order", "author_id"]


class BookTranslator(models.Model):
    pk = models.CompositePrimaryKey("product", "translator")
    product = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        db_column="product_id",
        related_name="translator_links",
    )
    translator = models.ForeignKey(
        Translator,
        on_delete=models.RESTRICT,
        db_column="translator_id",
        related_name="book_links",
    )

    class Meta:
        managed = False
        db_table = "book_translator"
        ordering = ["product_id", "translator_id"]
