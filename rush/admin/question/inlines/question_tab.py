import adminsortable2.admin as sortable_admin
from django.contrib import admin
from django.db import models
from django_summernote.admin import SummernoteModelAdminMixin

from rush import models


class QuestionTabInline(sortable_admin.SortableTabularInline, SummernoteModelAdminMixin, admin.TabularInline):
    """
    Allow editing of QuestionTab objects straight from the Question form.
    """

    exclude = ["id"]
    model = models.QuestionTab
    extra = 0  # don't display extra question tabs to add, let the user click
    sortable_field_name = "display_order"
    prepopulated_fields = {"slug": ("title",)}
    sortable_options = (
        # Added for compatibility SortableTabularInline <--> NestedModelAdmin (on QuestionAdmin page.)
        []
    )
