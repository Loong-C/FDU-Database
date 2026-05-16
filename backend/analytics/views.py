from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncDate
from rest_framework.views import APIView

from analytics.serializers import (
    CategorySummaryQuerySerializer,
    MemberRankQuerySerializer,
    ProductRankQuerySerializer,
    StoreDailyQuerySerializer,
)
from catalog.services import category_descendant_ids
from common.datetime_filters import apply_local_date_range, build_local_date_bounds
from common.permissions import AnalyticsPermission
from common.response import success_response
from customers.models import Member
from sales.models import Sale, SaleItem


class StoreDailyAnalyticsView(APIView):
    permission_classes = [AnalyticsPermission]

    def get(self, request):
        serializer = StoreDailyQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        queryset = Sale.objects.select_related("store").all()
        if params.get("store_id"):
            queryset = queryset.filter(store_id=params["store_id"])
        queryset = apply_local_date_range(
            queryset,
            "sale_time",
            params.get("date_from"),
            params.get("date_to"),
        )

        data = list(
            queryset.annotate(sale_date=TruncDate("sale_time"))
            .values("store_id", "store__store_name", "sale_date")
            .annotate(
                order_count=Count("sale_id"),
                total_amount_sum=Coalesce(Sum("total_amount"), Value(Decimal("0.00"))),
                discount_amount_sum=Coalesce(Sum("discount_amount"), Value(Decimal("0.00"))),
                actual_amount_sum=Coalesce(Sum("actual_amount"), Value(Decimal("0.00"))),
            )
            .order_by("sale_date", "store_id")
        )
        for row in data:
            row["store_name"] = row.pop("store__store_name")
        return success_response(data)


class ProductRankAnalyticsView(APIView):
    permission_classes = [AnalyticsPermission]

    def get(self, request):
        serializer = ProductRankQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        queryset = SaleItem.objects.select_related("sale", "product").all()
        if params.get("store_id"):
            queryset = queryset.filter(sale__store_id=params["store_id"])
        if params.get("category_id"):
            queryset = queryset.filter(
                product__category_id__in=category_descendant_ids(params["category_id"])
            )
        queryset = apply_local_date_range(
            queryset,
            "sale__sale_time",
            params.get("date_from"),
            params.get("date_to"),
        )

        data = list(
            queryset.values(
                "product_id",
                "product__product_name",
                "product__status",
            )
            .annotate(
                total_qty=Coalesce(Sum("quantity"), 0),
                total_sales_amount=Coalesce(
                    Sum("line_amount"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=12, decimal_places=2)),
                ),
            )
            .order_by("-total_sales_amount", "-total_qty")[: params["limit"]]
        )
        for row in data:
            row["product_name"] = row.pop("product__product_name")
            row["status"] = row.pop("product__status")
        return success_response(data)


class MemberRankAnalyticsView(APIView):
    permission_classes = [AnalyticsPermission]

    def get(self, request):
        serializer = MemberRankQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        sale_filter = Q()
        start, end = build_local_date_bounds(params.get("date_from"), params.get("date_to"))
        queryset = Member.objects.select_related("customer").all()
        if params.get("level"):
            queryset = queryset.filter(level=params["level"])
        if start:
            sale_filter &= Q(customer__sales__sale_time__gte=start)
        if end:
            sale_filter &= Q(customer__sales__sale_time__lte=end)

        data = list(
            queryset.values(
                "customer_id",
                "customer__customer_name",
                "member_no",
                "level",
            )
            .annotate(
                order_count=Count("customer__sales", filter=sale_filter, distinct=True),
                total_spending=Coalesce(
                    Sum(
                        "customer__sales__actual_amount",
                        filter=sale_filter,
                    ),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=12, decimal_places=2)),
                ),
            )
            .order_by("-total_spending", "-order_count")[: params["limit"]]
        )
        for row in data:
            row["customer_name"] = row.pop("customer__customer_name")
        return success_response(data)


class CategorySummaryAnalyticsView(APIView):
    permission_classes = [AnalyticsPermission]

    def get(self, request):
        serializer = CategorySummaryQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        params = serializer.validated_data
        queryset = SaleItem.objects.select_related("sale", "product__category").all()
        queryset = apply_local_date_range(
            queryset,
            "sale__sale_time",
            params.get("date_from"),
            params.get("date_to"),
        )

        data = list(
            queryset.values("product__category_id", "product__category__category_name")
            .annotate(
                total_qty=Coalesce(Sum("quantity"), 0),
                total_sales_amount=Coalesce(
                    Sum("line_amount"),
                    Value(Decimal("0.00"), output_field=DecimalField(max_digits=12, decimal_places=2)),
                ),
            )
            .order_by("-total_sales_amount")
        )
        for row in data:
            row["category_id"] = row.pop("product__category_id")
            row["category_name"] = row.pop("product__category__category_name")
        return success_response(data)
