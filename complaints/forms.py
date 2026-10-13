"""Forms for submitting and managing complaints."""
from django import forms

from accounts.forms_mixins import BootstrapFormMixin
from accounts.models import User

from .models import Complaint, ComplaintComment


class ComplaintForm(BootstrapFormMixin, forms.ModelForm):
    """Used by customers to submit a new complaint."""

    class Meta:
        model = Complaint
        fields = ["title", "category", "priority", "description", "attachment"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class ComplaintUpdateForm(BootstrapFormMixin, forms.ModelForm):
    """Used by agents/managers to change status and assignment."""

    class Meta:
        model = Complaint
        fields = ["status", "assigned_to", "priority"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(
            role__in=[User.Role.AGENT, User.Role.MANAGER]
        )
        self.fields["assigned_to"].required = False
        self.apply_bootstrap()


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ComplaintComment
        fields = ["text", "is_internal_note"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3, "placeholder": "Add a comment..."})}

    def __init__(self, *args, allow_internal: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        if not allow_internal:
            self.fields.pop("is_internal_note")
        self.apply_bootstrap()


class ComplaintFilterForm(BootstrapFormMixin, forms.Form):
    """Search & filter controls for the complaint list view."""

    q = forms.CharField(required=False, label="Search")
    status = forms.ChoiceField(
        required=False, choices=[("", "All statuses")] + list(Complaint.Status.choices)
    )
    priority = forms.ChoiceField(
        required=False, choices=[("", "All priorities")] + list(Complaint.Priority.choices)
    )
    category = forms.ModelChoiceField(
        required=False, queryset=None, empty_label="All categories"
    )
    assigned_to = forms.ModelChoiceField(
        required=False, queryset=None, empty_label="Anyone"
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category  # local import to avoid circularity

        self.fields["category"].queryset = Category.objects.all()
        self.fields["assigned_to"].queryset = User.objects.filter(
            role__in=[User.Role.AGENT, User.Role.MANAGER]
        )
        self.apply_bootstrap()
