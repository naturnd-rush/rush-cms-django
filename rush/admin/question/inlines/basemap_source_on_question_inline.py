from adminsortable2.admin import SortableTabularInline
from django.contrib.admin import TabularInline
from django_summernote.admin import SummernoteModelAdminMixin

from rush.models import BasemapSourceOnQuestion


class BasemapSourceOnQuestionInline(TabularInline):
    """
    Allow editing of BasemapSource objects straight from the Question form.
    """

    exclude = ["id"]
    model = BasemapSourceOnQuestion
    extra = 0
    sortable_options = (
        # Added for compatibility TabularInline <--> NestedModelAdmin (on QuestionAdmin page)
        []
    )
