from django.urls import path

from analytics.views import (
    CategorySummaryAnalyticsView,
    MemberRankAnalyticsView,
    ProductRankAnalyticsView,
    StoreDailyAnalyticsView,
)

urlpatterns = [
    path("analytics/stores/daily", StoreDailyAnalyticsView.as_view(), name="analytics-store-daily"),
    path("analytics/products/rank", ProductRankAnalyticsView.as_view(), name="analytics-product-rank"),
    path("analytics/members/rank", MemberRankAnalyticsView.as_view(), name="analytics-member-rank"),
    path("analytics/categories/summary", CategorySummaryAnalyticsView.as_view(), name="analytics-category-summary"),
]
