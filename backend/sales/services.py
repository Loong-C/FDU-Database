from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from catalog.models import Product
from customers.models import Customer
from sales.models import Sale, SaleItem
from stores.models import Store


def _get_product_map(product_ids):
    products = Product.objects.select_for_update().filter(product_id__in=product_ids)
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
        if product.stock_qty < quantity:
            raise serializers.ValidationError(
                {"items": f"商品 {product.product_name} 库存不足，当前库存 {product.stock_qty}。"}
            )
        unit_price = product.unit_price
        line_amount = unit_price * quantity
        total_amount += line_amount
        product.stock_qty -= quantity
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
        for product in product_map.values():
            product.save(update_fields=["stock_qty"])
        return sale


def update_sale(instance, validated_data):
    with transaction.atomic():
        existing_items = list(instance.items.select_related("product").all())
        items_payload = validated_data.get("items")
        if items_payload is not None:
            tracked_product_ids = list({item.product_id for item in existing_items} | {row["product_id"] for row in items_payload})
            product_map = _get_product_map(tracked_product_ids)
            for existing in existing_items:
                product_map[existing.product_id].stock_qty += existing.quantity
            line_items, total_amount = _build_sale_items(items_payload, product_map)
        else:
            product_map = {}
            line_items = None
            total_amount = instance.total_amount

        discount_amount = validated_data.get("discount_amount", instance.discount_amount)
        if discount_amount > total_amount:
            raise serializers.ValidationError({"discount_amount": "优惠金额不能大于原始总额。"})

        if "store_id" in validated_data:
            instance.store = Store.objects.get(pk=validated_data["store_id"])
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
            for product in product_map.values():
                product.save(update_fields=["stock_qty"])
        return instance


def delete_sale(instance):
    with transaction.atomic():
        product_ids = [item.product_id for item in instance.items.select_related("product").all()]
        product_map = _get_product_map(product_ids) if product_ids else {}
        for item in instance.items.select_related("product").all():
            product_map[item.product_id].stock_qty += item.quantity
        for product in product_map.values():
            product.save(update_fields=["stock_qty"])
        instance.delete()
