from collections.abc import Mapping

from django.db.models import Sum
from rest_framework import serializers

from inventory.models import Inventory
from stores.models import Store


def get_default_store():
    return Store.objects.order_by("store_id").first()


def product_stock_total(product) -> int:
    total = product.inventories.aggregate(total=Sum("stock_qty"))["total"]
    return int(total or 0)


def inventory_rows_for_product(product):
    return product.inventories.select_related("store").all()


def set_initial_inventory(product, stock_qty=None, safety_stock_qty=0, store_id=None):
    if stock_qty is None:
        return None
    store = Store.objects.filter(pk=store_id).first() if store_id else get_default_store()
    if not store:
        return None

    inventory = Inventory.objects.filter(store=store, product=product).first()
    if inventory is None:
        inventory = Inventory(
            store=store,
            product=product,
            stock_qty=stock_qty,
            safety_stock_qty=safety_stock_qty or 0,
        )
    else:
        inventory.stock_qty = stock_qty
        if safety_stock_qty is not None:
            inventory.safety_stock_qty = safety_stock_qty
    inventory.save()
    return inventory


def apply_inventory_deltas(deltas: Mapping[tuple[int, int], int], allow_create_positive: bool = False):
    clean_deltas = {key: delta for key, delta in deltas.items() if delta}
    if not clean_deltas:
        return []

    store_ids = {store_id for store_id, _ in clean_deltas}
    product_ids = {product_id for _, product_id in clean_deltas}
    rows = Inventory.objects.select_for_update().select_related("product").filter(
        store_id__in=store_ids,
        product_id__in=product_ids,
    )
    inventory_map = {(row.store_id, row.product_id): row for row in rows}
    touched = []

    for key, delta in clean_deltas.items():
        inventory = inventory_map.get(key)
        if inventory is None:
            if allow_create_positive and delta >= 0:
                inventory = Inventory(
                    store_id=key[0],
                    product_id=key[1],
                    stock_qty=0,
                    safety_stock_qty=0,
                )
                inventory_map[key] = inventory
            else:
                raise serializers.ValidationError(
                    {"items": f"门店 {key[0]} 的商品 {key[1]} 尚未建立库存记录。"}
                )

        next_qty = inventory.stock_qty + delta
        if next_qty < 0:
            raise serializers.ValidationError(
                {"items": f"商品 {inventory.product.product_name} 库存不足，当前库存 {inventory.stock_qty}。"}
            )
        inventory.stock_qty = next_qty
        if inventory._state.adding:
            inventory.save()
        else:
            inventory.save(update_fields=["stock_qty"])
        touched.append(inventory)

    return touched
