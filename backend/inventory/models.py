from django.db import models
from django.utils import timezone


class Inventory(models.Model):
    pk = models.CompositePrimaryKey("store", "product")
    store = models.ForeignKey(
        "stores.Store",
        on_delete=models.RESTRICT,
        db_column="store_id",
        related_name="inventories",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.RESTRICT,
        db_column="product_id",
        related_name="inventories",
    )
    stock_qty = models.IntegerField(default=0)
    safety_stock_qty = models.IntegerField(default=0)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "inventory"
        ordering = ["store_id", "product_id"]
