from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class DashboardRoutingTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="c1", password="pass12345")
        self.agent = User.objects.create_user(username="a1", password="pass12345", role=User.Role.AGENT)
        self.manager = User.objects.create_user(
            username="m1", password="pass12345", role=User.Role.MANAGER
        )

    def test_customer_sees_customer_dashboard(self):
        self.client.login(username="c1", password="pass12345")
        response = self.client.get(reverse("dashboard:home"))
        self.assertTemplateUsed(response, "dashboard/customer_dashboard.html")

    def test_agent_sees_agent_dashboard(self):
        self.client.login(username="a1", password="pass12345")
        response = self.client.get(reverse("dashboard:home"))
        self.assertTemplateUsed(response, "dashboard/agent_dashboard.html")

    def test_manager_sees_manager_dashboard(self):
        self.client.login(username="m1", password="pass12345")
        response = self.client.get(reverse("dashboard:home"))
        self.assertTemplateUsed(response, "dashboard/manager_dashboard.html")

    def test_anonymous_redirected_to_login(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)
