from django.contrib import admin
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe


def image_html(image_url: str, image_width: int = 200) -> str:
    """
    Return HTML for rendering an image.
    """
    return mark_safe(f'<img src="{image_url}" width="{image_width}" height="auto" />')


def content_preview_fn(
    content_attr_name: str = "content",
    preview_chars: int = 500,
):
    """
    Return an admin model function that renders a preview of some
    content in the inline display.
    """

    def inner(admin_instance: admin.ModelAdmin, obj: models.Model) -> str:
        content = getattr(obj, content_attr_name, None)
        if not content:
            return "No content"
        return format_html(content[:preview_chars] + "...")

    return inner


def get_map_preview_html(
    geojson: dict[str, any],
    change_element_id: str,
    height: str = "400px",
) -> str:
    """
    Return an HTML + JS snippet that renders
    """
    leaflet_html = render_to_string(
        template_name="admin/geojson_map_preview.html",
        context={
            "geojson_data": geojson,
            "height": height,
            "change_element_id": change_element_id,
        },
    )
    return mark_safe(leaflet_html)
