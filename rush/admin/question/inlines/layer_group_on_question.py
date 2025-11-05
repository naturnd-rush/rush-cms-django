from nested_admin.forms import SortableHiddenMixin
from nested_admin.nested import NestedTabularInline

from rush.admin.question.inlines import LayerOnLayerGroupInline
from rush.models import LayerGroupOnQuestion


class LayerGroupOnQuestionInline(SortableHiddenMixin, NestedTabularInline):
    """
    An inline group of layers that are assigned to a question.
    """

    verbose_name_plural = "Layer Groups"
    model = LayerGroupOnQuestion
    extra = 0
    exclude = ["id"]
    inlines = [LayerOnLayerGroupInline]
    sortable_field_name = "display_order"

    def get_fields(self, request, obj=None):
        """
        Only superusers should be able to see and edit the hidden field `group_type`.
        Group type defines special behaviour for `LayerGroupOnQuestion` that should
        not be exposed to regular staff users.
        """
        fields = super().get_fields(request, obj)
        if not request.user.is_superuser:
            fields = [x for x in fields if x != "behaviour"]
        return fields
