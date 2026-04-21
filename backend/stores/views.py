from common.exceptions import ConflictError
from common.permissions import CatalogPermission
from common.viewsets import StandardizedModelViewSet
from stores.models import Store
from stores.serializers import StoreSerializer


class StoreViewSet(StandardizedModelViewSet):
    queryset = Store.objects.all().order_by("store_id")
    serializer_class = StoreSerializer
    permission_classes = [CatalogPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        city = self.request.query_params.get("city")
        search = self.request.query_params.get("search")
        if city:
            queryset = queryset.filter(city__icontains=city)
        if search:
            queryset = queryset.filter(store_name__icontains=search)
        return queryset

    def perform_destroy(self, instance):
        if instance.sales.exists():
            raise ConflictError("存在关联销售记录，当前门店不能删除。")
        instance.delete()
