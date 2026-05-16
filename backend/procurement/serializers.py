from decimal import Decimal

from rest_framework import serializers

from procurement.models import PurchaseOrder, PurchaseOrderItem, StockIn, StockInItem


class PurchaseOrderItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    purchase_price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))


class PurchaseOrderItemReadSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = ["line_no", "product_id", "product_name", "quantity", "purchase_price", "line_amount"]


class PurchaseOrderReadSerializer(serializers.ModelSerializer):
    supplier_id = serializers.IntegerField(source="supplier.supplier_id", read_only=True)
    supplier_name = serializers.CharField(source="supplier.supplier_name", read_only=True)
    store_id = serializers.IntegerField(source="store.store_id", read_only=True)
    store_name = serializers.CharField(source="store.store_name", read_only=True)
    created_by = serializers.IntegerField(source="created_by.user_id", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    items = PurchaseOrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "purchase_order_id",
            "supplier_id",
            "supplier_name",
            "store_id",
            "store_name",
            "created_by",
            "created_by_name",
            "order_time",
            "status",
            "total_amount",
            "items",
        ]


class PurchaseOrderWriteSerializer(serializers.Serializer):
    supplier_id = serializers.IntegerField(required=False)
    store_id = serializers.IntegerField(required=False)
    created_by = serializers.IntegerField(required=False)
    order_time = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=PurchaseOrder.STATUS_CHOICES, required=False)
    items = PurchaseOrderItemInputSerializer(many=True, required=False)

    def validate_items(self, value):
        product_ids = [item["product_id"] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("同一采购单中商品不能重复。")
        return value

    def validate(self, attrs):
        if self.instance is None:
            required = ["supplier_id", "store_id", "order_time", "items"]
            missing = [field for field in required if field not in attrs]
            if missing:
                raise serializers.ValidationError({field: "该字段为必填。" for field in missing})
        return attrs


class StockInItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))


class StockInItemReadSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.product_id", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)

    class Meta:
        model = StockInItem
        fields = ["line_no", "product_id", "product_name", "quantity", "unit_cost", "line_amount"]


class StockInReadSerializer(serializers.ModelSerializer):
    purchase_order_id = serializers.IntegerField(source="purchase_order.purchase_order_id", read_only=True)
    store_id = serializers.IntegerField(source="store.store_id", read_only=True)
    store_name = serializers.CharField(source="store.store_name", read_only=True)
    operator_id = serializers.IntegerField(source="operator.user_id", read_only=True)
    operator_name = serializers.CharField(source="operator.username", read_only=True)
    items = StockInItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = StockIn
        fields = [
            "stock_in_id",
            "purchase_order_id",
            "store_id",
            "store_name",
            "operator_id",
            "operator_name",
            "inbound_time",
            "status",
            "items",
        ]


class StockInWriteSerializer(serializers.Serializer):
    purchase_order_id = serializers.IntegerField(required=False)
    store_id = serializers.IntegerField(required=False)
    operator_id = serializers.IntegerField(required=False)
    inbound_time = serializers.DateTimeField(required=False)
    status = serializers.ChoiceField(choices=StockIn.STATUS_CHOICES, required=False)
    items = StockInItemInputSerializer(many=True, required=False)

    def validate_items(self, value):
        product_ids = [item["product_id"] for item in value]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("同一入库单中商品不能重复。")
        return value

    def validate(self, attrs):
        if self.instance is None:
            required = ["purchase_order_id", "inbound_time", "items"]
            missing = [field for field in required if field not in attrs]
            if missing:
                raise serializers.ValidationError({field: "该字段为必填。" for field in missing})
        return attrs
