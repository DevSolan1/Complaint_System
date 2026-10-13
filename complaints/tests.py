from django.core import mail
from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Category, Complaint, StatusHistory


class ComplaintModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Billing")
        self.customer = User.objects.create_user(
            username="cust1", password="pass12345", email="cust1@example.com"
        )

    def test_reference_number_auto_generated(self):
        complaint = Complaint.objects.create(
            title="Overcharged",
            description="I was overcharged on my invoice.",
            category=self.category,
            customer=self.customer,
        )
        self.assertTrue(complaint.reference_number.startswith("COMP-"))

    def test_reference_numbers_increment(self):
        first = Complaint.objects.create(
            title="A", description="d", category=self.category, customer=self.customer
        )
        second = Complaint.objects.create(
            title="B", description="d", category=self.category, customer=self.customer
        )
        first_seq = int(first.reference_number.rsplit("-", 1)[-1])
        second_seq = int(second.reference_number.rsplit("-", 1)[-1])
        self.assertEqual(second_seq, first_seq + 1)

    def test_submission_sends_email(self):
        mail.outbox = []
        Complaint.objects.create(
            title="Late delivery", description="d", category=self.category, customer=self.customer
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("submitted", mail.outbox[0].subject)


class ComplaintAccessControlTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Technical")
        self.customer_a = User.objects.create_user(username="custa", password="pass12345")
        self.customer_b = User.objects.create_user(username="custb", password="pass12345")
        self.agent = User.objects.create_user(username="agent1", password="pass12345", role=User.Role.AGENT)
        self.manager = User.objects.create_user(
            username="mgr1", password="pass12345", role=User.Role.MANAGER
        )
        self.complaint = Complaint.objects.create(
            title="Bug report",
            description="Something broke",
            category=self.category,
            customer=self.customer_a,
            assigned_to=self.agent,
        )

    def test_owner_can_view(self):
        self.client.login(username="custa", password="pass12345")
        response = self.client.get(self.complaint.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_other_customer_cannot_view(self):
        self.client.login(username="custb", password="pass12345")
        response = self.client.get(self.complaint.get_absolute_url())
        self.assertEqual(response.status_code, 403)

    def test_assigned_agent_can_view(self):
        self.client.login(username="agent1", password="pass12345")
        response = self.client.get(self.complaint.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_manager_can_view_any_complaint(self):
        self.client.login(username="mgr1", password="pass12345")
        response = self.client.get(self.complaint.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_customer_cannot_access_update_view(self):
        self.client.login(username="custa", password="pass12345")
        response = self.client.get(reverse("complaints:update", args=[self.complaint.reference_number]))
        self.assertEqual(response.status_code, 403)

    def test_status_change_creates_history_entry(self):
        self.client.login(username="agent1", password="pass12345")
        self.client.post(
            reverse("complaints:update", args=[self.complaint.reference_number]),
            {"status": Complaint.Status.IN_PROGRESS, "priority": Complaint.Priority.MEDIUM},
        )
        self.assertEqual(StatusHistory.objects.filter(complaint=self.complaint).count(), 1)
