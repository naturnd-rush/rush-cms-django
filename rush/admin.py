from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from simple_history.admin import SimpleHistoryAdmin

from .models import Question


class QuestionAdmin(SummernoteModelAdmin, SimpleHistoryAdmin):
    summernote_fields = ("body",)  # Tell admin which fields use Summernote


admin.site.register(Question, QuestionAdmin)
