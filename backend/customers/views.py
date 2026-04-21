from rest_framework import status

from common.exceptions import ConflictError
from common.permissions import CustomerSalesPermission
from common.response import success_response
from common.viewsets import StandardizedModelViewSet
from customers.models import Customer, Member
from customers.serializers import CustomerSerializer, MemberReadSerializer, MemberWriteSerializer
from customers.services import create_member, update_member


class CustomerViewSet(StandardizedModelViewSet):
    queryset = Customer.objects.all().order_by("customer_id")
    serializer_class = CustomerSerializer
    permission_classes = [CustomerSalesPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        if status_value:
            queryset = queryset.filter(status=status_value)
        if search:
            queryset = queryset.filter(customer_name__icontains=search)
        return queryset

    def perform_destroy(self, instance):
        if hasattr(instance, "member"):
            raise ConflictError("客户已绑定会员，不能直接删除。")
        if instance.sales.exists():
            raise ConflictError("存在关联销售记录，当前客户不能删除。")
        instance.delete()


class MemberViewSet(StandardizedModelViewSet):
    queryset = Member.objects.select_related("customer").all().order_by("customer_id")
    permission_classes = [CustomerSalesPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        level = self.request.query_params.get("level")
        search = self.request.query_params.get("search")
        if level:
            queryset = queryset.filter(level=level)
        if search:
            queryset = queryset.filter(customer__customer_name__icontains=search)
        return queryset

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return MemberReadSerializer
        return MemberWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = MemberWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_member(serializer.validated_data)
        return success_response(MemberReadSerializer(instance).data, "Created", status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = MemberWriteSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = update_member(instance, serializer.validated_data)
        return success_response(MemberReadSerializer(instance).data, "Updated")
