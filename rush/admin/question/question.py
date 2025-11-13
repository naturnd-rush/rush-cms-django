from uuid import uuid4

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.safestring import mark_safe
from nested_admin.nested import NestedModelAdmin

from rush.admin.question.forms import QuestionForm
from rush.admin.question.inlines import LayerGroupOnQuestionInline, QuestionTabInline
from rush.admin.utils import image_html
from rush.models import Question


@admin.register(Question)
class QuestionAdmin(SortableAdminMixin, NestedModelAdmin):  # type: ignore
    form = QuestionForm
    exclude = ["id"]
    list_display = [
        "title",
        "slug",
        "image_preview",
        "sash_preview",
        "get_initiatives",
        "display_order",
    ]
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ["initiatives", "sash"]
    inlines = [QuestionTabInline, LayerGroupOnQuestionInline]
    actions = ["duplicate_object"]
    sortable_field_name = "display_order"  # Enable drag-and-drop for Questions in the list view
    # filter_horizontal = ["initiatives"]  # better admin editing for many-to-many fields

    @admin.display(description="Sash")
    def sash_preview(self, obj: Question):
        if obj and obj.sash:
            return mark_safe(obj.sash.get_html_preview())
        return "-"

    def image_preview(self, obj):
        """
        Image preview inline.
        """
        if obj.image:
            return image_html(obj.image.url)
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
