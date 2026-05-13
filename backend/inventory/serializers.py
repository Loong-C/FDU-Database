from rest_framework import serializers

from inventory.models import Inventory


class InventoryReadSerializer(serializers.ModelSerializer):
    store_id = serializers.IntegerField(source="store.store_id", read_only=True)
    store_name = serializers.CharField(source="store.store_name", read_only=True)
    product_id = serializers.IntegerField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_status = serializers.CharField(source="product.status", read_only=True)

    class Meta:
        model = Inventory
        fields = [
            "store_id",
            "store_name",
            "product_id",
            "product_name",
            "product_status",
            "stock_qty",
            "safety_stock_qty",
            "updated_at",
        ]


class InventoryUpdateSerializer(serializers.Serializer):
    stock_qty = serializers.IntegerField(min_value=0, required=False)
    safety_stock_qty = serializers.IntegerField(min_value=0, required=False)
