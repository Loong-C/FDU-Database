from django.urls import path

from inventory.views import InventoryDetailView, InventoryListView, InventoryWarningView

urlpatterns = [
    path("inventory", InventoryListView.as_view(), name="inventory-list"),
    path("inventory/warnings", InventoryWarningView.as_view(), name="inventory-warnings"),
    path("inventory/<int:store_id>/<int:product_id>", InventoryDetailView.as_view(), name="inventory-detail"),
]
