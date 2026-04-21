from django.urls import include, path
from rest_framework.routers import DefaultRouter

from sales.views import SaleViewSet

router = DefaultRouter(trailing_slash=False)
router.register("sales", SaleViewSet, basename="sales")

urlpatterns = [
    path("", include(router.urls)),
]
