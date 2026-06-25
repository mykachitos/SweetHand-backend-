from io import StringIO

from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Category, Product


class AccountsApiTests(APITestCase):
    def test_register_login_and_profile(self):
        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "user@example.com",
                "name": "Test User",
                "phone": "+79990000000",
                "password": "strongpass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

        login_response = self.client.post(
            "/api/auth/login/",
            {"email": "user@example.com", "password": "strongpass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        token = login_response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        me_response = self.client.get("/api/auth/me/")
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "user@example.com")

        patch_response = self.client.patch("/api/auth/me/", {"name": "Updated Name"}, format="json")
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(email="user@example.com").name, "Updated Name")


class BootstrapProjectDataCommandTests(APITestCase):
    def test_bootstrap_project_data_loads_fixture_once(self):
        first_output = StringIO()
        second_output = StringIO()

        call_command("bootstrap_project_data", stdout=first_output)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(Product.objects.count(), 22)
        self.assertIn("Project data fixture loaded successfully.", first_output.getvalue())

        call_command("bootstrap_project_data", stdout=second_output)

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(Product.objects.count(), 22)
        self.assertIn("Skipped fixture load because the database already has data", second_output.getvalue())
