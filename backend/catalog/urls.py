from django.urls import include, path
from rest_framework.routers import DefaultRouter

from catalog.views import (
    AuthorViewSet,
    BookViewSet,
    CategoryViewSet,
    ProductViewSet,
    PublisherViewSet,
    SupplierViewSet,
    TranslatorViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("suppliers", SupplierViewSet, basename="suppliers")
router.register("categories", CategoryViewSet, basename="categories")
router.register("publishers", PublisherViewSet, basename="publishers")
router.register("authors", AuthorViewSet, basename="authors")
router.register("translators", TranslatorViewSet, basename="translators")
router.register("products", ProductViewSet, basename="products")
router.register("books", BookViewSet, basename="books")

urlpatterns = [
    path("", include(router.urls)),
]
