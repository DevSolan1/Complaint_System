"""Authentication views: registration, login, logout."""
from django.contrib.auth import login
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomerRegistrationForm


class RegisterView(CreateView):
    """Public registration page. New accounts are always Customers."""

    form_class = CustomerRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginView(DjangoLoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy("home")
