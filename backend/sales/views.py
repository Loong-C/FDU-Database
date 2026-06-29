from rest_framework import status

from common.permissions import CustomerSalesPermission
from common.response import success_response
from common.viewsets import StandardizedModelViewSet
from common.datetime_filters import apply_local_date_range
from sales.models import Sale
from sales.serializers import SaleQuerySerializer, SaleReadSerializer, SaleWriteSerializer
from sales.services import create_sale, delete_sale, update_sale


class SaleViewSet(StandardizedModelViewSet):
    queryset = Sale.objects.select_related("store", "customer").prefetch_related("items__product").all().order_by("-sale_time", "-sale_id")
    permission_classes = [CustomerSalesPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        serializer = SaleQuerySerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        if params.get("store_id"):
            queryset = queryset.filter(store_id=params["store_id"])
        if params.get("customer_id"):
            queryset = queryset.filter(customer_id=params["customer_id"])
        if params.get("payment_method"):
            queryset = queryset.filter(payment_method=params["payment_method"])
        queryset = apply_local_date_range(queryset, "sale_time", params.get("date_from"), params.get("date_to"))
        return queryset

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return SaleReadSerializer
        return SaleWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = SaleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_sale(serializer.validated_data)
        return success_response(SaleReadSerializer(instance).data, "Created", status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = SaleWriteSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = update_sale(instance, serializer.validated_data)
        return success_response(SaleReadSerializer(instance).data, "Updated")

    def perform_destroy(self, instance):
        delete_sale(instance)
