from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product
from apps.feedback.models import ContactRequest
from apps.orders.models import Order


class AdminApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            name="Администратор",
            password="strongpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            name="Покупатель",
            password="strongpass123",
        )
        self.token = Token.objects.create(user=self.admin)
        self.category = Category.objects.create(name="Торты", slug="cakes", sort_order=1)
        self.product = Product.objects.create(
            category=self.category,
            name="Медовик",
            slug="medovik",
            description="Классический торт",
            price="2200.00",
            original_price="2500.00",
            weight="1 кг",
            image_url="https://example.com/medovik.jpg",
            allergens="Молоко, яйца",
        )
        self.order = Order.objects.create(
            user=self.user,
            status=Order.Status.NEW,
            delivery_method=Order.DeliveryMethod.PICKUP,
            contact_name="Покупатель",
            phone="+79990000000",
            subtotal="2200.00",
            delivery_price="0.00",
            total="2200.00",
            personal_data_consent=True,
        )
        ContactRequest.objects.create(
            name="Анна",
            email="anna@example.com",
            phone="+79991112233",
            message="Хочу заказать торт",
            personal_data_consent=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_dashboard_returns_real_data(self):
        response = self.client.get("/api/admin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["products"]), 1)
        self.assertEqual(len(response.data["users"]), 2)
        self.assertEqual(len(response.data["orders"]), 1)
        self.assertEqual(len(response.data["feedback"]), 1)

    def test_create_and_update_product(self):
        create_response = self.client.post(
            "/api/admin/products/",
            {
                "name": "Наполеон",
                "description": "Слоеный торт",
                "price": "2300.00",
                "original_price": "2600.00",
                "weight": "1.1 кг",
                "image_url": "https://example.com/napoleon.jpg",
                "badge": "new",
                "allergens": "Глютен",
                "is_month_pick": True,
                "category_slug": self.category.slug,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        product_id = create_response.data["id"]

        update_response = self.client.post(
            "/api/admin/products/",
            {
                "id": product_id,
                "name": "Наполеон обновленный",
                "slug": "napoleon-new",
                "description": "Слоеный торт",
                "price": "2400.00",
                "original_price": "2600.00",
                "weight": "1.2 кг",
                "image_url": "https://example.com/napoleon.jpg",
                "badge": "hit",
                "allergens": "Глютен",
                "is_month_pick": False,
                "category_slug": self.category.slug,
            },
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "Наполеон обновленный")

    def test_update_user_and_order_status(self):
        user_response = self.client.put(
            f"/api/admin/users/{self.user.id}/",
            {
                "email": "updated@example.com",
                "name": "Новый клиент",
                "phone": "+78889990000",
                "is_admin": True,
            },
            format="json",
        )
        self.assertEqual(user_response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)

        order_response = self.client.patch(
            f"/api/admin/orders/{self.user.id}/{self.order.id}/",
            {"status": Order.Status.COOKING},
            format="json",
        )
        self.assertEqual(order_response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.COOKING)

    def test_delete_product_and_user(self):
        delete_product_response = self.client.delete(f"/api/admin/products/{self.product.id}/")
        self.assertEqual(delete_product_response.status_code, status.HTTP_204_NO_CONTENT)

        delete_user_response = self.client.delete(f"/api/admin/users/{self.user.id}/")
        self.assertEqual(delete_user_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_admin_is_forbidden(self):
        client = self.client_class()
        user_token = Token.objects.create(user=self.user)
        client.credentials(HTTP_AUTHORIZATION=f"Token {user_token.key}")
        response = client.get("/api/admin/dashboard/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

