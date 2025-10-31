from adminsortable2.admin import SortableTabularInline
from django.contrib.admin import TabularInline
from django_summernote.admin import SummernoteModelAdminMixin

from rush.admin.question.forms import QuestionTabForm
from rush.models import QuestionTab


class QuestionTabInline(SortableTabularInline, SummernoteModelAdminMixin, TabularInline):
    """
    Allow editing of QuestionTab objects straight from the Question form.
    """

    exclude = ["id"]
    form = QuestionTabForm
    model = QuestionTab
    extra = 0  # don't display extra question tabs to add, let the user click
    sortable_field_name = "display_order"
    prepopulated_fields = {"slug": ("title",)}
    sortable_options = (
        # Added for compatibility SortableTabularInline <--> NestedModelAdmin (on QuestionAdmin page)
        []
    )

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super().get_formset(request, obj, **kwargs)
        formset_class.form.request = request  # type: ignore
        return formset_class
