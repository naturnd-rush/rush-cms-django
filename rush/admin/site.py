from uuid import uuid4

import adminsortable2.admin as sortable_admin
import nested_admin.forms as nested_forms
import nested_admin.nested as nested_admin
from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html_join
from django_summernote.admin import SummernoteModelAdmin, SummernoteModelAdminMixin

from rush import models
from rush.admin import utils


class LayerOnLayerGroupInline(nested_forms.SortableHiddenMixin, nested_admin.NestedTabularInline):
    verbose_name_plural = "Layers"
    model = models.LayerOnLayerGroup
    extra = 0
    exclude = ["id"]
    autocomplete_fields = [
        "layer",
        # "layer_group",
    ]
    sortable_field_name = "display_order"


class LayerGroupOnQuestionInline(nested_forms.SortableHiddenMixin, nested_admin.NestedTabularInline):
    verbose_name_plural = "Layer Groups"
    model = models.LayerGroupOnQuestion
    extra = 0
    exclude = ["id"]
    inlines = [LayerOnLayerGroupInline]
    sortable_field_name = "display_order"


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
    list_display = ["name", "tagged_initiatives"]
    search_fields = ["name"]

    # Reverse relation is readonly in the add/change view for now, we can
    # change this later, but the solution is a little complicated.
    readonly_fields = ["tagged_initiatives"]

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


class QuestionForm(forms.ModelForm):
    """
    Override the default add/change page for the Question model admin.
    """

    class Meta:
        model = models.Question
        fields = [
            "title",
            "slug",
            "subtitle",
            "image",
            "initiatives",
        ]

    def __init__(self, *args, **kwargs):
        """
        Inject image HTML in "image" field help text.
        TODO: Maybe delete this whole form and inject JS for preview using readonly_fields?
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["image"].help_text = utils.image_html(self.instance.image.url)


# @admin.register(models.QuestionTab)
# class QuestionTabAdmin(nested_admin.NestedModelAdmin, SummernoteModelAdmin):
#     exclude = ["id"]
#     summernote_fields = ["content"]
#     list_display = ["title", "content_preview"]
#     content_preview = utils.truncate_admin_text_from("content")
#     sortable_field_name = "display_order"


class QuestionTabInline(sortable_admin.SortableTabularInline, SummernoteModelAdminMixin, admin.TabularInline):
    """
    Allow editing of QuestionTab objects straight from the Question form.
    """

    exclude = ["id"]
    model = models.QuestionTab
    extra = 0  # don't display extra question tabs to add, let the user click
    sortable_field_name = "display_order"
    sortable_options = []


@admin.register(models.Question)
class QuestionAdmin(sortable_admin.SortableAdminMixin, nested_admin.NestedModelAdmin):  # type: ignore
    exclude = ["id"]
    form = QuestionForm
    list_display = ["title", "slug", "image_preview", "get_initiatives", "display_order"]
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["initiatives"]
    inlines = [QuestionTabInline, LayerGroupOnQuestionInline]
    actions = ["duplicate_object"]
    sortable_field_name = "display_order"  # Enable drag-and-drop for Questions in the list view
    # filter_horizontal = ["initiatives"]  # better admin editing for many-to-many fields

    def image_preview(self, obj):
        """
        Image preview inline.
        """
        if obj.image:
            return utils.image_html(obj.image.url)
        return "No image"

    @admin.display(description="Initiatives")
    def get_initiatives(self, obj):
        if obj.initiatives.count() > 0:
            return ", ".join([initiative.title for initiative in obj.initiatives.all()])
        return "No Initiatives"

    @admin.action(description="Duplicate selected items")
    def duplicate_object(self, request, queryset):
        for obj in queryset:
            obj.pk = None  # Clear primary key (should auto-generate)
            obj.id = None  # Clear id (should auto-generate)
            obj.slug = f"{obj.slug}-copy-{uuid4().hex}"  # Avoid unique constraint violations
            obj.save()

        self.message_user(request, f"Successfully duplicated {queryset.count()} item(s).")


# @admin.register(models.LayerGroupOnQuestion)
# class LayerGroupOnQuestionAdmin(nested_admin.NestedModelAdmin):
#     """
#     Admin page for the layer groups on questions.
#     """

#     exclude = ["id"]
#     search_fields = ["group_name"]
#     inlines = [LayerOnLayerGroupInline]
#     sortable_field_name = "display_order"


@admin.register(models.Page)
class PageAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    """
    Admin page for editing other, non-map-related, Pages on the website.
    """

    summernote_fields = ["content"]
    exclude = ["id"]
