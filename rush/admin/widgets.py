from dataclasses import dataclass
from typing import Any, List

from django.db.models import Model
from django.forms import Select
from django.template import Context, Engine
from django.utils.safestring import mark_safe

from rush.context_processors import base_url_from_request


class TiledForeignKeyWidget(Select):
    """
    A foreign-key selection widget for the admin site that displays foreign-key
    instances in a tile-like manner which can be selected by a user clicking on them.
    """

    @dataclass
    class Choice:
        """
        A possible choice of which foreign-key to select.
        """

        id: str

        # Relative url (e.g., from file-field)
        thumbnail_url: str

        # the form model instance (of type A) that has a foreign-key to a model (of type B),
        # whose instances we wish to display as selectable tiles.
        instance: Model

        # The name of the foreign key field (to a model of type B), on the form model instance model (of type A).
        fk_name: str

        request: Any

        def selected_str(self) -> str:
            """
            True when the fk object is attached to the form instance.
            """
            related = getattr(self.instance, self.fk_name, None)
            if related is None:
                # LOG TODO: Should log warning here.
                return ""
            selected = str(related.id) == self.id
            return "selected" if selected else ""

        def base_media_url(self) -> str:
            return base_url_from_request(self.request)

    def __init__(self, display_choices: List[Choice], attrs=None):
        self.display_choices = display_choices
        super().__init__(
            attrs,
            [
                # Just use id as the label for choices here, since the
                # display_html is shown in lieu of a label.
                (x.id, x.id)
                for x in display_choices
            ],
        )

    def render(self, name, value, attrs=None, renderer=None):
        """
        Renders the widget as a grid of tiles with images.
        """

        # Prepare context
        context = {
            "name": name,
            "value": value,
            "display_choices": self.display_choices,
        }
        template_str = """
        <div class="tiled-foreignkey-widget">

            {% for choice in display_choices %}
                <div class="tile {{ choice.selected_str }}" data-value="{{ choice.id }}">
                    <img src="{{ choice.base_media_url }}{{ choice.thumbnail_url }}" alt="">
                </div>
            {% endfor %}

            <!-- Hidden select -->
            <select name="{{ name }}" class="tiled-fk-select" style="display:none;">
                {% for choice in display_choices %}
                    <option value="{{ choice.id }}" {{ choice.selected_str }}></option>
                {% endfor %}
            </select>

        </div>

        <script type="module">
            document.querySelectorAll('.tiled-foreignkey-widget').forEach(widget => {
                widget.querySelectorAll('.tile').forEach(tile => {
                    tile.addEventListener('click', () => {
                        widget.querySelectorAll('.tile').forEach(t => t.classList.remove('selected'));
                        tile.classList.add('selected');
                        widget.querySelector('.tiled-fk-select').value = tile.dataset.value;
                    });
                });
            });
        </script>

        <style>
            .tiled-foreignkey-widget {
                display: flex;
                flex-wrap: wrap;
                width: 340px; /* controls 5 tiles per row */
                gap: 10px;
                justify-content: left;
                margin-top: 8px;
            }

            .tiled-foreignkey-widget .tile {
                width: 60px;
                height: 60px;
                border: 2px solid #ddd;
                border-radius: 6px;
                box-sizing: border-box;
                cursor: pointer;
                display: flex;
                padding: 4px;
                justify-content: center;
                align-items: center;
                background: #fafafa;
                transition: border 0.18s ease, box-shadow 0.18s ease;
            }

            .tiled-foreignkey-widget .tile:hover {
                border-color: #4285f4;
                box-shadow: 0 0 4px rgba(66,133,244,0.4);
            }

            .tiled-foreignkey-widget .tile.selected {
                border-color: #1e65d6;
                background: #e8f0fe;
                box-shadow: 0 0 0 2px rgba(30,101,214,0.3);
            }

            .tiled-foreignkey-widget img {
                width: 100%;
                height: auto;
                object-fit: contain;
            }
        </style>
        """
        engine = Engine()
        template = engine.from_string(template_str)
        html = template.render(Context(context))
        return mark_safe(html)
