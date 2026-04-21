from django.urls import include, path
from rest_framework.routers import DefaultRouter

from customers.views import CustomerViewSet, MemberViewSet

router = DefaultRouter(trailing_slash=False)
router.register("customers", CustomerViewSet, basename="customers")
router.register("members", MemberViewSet, basename="members")

urlpatterns = [
    path("", include(router.urls)),
]
