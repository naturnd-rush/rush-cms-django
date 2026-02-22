from django.contrib.admin import SimpleListFilter

from rush.models import PublishedState


class PublishedStateFilter(SimpleListFilter):

    DEFAULT = PublishedState.PUBLISHED.value

    title = "Site Visibility"
    parameter_name = "published_state"

    def lookups(self, request, model_admin):
        return (
            (None, "Published"),
            ("draft", "Draft"),
            ("all", "All"),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": cl.get_query_string(
                    {
                        self.parameter_name: lookup,
                    },
                    [],
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() == "draft":
            return queryset.filter(published_state=self.value())
        elif self.value() == None:
            return queryset.filter(published_state=self.DEFAULT)
