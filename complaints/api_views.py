"""Minimal read-only JSON API for complaints, scoped by the requester's role."""
from rest_framework import viewsets

from .models import Complaint
from .serializers import ComplaintSerializer


class ComplaintViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            return Complaint.objects.all()
        if user.is_agent:
            return Complaint.objects.filter(assigned_to=user)
        return Complaint.objects.filter(customer=user)
