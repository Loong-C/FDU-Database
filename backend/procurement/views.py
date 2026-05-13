from rest_framework import status

from common.exceptions import ConflictError
from common.permissions import CustomerSalesPermission
from common.response import success_response
from common.viewsets import StandardizedModelViewSet
from procurement.models import PurchaseOrder, StockIn
from procurement.serializers import (
    PurchaseOrderReadSerializer,
    PurchaseOrderWriteSerializer,
    StockInReadSerializer,
    StockInWriteSerializer,
)
from procurement.services import (
    create_purchase_order,
    create_stock_in,
    update_purchase_order,
    update_stock_in,
)


class PurchaseOrderViewSet(StandardizedModelViewSet):
    queryset = PurchaseOrder.objects.select_related("supplier", "store", "created_by").prefetch_related(
        "items__product"
    )
    permission_classes = [CustomerSalesPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        supplier_id = self.request.query_params.get("supplier_id")
        store_id = self.request.query_params.get("store_id")
        status_value = self.request.query_params.get("status")
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return PurchaseOrderReadSerializer
        return PurchaseOrderWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = PurchaseOrderWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_purchase_order(serializer.validated_data, request.user)
        return success_response(PurchaseOrderReadSerializer(instance).data, "Created", status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = PurchaseOrderWriteSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = update_purchase_order(instance, serializer.validated_data)
        return success_response(PurchaseOrderReadSerializer(instance).data, "Updated")

    def perform_destroy(self, instance):
        if instance.stock_ins.exists():
            raise ConflictError("已生成入库单的采购单不能删除。")
        instance.delete()


class StockInViewSet(StandardizedModelViewSet):
    queryset = StockIn.objects.select_related("purchase_order", "store", "operator").prefetch_related("items__product")
    permission_classes = [CustomerSalesPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        purchase_order_id = self.request.query_params.get("purchase_order_id")
        store_id = self.request.query_params.get("store_id")
        status_value = self.request.query_params.get("status")
        if purchase_order_id:
            queryset = queryset.filter(purchase_order_id=purchase_order_id)
        if store_id:
            queryset = queryset.filter(store_id=store_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return StockInReadSerializer
        return StockInWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = StockInWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_stock_in(serializer.validated_data, request.user)
        return success_response(StockInReadSerializer(instance).data, "Created", status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = StockInWriteSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = update_stock_in(instance, serializer.validated_data)
        return success_response(StockInReadSerializer(instance).data, "Updated")

    def perform_destroy(self, instance):
        if instance.status == StockIn.STATUS_APPROVED:
            raise ConflictError("已审核入库单不能删除。")
        instance.delete()
