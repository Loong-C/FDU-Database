from collections import defaultdict
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from catalog.models import Product
from customers.models import Customer
from inventory.services import apply_inventory_deltas
from sales.models import Sale, SaleItem
from stores.models import Store


def _get_product_map(product_ids):
    products = Product.objects.filter(product_id__in=product_ids)
    product_map = {product.product_id: product for product in products}
    missing = [product_id for product_id in product_ids if product_id not in product_map]
    if missing:
        raise serializers.ValidationError({"items": f"以下商品不存在: {missing}"})
    return product_map


def _build_sale_items(items_payload, product_map):
    total_amount = Decimal("0.00")
    line_items = []
    for line_no, item in enumerate(items_payload, start=1):
        product = product_map[item["product_id"]]
        quantity = item["quantity"]
        unit_price = product.unit_price
        line_amount = unit_price * quantity
        total_amount += line_amount
        line_items.append(
            {
                "line_no": line_no,
                "product": product,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_amount": line_amount,
            }
        )
    return line_items, total_amount


def _deltas_for_items(store_id, items, multiplier):
    deltas = defaultdict(int)
    for item in items:
        product_id = item["product_id"] if isinstance(item, dict) else item.product_id
        quantity = item["quantity"] if isinstance(item, dict) else item.quantity
        deltas[(store_id, product_id)] += multiplier * quantity
    return deltas


def create_sale(validated_data):
    items_payload = validated_data["items"]
    store = Store.objects.get(pk=validated_data["store_id"])
    customer = None
    if validated_data.get("customer_id") is not None:
        customer = Customer.objects.get(pk=validated_data["customer_id"])
    discount_amount = validated_data.get("discount_amount", Decimal("0.00"))

    with transaction.atomic():
        product_map = _get_product_map([item["product_id"] for item in items_payload])
        line_items, total_amount = _build_sale_items(items_payload, product_map)
        if discount_amount > total_amount:
            raise serializers.ValidationError({"discount_amount": "优惠金额不能大于原始总额。"})
        apply_inventory_deltas(_deltas_for_items(store.store_id, items_payload, -1))

        sale = Sale.objects.create(
            store=store,
            customer=customer,
            sale_time=validated_data["sale_time"],
            payment_method=validated_data["payment_method"],
            total_amount=total_amount,
            discount_amount=discount_amount,
            actual_amount=total_amount - discount_amount,
        )
        SaleItem.objects.bulk_create(
            [
                SaleItem(
                    sale=sale,
                    line_no=item["line_no"],
                    product=item["product"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    line_amount=item["line_amount"],
                )
                for item in line_items
            ]
        )
        return sale


def update_sale(instance, validated_data):
    with transaction.atomic():
        existing_items = list(instance.items.select_related("product").all())
        items_payload = validated_data.get("items")
        new_store = instance.store
        if "store_id" in validated_data:
            new_store = Store.objects.get(pk=validated_data["store_id"])

        items_changed = items_payload is not None
        store_changed = new_store.store_id != instance.store_id
        effective_items = items_payload
        if store_changed and effective_items is None:
            effective_items = [
                {"product_id": item.product_id, "quantity": item.quantity}
                for item in existing_items
            ]

        if effective_items is not None:
            product_map = _get_product_map([item["product_id"] for item in effective_items])
            line_items, total_amount = _build_sale_items(effective_items, product_map)
        else:
            line_items = None
            total_amount = instance.total_amount

        discount_amount = validated_data.get("discount_amount", instance.discount_amount)
        if discount_amount > total_amount:
            raise serializers.ValidationError({"discount_amount": "优惠金额不能大于原始总额。"})

        if items_changed or store_changed:
            deltas = defaultdict(int)
            for key, delta in _deltas_for_items(instance.store_id, existing_items, 1).items():
                deltas[key] += delta
            for key, delta in _deltas_for_items(new_store.store_id, effective_items, -1).items():
                deltas[key] += delta
            apply_inventory_deltas(deltas)

        if "store_id" in validated_data:
            instance.store = new_store
        if "customer_id" in validated_data:
            customer_id = validated_data["customer_id"]
            instance.customer = Customer.objects.get(pk=customer_id) if customer_id is not None else None
        if "sale_time" in validated_data:
            instance.sale_time = validated_data["sale_time"]
        if "payment_method" in validated_data:
            instance.payment_method = validated_data["payment_method"]
        instance.total_amount = total_amount
        instance.discount_amount = discount_amount
        instance.actual_amount = total_amount - discount_amount
        instance.save()

        if line_items is not None:
            instance.items.all().delete()
            SaleItem.objects.bulk_create(
                [
                    SaleItem(
                        sale=instance,
                        line_no=item["line_no"],
                        product=item["product"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        line_amount=item["line_amount"],
                    )
                    for item in line_items
                ]
            )
        return instance


def delete_sale(instance):
    with transaction.atomic():
        existing_items = list(instance.items.select_related("product").all())
        apply_inventory_deltas(_deltas_for_items(instance.store_id, existing_items, 1))
        instance.delete()
