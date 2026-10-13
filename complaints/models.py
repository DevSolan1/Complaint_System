"""Core data models for the Complaint Management System."""
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .utils import generate_reference_number, validate_attachment


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Complaint(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        PENDING = "pending", "Pending (awaiting customer)"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"
        REJECTED = "rejected", "Rejected"

    reference_number = models.CharField(max_length=20, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="complaints")
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submitted_complaints"
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_complaints",
    )
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    attachment = models.FileField(
        upload_to="complaints/%Y/%m/", blank=True, null=True, validators=[validate_attachment]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["reference_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.reference_number} — {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = generate_reference_number(Complaint)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("complaints:detail", kwargs={"ref_number": self.reference_number})

    @property
    def resolution_time(self):
        """Return timedelta between creation and resolution, or None."""
        if self.resolved_at:
            return self.resolved_at - self.created_at
        return None


class Attachment(models.Model):
    """Supports multiple file attachments per complaint (beyond the primary one)."""

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="complaints/extra/%Y/%m/", validators=[validate_attachment])
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Attachment for {self.complaint.reference_number}"


class ComplaintComment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    is_internal_note = models.BooleanField(
        default=False, help_text="Internal notes are only visible to agents and managers."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        kind = "Internal note" if self.is_internal_note else "Comment"
        return f"{kind} on {self.complaint.reference_number} by {self.author}"


class StatusHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="status_history")
    old_status = models.CharField(max_length=15, choices=Complaint.Status.choices, blank=True)
    new_status = models.CharField(max_length=15, choices=Complaint.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["changed_at"]
        verbose_name_plural = "Status histories"

    def __str__(self) -> str:
        return f"{self.complaint.reference_number}: {self.old_status} → {self.new_status}"
