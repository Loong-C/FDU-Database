from rest_framework import status

from catalog.models import Author, Book, Category, Product, Publisher, Supplier, Translator
from catalog.serializers import (
    AuthorSerializer,
    BookReadSerializer,
    BookWriteSerializer,
    CategorySerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
    PublisherSerializer,
    SupplierSerializer,
    TranslatorSerializer,
)
from catalog.services import (
    category_descendant_ids,
    create_book,
    create_product,
    update_book,
    update_product,
)
from common.exceptions import ConflictError
from common.permissions import CatalogPermission
from common.response import success_response
from common.viewsets import StandardizedModelViewSet


class BaseCatalogViewSet(StandardizedModelViewSet):
    permission_classes = [CatalogPermission]


class SupplierViewSet(BaseCatalogViewSet):
    queryset = Supplier.objects.all().order_by("supplier_id")
    serializer_class = SupplierSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        if status_value:
            queryset = queryset.filter(status=status_value)
        if search:
            queryset = queryset.filter(supplier_name__icontains=search)
        return queryset

    def perform_destroy(self, instance):
        if instance.supplier_links.exists():
            raise ConflictError("存在关联商品，当前供应商不能删除。")
        instance.delete()


class CategoryViewSet(BaseCatalogViewSet):
    queryset = Category.objects.select_related("parent_category").all().order_by("category_id")
    serializer_class = CategorySerializer

    def perform_destroy(self, instance):
        if instance.products.exists():
            raise ConflictError("存在关联商品，当前分类不能删除。")
        instance.delete()


class PublisherViewSet(BaseCatalogViewSet):
    queryset = Publisher.objects.all().order_by("publisher_id")
    serializer_class = PublisherSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(publisher_name__icontains=search)
        return queryset

    def perform_destroy(self, instance):
        if instance.books.exists():
            raise ConflictError("存在关联图书，当前出版社不能删除。")
        instance.delete()


class AuthorViewSet(BaseCatalogViewSet):
    queryset = Author.objects.all().order_by("author_id")
    serializer_class = AuthorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(author_name__icontains=search)
        return queryset

    def perform_destroy(self, instance):
        if instance.book_links.exists():
            raise ConflictError("存在关联图书，当前作者不能删除。")
        instance.delete()


class TranslatorViewSet(BaseCatalogViewSet):
    queryset = Translator.objects.all().order_by("translator_id")
    serializer_class = TranslatorSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(translator_name__icontains=search)
        return queryset

    def perform_destroy(self, instance):
        if instance.book_links.exists():
            raise ConflictError("存在关联图书，当前译者不能删除。")
        instance.delete()


class ProductViewSet(BaseCatalogViewSet):
    queryset = (
        Product.objects.select_related("category")
        .prefetch_related("supplier_links__supplier", "inventories__store")
        .all()
        .order_by("product_id")
    )

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get("category_id")
        status_value = self.request.query_params.get("status")
        search = self.request.query_params.get("search")
        if category_id:
            # 选父分类时一并匹配其下所有子分类，避免商品挂在叶子分类时父分类筛选返回空。
            queryset = queryset.filter(category_id__in=category_descendant_ids(category_id))
        if status_value:
            queryset = queryset.filter(status=status_value)
        if search:
            queryset = queryset.filter(product_name__icontains=search)
        return queryset

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return ProductReadSerializer
        return ProductWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = ProductWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_product(serializer.validated_data)
        return success_response(ProductReadSerializer(instance).data, "Created", status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = ProductWriteSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = update_product(instance, serializer.validated_data)
        return success_response(ProductReadSerializer(instance).data, "Updated")

    def perform_destroy(self, instance):
        if hasattr(instance, "book"):
            raise ConflictError("图书类商品请使用 books 接口删除。")
        if instance.sale_items.exists():
            raise ConflictError("存在关联销售记录，当前商品不能删除。")
        instance.delete()


class BookViewSet(BaseCatalogViewSet):
    queryset = Book.objects.select_related("product__category", "publisher").prefetch_related(
        "product__supplier_links__supplier",
        "product__inventories__store",
        "author_links__author",
        "translator_links__translator",
    ).all().order_by("product_id")

    def get_queryset(self):
        queryset = super().get_queryset()
        publisher_id = self.request.query_params.get("publisher_id")
        category_id = self.request.query_params.get("category_id")
        search = self.request.query_params.get("search")
        if publisher_id:
            queryset = queryset.filter(publisher_id=publisher_id)
        if category_id:
            queryset = queryset.filter(product__category_id__in=category_descendant_ids(category_id))
        if search:
            queryset = queryset.filter(product__product_name__icontains=search)
        return queryset

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return BookReadSerializer
        return BookWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = BookWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = create_book(serializer.validated_data)
        return success_response(BookReadSerializer(instance).data, "Created", status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = BookWriteSerializer(instance=instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = update_book(instance, serializer.validated_data)
        return success_response(BookReadSerializer(instance).data, "Updated")

    def perform_destroy(self, instance):
        if instance.product.sale_items.exists():
            raise ConflictError("存在关联销售记录，当前图书不能删除。")
        instance.product.delete()
