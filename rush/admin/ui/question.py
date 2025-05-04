from django import forms
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from rush import models
from rush.admin import utils


class QuestionForm(forms.ModelForm):
    """
    Override the default add/change page for the Question model admin.
    TODO: Maybe delete this form and inject JS for preview using readonly_fields?
    """

    class Meta:
        model = models.Question
        fields = [
            "layer",
            "title",
            "image",
            "content",
            "sub_question",
            "initiatives",
        ]

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


@admin.register(models.Question)
class QuestionAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    form = QuestionForm
    summernote_fields = ["content"]
    list_display = [
        "title",
        "content_preview",
        "image_preview",
        "get_initiatives",
    ]
    content_preview = utils.content_preview_fn()
    filter_horizontal = ["initiatives"]  # better admin editing for many-to-many fields

    def image_preview(self, obj):
        """
        Image preview inline.
        """
        if obj.image:
            return utils.image_html(obj.image.url)
        return "No image"

    def get_initiatives(self, obj):
        if obj.initiatives.count() > 0:
            return ", ".join([initiative.title for initiative in obj.initiatives.all()])
        return "No Initiatives"

    get_initiatives.short_description = "Initiatives"


@admin.register(models.QuestionTab)
class QuestionTabAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    list_display = ["title", "content_preview"]
    content_preview = utils.content_preview_fn()
