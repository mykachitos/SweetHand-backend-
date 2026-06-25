from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.admin_api.serializers import (
    AdminOrderSerializer,
    AdminOrderStatusSerializer,
    AdminProductWriteSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    get_admin_dashboard_payload,
)
from apps.catalog.models import Product
from apps.orders.models import Order


User = get_user_model()


class IsStaffAdmin(permissions.BasePermission):
    message = "Доступ только для администратора."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


class AdminDashboardAPIView(APIView):
    permission_classes = [IsStaffAdmin]

    def get(self, request):
        return Response(get_admin_dashboard_payload(request))


class AdminProductUpsertAPIView(APIView):
    permission_classes = [IsStaffAdmin]

    def post(self, request):
        product_id = request.data.get("id")
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            serializer = AdminProductWriteSerializer(product, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                AdminProductWriteSerializer(serializer.instance).data,
                status=status.HTTP_200_OK,
            )

        serializer = AdminProductWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdminProductDeleteAPIView(APIView):
    permission_classes = [IsStaffAdmin]

    def delete(self, request, product_id):
        product = get_object_or_404(Product, pk=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserUpdateAPIView(APIView):
    permission_classes = [IsStaffAdmin]

    def put(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        serializer = AdminUserUpdateSerializer(user, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        annotated_user = User.objects.annotate(orders_count=Count("orders")).get(pk=user.pk)
        return Response(AdminUserSerializer(annotated_user).data)

    def delete(self, request, user_id):
        if request.user.pk == user_id:
            return Response(
                {"detail": "Нельзя удалить текущего администратора."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, pk=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUserDeleteAPIView(AdminUserUpdateAPIView):
    pass


class AdminOrderStatusAPIView(APIView):
    permission_classes = [IsStaffAdmin]

    def patch(self, request, user_id, order_id):
        order = get_object_or_404(Order.objects.select_related("user"), pk=order_id, user_id=user_id)
        serializer = AdminOrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AdminOrderSerializer(order).data)
