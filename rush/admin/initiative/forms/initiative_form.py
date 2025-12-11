from django import forms
from rush.models.initiative import Initiative


class InitiativeForm(forms.ModelForm):
    class Meta:
        model = Initiative
        fields = "__all__"
