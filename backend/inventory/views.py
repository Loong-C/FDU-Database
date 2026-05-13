from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView

from common.permissions import CatalogPermission
from common.response import success_response
from inventory.models import Inventory
from inventory.serializers import InventoryReadSerializer, InventoryUpdateSerializer


class InventoryListView(APIView):
    permission_classes = [CatalogPermission]

    def get(self, request):
        queryset = Inventory.objects.select_related("store", "product").all()
        store_id = request.query_params.get("store_id")
        product_id = request.query_params.get("product_id")
        warning = request.query_params.get("warning")
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if warning and warning.lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(stock_qty__lte=models.F("safety_stock_qty"))

        serializer = InventoryReadSerializer(queryset, many=True)
        return success_response(
            {
                "items": serializer.data,
                "total": len(serializer.data),
                "page": 1,
                "page_size": len(serializer.data),
            }
        )


class InventoryWarningView(APIView):
    permission_classes = [CatalogPermission]

    def get(self, request):
        queryset = (
            Inventory.objects.select_related("store", "product")
            .filter(stock_qty__lte=models.F("safety_stock_qty"))
            .order_by("store_id", "stock_qty", "product_id")
        )
        serializer = InventoryReadSerializer(queryset, many=True)
        return success_response(serializer.data)


class InventoryDetailView(APIView):
    permission_classes = [CatalogPermission]

    def get_object(self, store_id, product_id):
        return get_object_or_404(
            Inventory.objects.select_related("store", "product"),
            store_id=store_id,
            product_id=product_id,
        )

    def get(self, request, store_id, product_id):
        inventory = self.get_object(store_id, product_id)
        return success_response(InventoryReadSerializer(inventory).data)

    def patch(self, request, store_id, product_id):
        inventory = self.get_object(store_id, product_id)
        serializer = InventoryUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(inventory, field, value)
        inventory.save()
        return success_response(InventoryReadSerializer(inventory).data, "Updated", status.HTTP_200_OK)
