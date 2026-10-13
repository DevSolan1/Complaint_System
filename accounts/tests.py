from django.test import TestCase
from django.urls import reverse

from .models import User


class UserModelTests(TestCase):
    def test_default_role_is_customer(self):
        user = User.objects.create_user(username="alice", password="pass12345")
        self.assertTrue(user.is_customer)
        self.assertFalse(user.is_agent)
        self.assertFalse(user.is_manager)

    def test_manager_role_flag(self):
        user = User.objects.create_user(username="mgr", password="pass12345", role=User.Role.MANAGER)
        self.assertTrue(user.is_manager)

    def test_superuser_is_always_manager(self):
        user = User.objects.create_superuser(username="root", password="pass12345", email="root@example.com")
        self.assertTrue(user.is_manager)


class RegistrationViewTests(TestCase):
    def test_registration_creates_customer(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newcustomer",
                "email": "newcustomer@example.com",
                "phone": "555-0100",
                "first_name": "New",
                "last_name": "Customer",
                "password1": "Str0ngPassw0rd!",
                "password2": "Str0ngPassw0rd!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newcustomer")
        self.assertTrue(user.is_customer)
