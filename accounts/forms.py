"""Forms for user registration."""
from django import forms
from django.contrib.auth.forms import UserCreationForm

from .forms_mixins import BootstrapFormMixin
from .models import User


class CustomerRegistrationForm(BootstrapFormMixin, UserCreationForm):
    """Public self-registration form. Always creates a Customer role account."""

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER
        user.phone = self.cleaned_data.get("phone", "")
        if commit:
            user.save()
        return user


class StaffCreationForm(UserCreationForm):
    """Used by managers (via admin or a manager-only view) to create agent/manager accounts."""

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "department", "phone"]
