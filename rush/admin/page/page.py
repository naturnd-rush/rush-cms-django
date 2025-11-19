from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from rush.models import Page


@admin.register(Page)
class PageAdmin(SummernoteModelAdmin, admin.ModelAdmin):
    """
    Admin page for editing other, non-map-related, Pages on the website.
    """

    summernote_fields = ["content"]
    exclude = ["id"]
