from django.urls import path

from apps.admin_api.views import (
    AdminDashboardAPIView,
    AdminOrderStatusAPIView,
    AdminProductDeleteAPIView,
    AdminProductUpsertAPIView,
    AdminUserDeleteAPIView,
    AdminUserUpdateAPIView,
)


urlpatterns = [
    path("dashboard/", AdminDashboardAPIView.as_view(), name="admin-dashboard"),
    path("products/", AdminProductUpsertAPIView.as_view(), name="admin-product-upsert"),
    path("products/<int:product_id>/", AdminProductDeleteAPIView.as_view(), name="admin-product-delete"),
    path("users/<int:user_id>/", AdminUserUpdateAPIView.as_view(), name="admin-user-update"),
    path("users/<int:user_id>/delete/", AdminUserDeleteAPIView.as_view(), name="admin-user-delete-alt"),
    path("users/<int:user_id>", AdminUserUpdateAPIView.as_view(), name="admin-user-update-no-slash"),
    path("orders/<int:user_id>/<int:order_id>/", AdminOrderStatusAPIView.as_view(), name="admin-order-status"),
]

