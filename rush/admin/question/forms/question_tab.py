from django.forms import ModelForm

from rush.admin.widgets import TiledForeignKeyWidget
from rush.models import Icon, QuestionTab


class QuestionTabForm(ModelForm):
    class Meta:
        model = QuestionTab
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["icon"].widget = TiledForeignKeyWidget(
            display_choices=[
                TiledForeignKeyWidget.Choice(
                    id=str(icon.id),
                    thumbnail_url=icon.file.url,
                    instance=self.instance,
                    fk_name="icon",
                    request=getattr(self, "request"),
                )
                for icon in Icon.objects.order_by("-created_at")[:10]
            ],
        )
