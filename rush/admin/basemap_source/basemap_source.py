from django.contrib.admin import register
from django_summernote.admin import SummernoteModelAdmin

from rush.admin.basemap_source.forms import BasemapSourceForm
from rush.models import BasemapSource


@register(BasemapSource)
class BasemapSourceAdmin(SummernoteModelAdmin):
    exclude = ["id"]
    list_display = [
        "name",
        "tile_url",
        "attribution",
        "max_zoom",
        "is_default",
    ]
    search_fields = ["name", "tile_url"]
    form = BasemapSourceForm

    def get_fields(self, request, obj=None):
        """
        Only superusers should be able to see and edit "is_default".
        """
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = [x for x in fields if x != "is_default"]
        return fields
