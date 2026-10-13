"""Helper utilities: reference number generation and file validation."""
import datetime
import os

from django.conf import settings
from django.core.exceptions import ValidationError


def validate_attachment(file) -> None:
    """Validate an uploaded attachment's extension and size.

    Raises ``ValidationError`` if the file is too large or has a
    disallowed extension.
    """
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(
            f"File too large. Maximum allowed size is {settings.MAX_UPLOAD_SIZE_MB}MB."
        )

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in settings.ALLOWED_ATTACHMENT_EXTENSIONS:
        allowed = ", ".join(settings.ALLOWED_ATTACHMENT_EXTENSIONS)
        raise ValidationError(f"Unsupported file type '{ext}'. Allowed types: {allowed}.")


def generate_reference_number(model_cls) -> str:
    """Generate a unique reference number like ``COMP-2026-00001``.

    Numbering resets each calendar year and is based on how many
    complaints already exist for that year.
    """
    year = datetime.date.today().year
    prefix = f"COMP-{year}-"
    last = (
        model_cls.objects.filter(reference_number__startswith=prefix)
        .order_by("-reference_number")
        .first()
    )
    if last:
        last_seq = int(last.reference_number.rsplit("-", 1)[-1])
    else:
        last_seq = 0
    return f"{prefix}{last_seq + 1:05d}"
