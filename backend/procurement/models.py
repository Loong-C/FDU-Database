from django.db import models


class SystemUser(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_DISABLED = "disabled"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_DISABLED, "Disabled"),
    ]

    user_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=255)
    real_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "system_user"
        ordering = ["user_id"]


class PurchaseOrder(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SUBMITTED = "submitted"
    STATUS_APPROVED = "approved"
    STATUS_RECEIVED = "received"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_RECEIVED, "Received"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    purchase_order_id = models.BigAutoField(primary_key=True)
    supplier = models.ForeignKey(
        "catalog.Supplier",
        on_delete=models.RESTRICT,
        db_column="supplier_id",
        related_name="purchase_orders",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.RESTRICT,
        db_column="store_id",
        related_name="purchase_orders",
    )
    created_by = models.ForeignKey(
        SystemUser,
        on_delete=models.RESTRICT,
        db_column="created_by",
        related_name="purchase_orders",
    )
    order_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "purchase_order"
        ordering = ["-order_time", "-purchase_order_id"]


class PurchaseOrderItem(models.Model):
    pk = models.CompositePrimaryKey("purchase_order", "line_no")
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        db_column="purchase_order_id",
        related_name="items",
    )
    line_no = models.IntegerField()
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.RESTRICT,
        db_column="product_id",
        related_name="purchase_order_items",
    )
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "purchase_order_item"
        ordering = ["purchase_order_id", "line_no"]


class StockIn(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    stock_in_id = models.BigAutoField(primary_key=True)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.RESTRICT,
        db_column="purchase_order_id",
        related_name="stock_ins",
    )
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.RESTRICT,
        db_column="store_id",
        related_name="stock_ins",
    )
    operator = models.ForeignKey(
        SystemUser,
        on_delete=models.RESTRICT,
        db_column="operator_id",
        related_name="stock_ins",
    )
    inbound_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        managed = False
        db_table = "stock_in"
        ordering = ["-inbound_time", "-stock_in_id"]


class StockInItem(models.Model):
    pk = models.CompositePrimaryKey("stock_in", "line_no")
    stock_in = models.ForeignKey(
        StockIn,
        on_delete=models.CASCADE,
        db_column="stock_in_id",
        related_name="items",
    )
    line_no = models.IntegerField()
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.RESTRICT,
        db_column="product_id",
        related_name="stock_in_items",
    )
    quantity = models.IntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    line_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "stock_in_item"
        ordering = ["stock_in_id", "line_no"]
