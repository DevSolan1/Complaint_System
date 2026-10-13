"""Views for submitting, listing, viewing, and updating complaints."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import staff_required

from .forms import CommentForm, ComplaintFilterForm, ComplaintForm, ComplaintUpdateForm
from .models import Complaint, StatusHistory


def _visible_queryset(user):
    """Return the complaints a given user is allowed to see."""
    if user.is_manager:
        return Complaint.objects.all()
    if user.is_agent:
        return Complaint.objects.filter(assigned_to=user)
    return Complaint.objects.filter(customer=user)


@login_required
def complaint_list(request):
    """List complaints visible to the current user, with search & filters."""
    form = ComplaintFilterForm(request.GET or None)
    queryset = _visible_queryset(request.user).select_related("category", "assigned_to", "customer")

    if form.is_valid():
        data = form.cleaned_data
        if data.get("q"):
            from django.db.models import Q

            q = data["q"]
            queryset = queryset.filter(
                Q(reference_number__icontains=q) | Q(title__icontains=q) | Q(description__icontains=q)
            )
        if data.get("status"):
            queryset = queryset.filter(status=data["status"])
        if data.get("priority"):
            queryset = queryset.filter(priority=data["priority"])
        if data.get("category"):
            queryset = queryset.filter(category=data["category"])
        if data.get("assigned_to"):
            queryset = queryset.filter(assigned_to=data["assigned_to"])
        if data.get("date_from"):
            queryset = queryset.filter(created_at__date__gte=data["date_from"])
        if data.get("date_to"):
            queryset = queryset.filter(created_at__date__lte=data["date_to"])

    paginator = Paginator(queryset, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "complaints/list.html",
        {"page_obj": page_obj, "filter_form": form},
    )


@login_required
def complaint_create(request):
    """Customers submit a new complaint. Staff may also log one on a customer's behalf."""
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.customer = request.user
            complaint.save()
            messages.success(
                request, f"Complaint submitted successfully. Reference: {complaint.reference_number}"
            )
            return redirect(complaint.get_absolute_url())
    else:
        form = ComplaintForm()
    return render(request, "complaints/form.html", {"form": form})


def _can_view(user, complaint: Complaint) -> bool:
    if user.is_manager:
        return True
    if user.is_agent:
        return complaint.assigned_to_id == user.id
    return complaint.customer_id == user.id


@login_required
def complaint_detail(request, ref_number: str):
    complaint = get_object_or_404(
        Complaint.objects.select_related("category", "assigned_to", "customer"),
        reference_number=ref_number,
    )
    if not _can_view(request.user, complaint):
        raise PermissionDenied("You do not have access to this complaint.")

    is_staff_viewer = request.user.is_agent or request.user.is_manager
    comments = complaint.comments.select_related("author")
    if not is_staff_viewer:
        comments = comments.filter(is_internal_note=False)

    if request.method == "POST":
        comment_form = CommentForm(request.POST, allow_internal=is_staff_viewer)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.complaint = complaint
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
            return redirect(complaint.get_absolute_url())
    else:
        comment_form = CommentForm(allow_internal=is_staff_viewer)

    return render(
        request,
        "complaints/detail.html",
        {
            "complaint": complaint,
            "comments": comments,
            "comment_form": comment_form,
            "status_history": complaint.status_history.select_related("changed_by"),
            "is_staff_viewer": is_staff_viewer,
        },
    )


@staff_required
def complaint_update(request, ref_number: str):
    """Agents/managers update status, priority, and assignment."""
    complaint = get_object_or_404(Complaint, reference_number=ref_number)

    if request.user.is_agent and complaint.assigned_to_id != request.user.id:
        raise PermissionDenied("You can only update complaints assigned to you.")

    old_status = complaint.status

    if request.method == "POST":
        form = ComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            updated = form.save(commit=False)
            if updated.status in (Complaint.Status.RESOLVED, Complaint.Status.CLOSED) and not updated.resolved_at:
                updated.resolved_at = timezone.now()
            updated.save()

            if old_status != updated.status:
                StatusHistory.objects.create(
                    complaint=updated,
                    old_status=old_status,
                    new_status=updated.status,
                    changed_by=request.user,
                )
            messages.success(request, "Complaint updated.")
            return redirect(complaint.get_absolute_url())
    else:
        form = ComplaintUpdateForm(instance=complaint)

    return render(request, "complaints/update.html", {"form": form, "complaint": complaint})
