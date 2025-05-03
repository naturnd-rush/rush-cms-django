from django.contrib import admin

from rush.models import DeployLog


@admin.register(DeployLog)
class DeployLogAdmin(admin.ModelAdmin):
    exclude = ["id"]
    list_display = ["created_at", "status"]
    readonly_fields = ("status", "created_at", "log_contents")

    def log_contents(self, obj: DeployLog) -> str:
        return obj.get_log_contents()

    def has_change_permission(self, request, obj=...):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        return False
