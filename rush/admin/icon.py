from django.contrib.admin import ModelAdmin, register

from rush.admin.utils import image_html
from rush.models import Icon


@register(Icon)
class IconAdmin(ModelAdmin):
    exclude = ["id", "mime_type", "is_file_compressed"]
    list_display = ["preview"]

    def preview(self, obj):
        if obj.file:
            return image_html(obj.file.url, image_width=60)
        return "No image"
