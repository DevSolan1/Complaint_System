"""Signal handlers that send email notifications for key complaint events."""
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Complaint, ComplaintComment


def _notify(subject: str, message: str, recipient_email: str) -> None:
    if not recipient_email:
        return
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        fail_silently=True,
    )


@receiver(post_save, sender=Complaint)
def notify_on_complaint_change(sender, instance: Complaint, created: bool, **kwargs) -> None:
    if created:
        _notify(
            subject=f"Complaint {instance.reference_number} submitted",
            message=(
                f"Hi {instance.customer.get_full_name() or instance.customer.username},\n\n"
                f"Your complaint '{instance.title}' has been received and assigned "
                f"reference number {instance.reference_number}. We will keep you "
                f"updated on its progress."
            ),
            recipient_email=instance.customer.email,
        )
    else:
        _notify(
            subject=f"Complaint {instance.reference_number} updated",
            message=(
                f"Hi {instance.customer.get_full_name() or instance.customer.username},\n\n"
                f"Your complaint '{instance.title}' ({instance.reference_number}) "
                f"status is now: {instance.get_status_display()}."
            ),
            recipient_email=instance.customer.email,
        )
        if instance.assigned_to:
            _notify(
                subject=f"Complaint {instance.reference_number} assigned to you",
                message=(
                    f"Hi {instance.assigned_to.get_full_name() or instance.assigned_to.username},\n\n"
                    f"Complaint '{instance.title}' ({instance.reference_number}) has been "
                    f"assigned to you. Priority: {instance.get_priority_display()}."
                ),
                recipient_email=instance.assigned_to.email,
            )


@receiver(post_save, sender=ComplaintComment)
def notify_on_new_comment(sender, instance: ComplaintComment, created: bool, **kwargs) -> None:
    if not created or instance.is_internal_note:
        return
    complaint = instance.complaint
    # Notify the customer unless they authored the comment themselves.
    if instance.author_id != complaint.customer_id:
        _notify(
            subject=f"New comment on complaint {complaint.reference_number}",
            message=(
                f"Hi {complaint.customer.get_full_name() or complaint.customer.username},\n\n"
                f"A new comment was added to your complaint '{complaint.title}':\n\n"
                f"{instance.text}"
            ),
            recipient_email=complaint.customer.email,
        )
    # Notify the assigned agent if someone else commented.
    if complaint.assigned_to and instance.author_id != complaint.assigned_to_id:
        _notify(
            subject=f"New comment on complaint {complaint.reference_number}",
            message=(
                f"Hi {complaint.assigned_to.get_full_name() or complaint.assigned_to.username},\n\n"
                f"A new comment was added to complaint '{complaint.title}':\n\n"
                f"{instance.text}"
            ),
            recipient_email=complaint.assigned_to.email,
        )
