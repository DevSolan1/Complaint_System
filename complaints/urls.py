from django.urls import path

from . import views

app_name = "complaints"

urlpatterns = [
    path("", views.complaint_list, name="list"),
    path("new/", views.complaint_create, name="create"),
    path("<str:ref_number>/", views.complaint_detail, name="detail"),
    path("<str:ref_number>/update/", views.complaint_update, name="update"),
]
