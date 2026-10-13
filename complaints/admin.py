from django.contrib import admin

from .models import Attachment, Category, Complaint, ComplaintComment, StatusHistory


class ComplaintCommentInline(admin.TabularInline):
    model = ComplaintComment
    extra = 0
    readonly_fields = ("author", "created_at")


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_by", "changed_at")
    can_delete = False


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ("uploaded_by", "uploaded_at")


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "reference_number",
        "title",
        "category",
        "customer",
        "assigned_to",
        "priority",
        "status",
        "created_at",
    )
    list_filter = ("status", "priority", "category")
    search_fields = ("reference_number", "title", "description", "customer__username")
    readonly_fields = ("reference_number", "created_at", "updated_at")
    inlines = [ComplaintCommentInline, StatusHistoryInline, AttachmentInline]
    date_hierarchy = "created_at"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ComplaintComment)
class ComplaintCommentAdmin(admin.ModelAdmin):
    list_display = ("complaint", "author", "is_internal_note", "created_at")
    list_filter = ("is_internal_note",)


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("complaint", "old_status", "new_status", "changed_by", "changed_at")
