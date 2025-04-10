from django.contrib import admin
from django.template.response import TemplateResponse

from rush.models import DeployLog


@admin.register(DeployLog)
class DeployLogAdmin(admin.ModelAdmin):
    exclude = ["id"]
    list_display = ["filename"]
    readonly_fields = ("filename", "log_contents")

    def log_contents(self, obj):
        return obj.get_log_contents()
