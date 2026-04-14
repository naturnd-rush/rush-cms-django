from django.contrib.admin import ModelAdmin, register

from rush.admin.page import PageForm
from rush.models import Page


@register(Page)
class PageAdmin(ModelAdmin):
    """
    Admin page for editing other, non-map-related, Pages on the website.
    """

    form = PageForm
