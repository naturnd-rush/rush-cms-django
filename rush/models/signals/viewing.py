from django.contrib.admin.models import ADDITION, LogEntry
from django.db.models import Model
from django.dispatch import Signal, receiver

from rush.models.signals.utils import user_content_type
from rush.utils import get_client_ip

# Fired when *any* admin changelist is viewed
admin_changelist_viewed = Signal()

# Fired when *any* admin changeform is viewed
admin_changeform_viewed = Signal()


@receiver(admin_changelist_viewed)
def log_changelist(sender, request, model, modeladmin, **kwargs):
    user = getattr(request, "user", None)
    if user is not None:
        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=user_content_type().pk,
            object_id=user.pk,
            object_repr=str(user)[:200],
            action_flag=ADDITION,
            change_message=f"{user} viewed the list of {model._meta.verbose_name_plural}.",
        )
    else:
        # LOG TODO Should log a warning here...
        ...


@receiver(admin_changeform_viewed)
def log_changeform(sender, request, model, object_id, modeladmin, **kwargs):
    user = getattr(request, "user", None)
    if user is not None:
        try:
            obj = model.objects.get(id=object_id)
            obj_desc = f"<{model.__name__}: {str(obj)}>"
            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=user_content_type().pk,
                object_id=user.pk,
                object_repr=str(user)[:200],
                action_flag=ADDITION,
                change_message=f"{user} viewed {obj_desc}.",
            )
        except Exception as e:
            # LOG TODO: should log a warning here...
            ...
    else:
        # LOG TODO: Should log a warning here...
        ...
