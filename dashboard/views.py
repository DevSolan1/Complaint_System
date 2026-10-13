"""Role-based dashboard: customer summary, agent workload, manager analytics."""
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, F
from django.shortcuts import render
from django.utils import timezone

from complaints.models import Category, Complaint


@login_required
def dashboard_home(request):
    user = request.user
    if user.is_manager:
        return _manager_dashboard(request)
    if user.is_agent:
        return _agent_dashboard(request)
    return _customer_dashboard(request)


def _customer_dashboard(request):
    complaints = Complaint.objects.filter(customer=request.user)
    context = {
        "complaints": complaints[:10],
        "total": complaints.count(),
        "open_count": complaints.exclude(
            status__in=[Complaint.Status.RESOLVED, Complaint.Status.CLOSED, Complaint.Status.REJECTED]
        ).count(),
        "resolved_count": complaints.filter(status=Complaint.Status.RESOLVED).count(),
    }
    return render(request, "dashboard/customer_dashboard.html", context)


def _agent_dashboard(request):
    complaints = Complaint.objects.filter(assigned_to=request.user)
    context = {
        "complaints": complaints,
        "total": complaints.count(),
        "open_count": complaints.filter(status=Complaint.Status.OPEN).count(),
        "in_progress_count": complaints.filter(status=Complaint.Status.IN_PROGRESS).count(),
        "pending_count": complaints.filter(status=Complaint.Status.PENDING).count(),
    }
    return render(request, "dashboard/agent_dashboard.html", context)


def _manager_dashboard(request):
    complaints = Complaint.objects.all()
    resolved = complaints.filter(resolved_at__isnull=False).annotate(
        duration=F("resolved_at") - F("created_at")
    )
    avg_resolution = resolved.aggregate(avg=Avg("duration"))["avg"]

    by_category = (
        complaints.values("category__name").annotate(total=Count("id")).order_by("-total")
    )
    by_priority = complaints.values("priority").annotate(total=Count("id")).order_by("-total")

    context = {
        "total": complaints.count(),
        "open_count": complaints.filter(status=Complaint.Status.OPEN).count(),
        "in_progress_count": complaints.filter(status=Complaint.Status.IN_PROGRESS).count(),
        "resolved_count": complaints.filter(status=Complaint.Status.RESOLVED).count(),
        "closed_count": complaints.filter(status=Complaint.Status.CLOSED).count(),
        "avg_resolution": avg_resolution,
        "by_category": by_category,
        "by_priority": by_priority,
        "categories": Category.objects.all(),
        "recent_complaints": complaints.order_by("-created_at")[:10],
        "now": timezone.now(),
    }
    return render(request, "dashboard/manager_dashboard.html", context)
