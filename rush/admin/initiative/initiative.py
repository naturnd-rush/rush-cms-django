from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from rush.admin.initiative.forms.initiative_form import InitiativeForm
from rush import models
from rush.admin import utils


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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Prefetch tags to avoid N+1 queries in get_tags() display method
        return qs.prefetch_related("tags")

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
