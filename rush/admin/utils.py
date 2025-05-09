from django import forms
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class SliderAndTextboxNumberInput(forms.Widget):
    """
    A number input Django form widget that provides both a slider and an
    input textbox so the user can choose their preferred way to enter data.

    NOTE: For this widget to work the corresponding `slider_textbox_input_sync.js`
          script must be included in the Django form Media subclass.
    """

    def __init__(self, attrs=None, min=0, max=1, step=0.01):
        self.min = min
        self.max = max
        self.step = step
        self.slider_input = None
        self.textbox_input = None
        super().__init__(attrs)

    def _lazy_create_input_widgets(self, fieldname: str) -> None:
        """
        Lazily create the slider and textbox input form widgets once we know the input fieldname.
        """
        if self.slider_input and self.number_input:
            # prevent from re-creating every render
            return
        self.slider_input = forms.NumberInput(
            attrs={
                "type": "range",
                "min": str(self.min),
                "max": str(self.max),
                "step": str(self.step),
            }
        )
        self.number_input = forms.NumberInput(
            attrs={
                "type": "number",
                "min": str(self.min),
                "max": str(self.max),
                "step": str(self.step),
            }
        )

    def render(self, name, value, attrs=None, renderer=None) -> str:
        self._lazy_create_input_widgets(fieldname=name)
        value = float(value) if value is not None else 0
        slider_id = f"slider_{name}"
        textbox_id = f"id_{name}"
        slider_html = self.slider_input.render(
            name,
            value,
            attrs={**self.attrs, "id": slider_id},
            renderer=renderer,
        )
        number_html = self.number_input.render(
            name,
            value,
            attrs={**self.attrs, "id": textbox_id},
            renderer=renderer,
        )

        return mark_safe(
            f"""
            <div class="dual-slider-textbox" data-fieldname="{name}">
                {slider_html}<div style="margin-right: 15px; display: inline;"></div>{number_html}
            </div>
        """
        )


class LiveImagePreviewInput(forms.ClearableFileInput):
    """
    An image upload input field with life-previewing of the selected image.

    NOTE: For this widget to work the corresponding `live_image_preview_refresh.js`
          script must be included in the Django form Media subclass.
    """

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None) -> str:
        image_upload_html = forms.ClearableFileInput().render(
            name=name,
            value=value,
            attrs={**self.attrs, "id": f"live_image_input_{name}"},
            renderer=renderer,
        )
        src = f"{settings.MEDIA_URL}{value}" if value else "#"
        return mark_safe(
            f"""
            {image_upload_html}
            <div style="margin-right: 15px;"></div>
            <img id="live_image_preview_{name}" src="{src}" style="max-width: 200px; display: block;" />
            """
        )


def image_html(image_url: str, image_width: int = 200) -> str:
    """
    Return HTML for rendering an image.
    TODO: See if I can't get the image preview to live-reload by injecting some JS here...
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
    Return an HTML + JS snippet that renders TODO
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
