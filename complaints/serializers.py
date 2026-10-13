from rest_framework import serializers

from .models import Complaint, ComplaintComment


class ComplaintSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    customer = serializers.StringRelatedField()
    assigned_to = serializers.StringRelatedField()

    class Meta:
        model = Complaint
        fields = [
            "reference_number",
            "title",
            "description",
            "category",
            "customer",
            "assigned_to",
            "priority",
            "status",
            "created_at",
            "updated_at",
            "resolved_at",
        ]
        read_only_fields = fields


class ComplaintCommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = ComplaintComment
        fields = ["id", "text", "is_internal_note", "author", "created_at"]
        read_only_fields = fields
