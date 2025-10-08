from django import forms
from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html_join
from django_summernote.admin import SummernoteInlineModelAdmin, SummernoteModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from rush import models
from rush.admin import utils


class LayerOnQuestionStackedInline(admin.StackedInline):
    verbose_name_plural = "Layers on this Question"
    model = models.LayerOnQuestion
    extra = 0
    exclude = ["id"]
    autocomplete_fields = ["layer", "layer_group"]


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
class InitiativeTagAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
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
    TODO: Maybe delete this form and inject JS for preview using readonly_fields?
    """

    class Meta:
        model = models.Question
        fields = [
            # "layers",
            "title",
            "slug", 
            "subtitle",
            "image",
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


@admin.register(models.QuestionTab)
class QuestionTabAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    exclude = ["id"]
    summernote_fields = ["content"]
    list_display = ["title", "content_preview"]
    content_preview = utils.truncate_admin_text_from("content")


class QuestionTabInline(admin.TabularInline, SummernoteInlineModelAdmin):
    """
    Allow editing of QuestionTab objects straight from the Question form.
    """

    exclude = ["id"]
    model = models.QuestionTab
    extra = 1  # show 1 extra empty form


@admin.register(models.Question)
class QuestionAdmin(SimpleHistoryAdmin):
    exclude = ["id"]
    form = QuestionForm
    list_display = [
        "title",
        "slug",  
        "image_preview",
        "get_initiatives",
    ]
    prepopulated_fields = {"slug": ("title",)} # new line for slug
    autocomplete_fields = ["initiatives"]
    inlines = [QuestionTabInline, LayerOnQuestionStackedInline]
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


@admin.register(models.LayerGroup)
class LayerGroupTitleAdmin(admin.ModelAdmin):
    """
    Admin page for the Layer group titles.
    """

    exclude = ["id"]
    search_fields = ["group_name"]


@admin.register(models.Page)
class PageAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    """
    Admin page for editing other, non-map-related, Pages on the website.
    """

    summernote_fields = ["content"]
    exclude = ["id"]
