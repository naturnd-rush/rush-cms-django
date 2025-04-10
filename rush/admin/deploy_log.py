from django.contrib import admin

from rush.models import DeployLog


@admin.register(DeployLog)
class DeployLogAdmin(admin.ModelAdmin):
    list_display = ("filename", "get_file_path")
    search_fields = ("filename",)

    def get_file_path(self, obj):
        return obj.get_file_path()

    get_file_path.short_description = "Log File Path"
