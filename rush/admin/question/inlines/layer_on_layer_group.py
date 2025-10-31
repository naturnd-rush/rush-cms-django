from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedTabularInline

from rush.models import LayerOnLayerGroup


class LayerOnLayerGroupInline(SortableHiddenMixin, NestedTabularInline):
    """
    A layer that is nested inside of a layer-group on a question.
    """

    verbose_name_plural = "Layers"
    model = LayerOnLayerGroup
    extra = 0
    exclude = ["id"]
    autocomplete_fields = ["layer"]
    sortable_field_name = "display_order"
