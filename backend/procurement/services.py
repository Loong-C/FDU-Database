from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from catalog.models import Product, Supplier
from inventory.services import apply_inventory_deltas
from procurement.models import PurchaseOrder, PurchaseOrderItem, StockIn, StockInItem, SystemUser
from stores.models import Store


def _validate_related_ids(model, ids, field_name):
    existing = model.objects.in_bulk(ids)
    missing = [value for value in ids if value not in existing]
    if missing:
        raise serializers.ValidationError({field_name: f"以下ID不存在: {missing}"})
    return existing


def _resolve_system_user(user_id=None, request_user=None):
    if user_id is not None:
        user = SystemUser.objects.filter(pk=user_id).first()
        if not user:
            raise serializers.ValidationError({"created_by": "系统用户不存在。"})
        return user
    if request_user is not None and getattr(request_user, "is_authenticated", False):
        user = SystemUser.objects.filter(username=request_user.username).first()
        if user:
            return user
    user = SystemUser.objects.order_by("user_id").first()
    if not user:
        raise serializers.ValidationError({"created_by": "缺少 system_user 基础数据。"})
    return user


def _build_purchase_items(items_payload, product_map, price_field):
    total_amount = Decimal("0.00")
    line_items = []
    for line_no, item in enumerate(items_payload, start=1):
        product = product_map[item["product_id"]]
        quantity = item["quantity"]
        price = item[price_field]
        line_amount = price * quantity
        total_amount += line_amount
        line_items.append(
            {
                "line_no": line_no,
                "product": product,
                "quantity": quantity,
                "price": price,
                "line_amount": line_amount,
            }
        )
    return line_items, total_amount


def create_purchase_order(validated_data, request_user=None):
    items_payload = validated_data["items"]
    supplier = Supplier.objects.filter(pk=validated_data["supplier_id"]).first()
    if not supplier:
        raise serializers.ValidationError({"supplier_id": "供应商不存在。"})
    store = Store.objects.filter(pk=validated_data["store_id"]).first()
    if not store:
        raise serializers.ValidationError({"store_id": "门店不存在。"})
    created_by = _resolve_system_user(validated_data.get("created_by"), request_user)
    products = _validate_related_ids(Product, [item["product_id"] for item in items_payload], "items")
    line_items, total_amount = _build_purchase_items(items_payload, products, "purchase_price")

    with transaction.atomic():
        purchase_order = PurchaseOrder.objects.create(
            supplier=supplier,
            store=store,
            created_by=created_by,
            order_time=validated_data["order_time"],
            status=validated_data.get("status", PurchaseOrder.STATUS_DRAFT),
            total_amount=total_amount,
        )
        PurchaseOrderItem.objects.bulk_create(
            [
                PurchaseOrderItem(
                    purchase_order=purchase_order,
                    line_no=item["line_no"],
                    product=item["product"],
                    quantity=item["quantity"],
                    purchase_price=item["price"],
                    line_amount=item["line_amount"],
                )
                for item in line_items
            ]
        )
        return purchase_order


def update_purchase_order(instance, validated_data):
    if instance.stock_ins.exists():
        raise serializers.ValidationError("已生成入库单的采购单不能修改。")
    items_payload = validated_data.pop("items", None)

    if "supplier_id" in validated_data:
        supplier = Supplier.objects.filter(pk=validated_data.pop("supplier_id")).first()
        if not supplier:
            raise serializers.ValidationError({"supplier_id": "供应商不存在。"})
        instance.supplier = supplier
    if "store_id" in validated_data:
        store = Store.objects.filter(pk=validated_data.pop("store_id")).first()
        if not store:
            raise serializers.ValidationError({"store_id": "门店不存在。"})
        instance.store = store
    if "created_by" in validated_data:
        instance.created_by = _resolve_system_user(validated_data.pop("created_by"))
    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    with transaction.atomic():
        if items_payload is not None:
            products = _validate_related_ids(Product, [item["product_id"] for item in items_payload], "items")
            line_items, total_amount = _build_purchase_items(items_payload, products, "purchase_price")
            instance.total_amount = total_amount
            instance.items.all().delete()
            PurchaseOrderItem.objects.bulk_create(
                [
                    PurchaseOrderItem(
                        purchase_order=instance,
                        line_no=item["line_no"],
                        product=item["product"],
                        quantity=item["quantity"],
                        purchase_price=item["price"],
                        line_amount=item["line_amount"],
                    )
                    for item in line_items
                ]
            )
        instance.save()
        return instance


def create_stock_in(validated_data, request_user=None):
    items_payload = validated_data["items"]
    purchase_order = PurchaseOrder.objects.filter(pk=validated_data["purchase_order_id"]).first()
    if not purchase_order:
        raise serializers.ValidationError({"purchase_order_id": "采购单不存在。"})
    store_id = validated_data.get("store_id", purchase_order.store_id)
    store = Store.objects.filter(pk=store_id).first()
    if not store:
        raise serializers.ValidationError({"store_id": "门店不存在。"})
    operator = _resolve_system_user(validated_data.get("operator_id"), request_user)
    products = _validate_related_ids(Product, [item["product_id"] for item in items_payload], "items")
    line_items, _ = _build_purchase_items(items_payload, products, "unit_cost")
    status = validated_data.get("status", StockIn.STATUS_PENDING)

    with transaction.atomic():
        stock_in = StockIn.objects.create(
            purchase_order=purchase_order,
            store=store,
            operator=operator,
            inbound_time=validated_data["inbound_time"],
            status=status,
        )
        StockInItem.objects.bulk_create(
            [
                StockInItem(
                    stock_in=stock_in,
                    line_no=item["line_no"],
                    product=item["product"],
                    quantity=item["quantity"],
                    unit_cost=item["price"],
                    line_amount=item["line_amount"],
                )
                for item in line_items
            ]
        )
        if status == StockIn.STATUS_APPROVED:
            apply_inventory_deltas(
                {(store.store_id, item["product"].product_id): item["quantity"] for item in line_items},
                allow_create_positive=True,
            )
        return stock_in


def update_stock_in(instance, validated_data):
    if instance.status == StockIn.STATUS_APPROVED:
        raise serializers.ValidationError("已审核入库单不能修改。")
    items_payload = validated_data.pop("items", None)
    next_status = validated_data.get("status", instance.status)

    if "purchase_order_id" in validated_data:
        purchase_order = PurchaseOrder.objects.filter(pk=validated_data.pop("purchase_order_id")).first()
        if not purchase_order:
            raise serializers.ValidationError({"purchase_order_id": "采购单不存在。"})
        instance.purchase_order = purchase_order
    if "store_id" in validated_data:
        store = Store.objects.filter(pk=validated_data.pop("store_id")).first()
        if not store:
            raise serializers.ValidationError({"store_id": "门店不存在。"})
        instance.store = store
    if "operator_id" in validated_data:
        instance.operator = _resolve_system_user(validated_data.pop("operator_id"))
    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    with transaction.atomic():
        if items_payload is not None:
            products = _validate_related_ids(Product, [item["product_id"] for item in items_payload], "items")
            line_items, _ = _build_purchase_items(items_payload, products, "unit_cost")
            instance.items.all().delete()
            StockInItem.objects.bulk_create(
                [
                    StockInItem(
                        stock_in=instance,
                        line_no=item["line_no"],
                        product=item["product"],
                        quantity=item["quantity"],
                        unit_cost=item["price"],
                        line_amount=item["line_amount"],
                    )
                    for item in line_items
                ]
            )
        else:
            line_items = [
                {"product": item.product, "quantity": item.quantity}
                for item in instance.items.select_related("product").all()
            ]
        instance.save()
        if next_status == StockIn.STATUS_APPROVED:
            apply_inventory_deltas(
                {(instance.store_id, item["product"].product_id): item["quantity"] for item in line_items},
                allow_create_positive=True,
            )
        return instance
