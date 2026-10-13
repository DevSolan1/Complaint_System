"""Custom user model with role-based access control."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model supporting Customer, Agent, and Manager roles."""

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        AGENT = "agent", "Support Agent"
        MANAGER = "manager", "Manager"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CUSTOMER
    )
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_customer(self) -> bool:
        return self.role == self.Role.CUSTOMER

    @property
    def is_agent(self) -> bool:
        return self.role == self.Role.AGENT

    @property
    def is_manager(self) -> bool:
        return self.role == self.Role.MANAGER or self.is_superuser
