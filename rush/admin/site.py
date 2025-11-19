from uuid import uuid4

import adminsortable2.admin as sortable_admin
import nested_admin.forms as nested_forms
import nested_admin.nested as nested_admin
from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin

from rush import models
from rush.admin import utils


class InitiativeForm(forms.ModelForm):
    """
    Override the default add/change page for the Initiative model admin.
    """

    class Meta:
        model = models.Initiative
        fields = ["title", "link", "image", "content", "tags"]

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
class InitiativeAdmin(SummernoteModelAdmin):
    exclude = ["id"]
    form = InitiativeForm
    list_display = ["title", "link", "content_preview", "image_preview", "get_tags"]
    content_preview = utils.truncate_admin_text_from("content")
    autocomplete_fields = [
        # uses the searchable textbox in the admin form to add/remove Tags
        "tags"
    ]
    search_fields = ["title"]

    def image_preview(self, obj):
        """
        Image preview inline.
        """
        if obj.image:
            return utils.image_html(obj.image.url)
        return "No image"

    @admin.display(description="Tags")
    def get_tags(self, obj):
        if obj.tags.count() > 0:
            return ", ".join([tag.name for tag in obj.tags.all()])
        return "No Tags"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "tags":
            # Tags not required to create an initiative
            kwargs["required"] = False
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(models.InitiativeTag)
class InitiativeTagAdmin(SummernoteModelAdmin):
    exclude = ["id"]
    list_display = ["name", "preview", "tagged_initiatives"]
    search_fields = ["name"]

    # Reverse relation is readonly in the add/change view for now, we can
    # change this later, but the solution is a little complicated.
    readonly_fields = ["tagged_initiatives"]

    def preview(self, obj: models.InitiativeTag):
        return mark_safe(
            f"""
                <p style='
                    color: {obj.text_color};
                    background-color: {obj.background_color};
                    font-size: 0.75rem;
                    text-transform: uppercase;
                    border-radius: 0.125rem;
                    font-family: "Bitter Variable", serif;
                    width: fit-content;
                    padding-left: 0.25rem;
                    padding-right: 0.25rem;
                    font-weight: 700;
                '>
                    {obj.name}
                </p>
            """
        )

    @admin.display(description="Initiatives with this tag")
    def tagged_initiatives(self, obj):
        initiatives = obj.initiatives.all()
        if not initiatives.exists():
            return "-"
        return format_html_join(
            ", ",
            '<a href="{}">{}</a>',
            [
                (
                    reverse("admin:rush_initiative_change", args=[initiative.pk]),
                    initiative.title,
                )
                for initiative in initiatives
            ],
        )
        # if obj.initiatives.count() > 0:
        #     return ", ".join([initiative.title for initiative in obj.initiatives.all()])
        # return "No Initiatives"


# @admin.register(models.QuestionTab)
# class QuestionTabAdmin(nested_admin.NestedModelAdmin, SummernoteModelAdmin):
#     exclude = ["id"]
#     summernote_fields = ["content"]
#     list_display = ["title", "content_preview"]
#     content_preview = utils.truncate_admin_text_from("content")
#     sortable_field_name = "display_order"


# @admin.register(models.LayerGroupOnQuestion)
# class LayerGroupOnQuestionAdmin(nested_admin.NestedModelAdmin):
#     """
#     Admin page for the layer groups on questions.
#     """

#     exclude = ["id"]
#     search_fields = ["group_name"]
#     inlines = [LayerOnLayerGroupInline]
#     sortable_field_name = "display_order"

