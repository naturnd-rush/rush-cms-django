from django.contrib import admin
from rush.models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ["name", "latitude", "longitude", "default_zoom", "question_count"]
    search_fields = ["name"]
    ordering = ["name"]
    
    @admin.display(description="Questions")
    def question_count(self, obj):
        return obj.questions_in_region.count()
