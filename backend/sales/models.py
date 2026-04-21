from django.db import models


class Sale(models.Model):
    PAYMENT_CASH = "cash"
    PAYMENT_CARD = "card"
    PAYMENT_WECHAT = "wechat"
    PAYMENT_ALIPAY = "alipay"
    PAYMENT_MIXED = "mixed"
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, "Cash"),
        (PAYMENT_CARD, "Card"),
        (PAYMENT_WECHAT, "WeChat"),
        (PAYMENT_ALIPAY, "Alipay"),
        (PAYMENT_MIXED, "Mixed"),
    ]

    sale_id = models.BigAutoField(primary_key=True)
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.RESTRICT,
        db_column="store_id",
        related_name="sales",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        db_column="customer_id",
        related_name="sales",
        null=True,
        blank=True,
    )
    sale_time = models.DateTimeField()
    payment_method = models.CharField(max_length=30, choices=PAYMENT_CHOICES)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "sale"
        ordering = ["-sale_time", "-sale_id"]


class SaleItem(models.Model):
    pk = models.CompositePrimaryKey("sale", "line_no")
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        db_column="sale_id",
        related_name="items",
    )
    line_no = models.IntegerField()
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.RESTRICT,
        db_column="product_id",
        related_name="sale_items",
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = "sale_item"
        ordering = ["sale_id", "line_no"]
