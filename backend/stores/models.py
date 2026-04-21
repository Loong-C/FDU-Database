from django.db import models
from django.utils import timezone


class Store(models.Model):
    store_id = models.BigAutoField(primary_key=True)
    store_name = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, unique=True, null=True, blank=True)
    manager_name = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "store"
        ordering = ["store_id"]

    def __str__(self) -> str:
        return self.store_name
