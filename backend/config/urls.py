from django.contrib import admin
from django.http import Http404, HttpResponse
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache

from .settings import REPO_ROOT


@never_cache
def frontend_app(request):
    index_path = REPO_ROOT / "frontend" / "dist" / "index.html"
    if not index_path.exists():
        raise Http404("Frontend build not found. Run `npm.cmd run build` in frontend first.")
    return HttpResponse(index_path.read_text(encoding="utf-8"), content_type="text/html")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("accounts.urls")),
    path("api/v1/", include("stores.urls")),
    path("api/v1/", include("catalog.urls")),
    path("api/v1/", include("customers.urls")),
    path("api/v1/", include("sales.urls")),
    path("api/v1/", include("analytics.urls")),
    re_path(r"^(?!api/|admin/|assets/).*$", frontend_app),
]
