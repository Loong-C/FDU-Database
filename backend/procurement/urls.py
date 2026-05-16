from django.urls import include, path
from rest_framework.routers import DefaultRouter

from procurement.views import PurchaseOrderViewSet, StockInViewSet

router = DefaultRouter(trailing_slash=False)
router.register("purchase-orders", PurchaseOrderViewSet, basename="purchase-orders")
router.register("stock-ins", StockInViewSet, basename="stock-ins")

urlpatterns = [
    path("", include(router.urls)),
]
