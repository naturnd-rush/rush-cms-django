from django import forms
from django.contrib import admin
from django.db import models
from django_summernote.admin import SummernoteModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from rush import models
from rush.admin import utils


class InitiativeForm(forms.ModelForm):
    """
    Override the default add/change page for the Initiative model admin.
    """

    class Meta:
        model = models.Initiative
        fields = ["title", "image", "content", "tags"]

    def __init__(self, *args, **kwargs):
        """
        Inject image HTML in "image" field help text.
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["image"].help_text = utils.image_html(self.instance.image.url)

    def clean_image(self):
        """
        Can add custom image validation here if we want...
        """
        image = self.cleaned_data.get("image")
        return image


@admin.register(models.Initiative)
class InitiativeAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    form = InitiativeForm
    list_display = ["title", "content_preview", "image_preview", "get_tags"]
    content_preview = utils.content_preview_fn()
    filter_horizontal = ["tags"]  # better admin editing for many-to-many fields

    def image_preview(self, obj):
        """
        Image preview inline.
        """
        if obj.image:
            return utils.image_html(obj.image.url)
        return "No image"

    def get_tags(self, obj):
        if obj.tags.count() > 0:
            return ", ".join([tag.name for tag in obj.tags.all()])
        return "No Tags"

    get_tags.short_description = "Tags"


@admin.register(models.InitiativeTag)
class InitiativeTagAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    list_display = ["name", "get_initiatives"]

    # Reverse relation is readonly in the add/change view for now, we can
    # change this later, but the solution is a little complicated.
    readonly_fields = ["get_initiatives"]

    def get_initiatives(self, obj):
        if obj.initiatives.count() > 0:
            return ", ".join([initiative.title for initiative in obj.initiatives.all()])
        return "No Initiatives"

    get_initiatives.short_description = "Initiatives"
