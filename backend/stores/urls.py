from django.urls import include, path
from rest_framework.routers import DefaultRouter

from stores.views import StoreViewSet

router = DefaultRouter(trailing_slash=False)
router.register("stores", StoreViewSet, basename="stores")

urlpatterns = [
    path("", include(router.urls)),
]
