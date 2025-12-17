from django import forms
from rush.models.initiative import Initiative


class InitiativeForm(forms.ModelForm):
    """Override the default add/change page for the Initiative model admin."""
    class Meta:
        model = Initiative
        fields = "__all__"
