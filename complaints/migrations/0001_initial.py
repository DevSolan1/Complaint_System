import complaints.utils
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=110, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "verbose_name_plural": "Categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Complaint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference_number", models.CharField(editable=False, max_length=20, unique=True)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                (
                    "priority",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
                        default="medium",
                        max_length=10,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_progress", "In Progress"),
                            ("pending", "Pending (awaiting customer)"),
                            ("resolved", "Resolved"),
                            ("closed", "Closed"),
                            ("rejected", "Rejected"),
                        ],
                        default="open",
                        max_length=15,
                    ),
                ),
                (
                    "attachment",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="complaints/%Y/%m/",
                        validators=[complaints.utils.validate_attachment],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_complaints",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="complaints",
                        to="complaints.category",
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submitted_complaints",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="StatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "old_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("open", "Open"),
                            ("in_progress", "In Progress"),
                            ("pending", "Pending (awaiting customer)"),
                            ("resolved", "Resolved"),
                            ("closed", "Closed"),
                            ("rejected", "Rejected"),
                        ],
                        max_length=15,
                    ),
                ),
                (
                    "new_status",
                    models.CharField(
                        choices=[
                            ("open", "Open"),
                            ("in_progress", "In Progress"),
                            ("pending", "Pending (awaiting customer)"),
                            ("resolved", "Resolved"),
                            ("closed", "Closed"),
                            ("rejected", "Rejected"),
                        ],
                        max_length=15,
                    ),
                ),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "changed_by",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "complaint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_history",
                        to="complaints.complaint",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Status histories",
                "ordering": ["changed_at"],
            },
        ),
        migrations.CreateModel(
            name="ComplaintComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                (
                    "is_internal_note",
                    models.BooleanField(
                        default=False, help_text="Internal notes are only visible to agents and managers."
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                (
                    "complaint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="complaints.complaint",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="Attachment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "file",
                    models.FileField(
                        upload_to="complaints/extra/%Y/%m/", validators=[complaints.utils.validate_attachment]
                    ),
                ),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "complaint",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="complaints.complaint",
                    ),
                ),
                ("uploaded_by", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name="complaint",
            index=models.Index(fields=["status"], name="complaints__status_9b2b7e_idx"),
        ),
        migrations.AddIndex(
            model_name="complaint",
            index=models.Index(fields=["priority"], name="complaints__priorit_2f1e35_idx"),
        ),
        migrations.AddIndex(
            model_name="complaint",
            index=models.Index(fields=["reference_number"], name="complaints__referen_6a1b7f_idx"),
        ),
    ]
