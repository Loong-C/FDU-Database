from decimal import Decimal

from rest_framework import serializers

from customers.models import Customer
from sales.models import Sale, SaleItem
from stores.models import Store


class SaleItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class SaleWriteSerializer(serializers.Serializer):
    store_id = serializers.IntegerField(required=False)
    customer_id = serializers.IntegerField(required=False, allow_null=True)
    sale_time = serializers.DateTimeField(required=False)
    payment_method = serializers.ChoiceField(choices=Sale.PAYMENT_CHOICES, required=False)
    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
    )
    items = SaleItemInputSerializer(many=True, required=False)

    def validate(self, attrs):
        if self.instance is None:
            required_fields = ["store_id", "sale_time", "payment_method", "items"]
            missing = [field for field in required_fields if field not in attrs]
            if missing:
                raise serializers.ValidationError({field: "该字段为必填。" for field in missing})

        if "store_id" in attrs and not Store.objects.filter(pk=attrs["store_id"]).exists():
            raise serializers.ValidationError({"store_id": "门店不存在。"})

        if "customer_id" in attrs:
            customer_id = attrs["customer_id"]
            if customer_id is not None and not Customer.objects.filter(pk=customer_id).exists():
                raise serializers.ValidationError({"customer_id": "客户不存在。"})

        items = attrs.get("items")
        if items is not None:
            product_ids = [item["product_id"] for item in items]
            if len(product_ids) != len(set(product_ids)):
                raise serializers.ValidationError({"items": "同一商品不能重复出现。"})
        return attrs


class SaleItemReadSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            "line_no",
            "product_id",
            "product_name",
            "quantity",
            "unit_price",
            "line_amount",
        ]


class SaleReadSerializer(serializers.ModelSerializer):
    store_id = serializers.IntegerField(source="store.store_id", read_only=True)
    store_name = serializers.CharField(source="store.store_name", read_only=True)
    customer_id = serializers.IntegerField(source="customer.customer_id", read_only=True, allow_null=True)
    customer_name = serializers.CharField(source="customer.customer_name", read_only=True, allow_null=True)
    items = SaleItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "sale_id",
            "store_id",
            "store_name",
            "customer_id",
            "customer_name",
            "sale_time",
            "payment_method",
            "total_amount",
            "discount_amount",
            "actual_amount",
            "items",
        ]
