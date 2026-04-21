from django.db import models
from django.utils import timezone


class Customer(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    customer_id = models.BigAutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    register_time = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        managed = False
        db_table = "customer"
        ordering = ["customer_id"]

    def __str__(self) -> str:
        return self.customer_name


class Member(models.Model):
    LEVEL_BRONZE = "bronze"
    LEVEL_SILVER = "silver"
    LEVEL_GOLD = "gold"
    LEVEL_PLATINUM = "platinum"
    LEVEL_CHOICES = [
        (LEVEL_BRONZE, "Bronze"),
        (LEVEL_SILVER, "Silver"),
        (LEVEL_GOLD, "Gold"),
        (LEVEL_PLATINUM, "Platinum"),
    ]

    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        db_column="customer_id",
        primary_key=True,
        related_name="member",
    )
    member_no = models.CharField(max_length=50, unique=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    points = models.IntegerField(default=0)
    join_date = models.DateField()

    class Meta:
        managed = False
        db_table = "member"
        ordering = ["customer_id"]
