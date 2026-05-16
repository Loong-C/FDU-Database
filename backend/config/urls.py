from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("accounts.urls")),
    path("api/v1/", include("stores.urls")),
    path("api/v1/", include("catalog.urls")),
    path("api/v1/", include("customers.urls")),
    path("api/v1/", include("inventory.urls")),
    path("api/v1/", include("procurement.urls")),
    path("api/v1/", include("sales.urls")),
    path("api/v1/", include("analytics.urls")),
]
