from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Type

from deepdiff import DeepDiff
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db.models import Model

from rush.logger import get_logger

logger = get_logger()


class LogChangesAdminBase(ModelAdmin):
    """
    A Django admin base class that logs user activity on the model.
    """

    @dataclass
    class Description(ABC):

        model: Model | Type[Model]

        @abstractmethod
        def as_string(self) -> str:
            """
            Return a description of the activity.
            """
            raise NotImplementedError

        def model_desc(self) -> str:
            """
            Short description of the modelname + id.
            """
            if isinstance(self.model, type):
                # class instance so just return the classname
                return f"<{self.model.__name__}>"

            # otherwise return mode detailed model instance information
            modelname = self.model.__class__.__name__
            model_id = ""
            instance_name = ""
            if hasattr(self.model, "id"):
                model_id = f'|{getattr(self.model, "id")}'
            if hasattr(self.model, "name"):
                instance_name = f'|{getattr(self.model, "name")}'
            return f"<{modelname}{instance_name}{model_id}>"

    @dataclass
    class ViewedList(Description):

        def as_string(self) -> str:
            return f"viewed a list of {self.model_desc()}"

    @dataclass
    class ViewedModel(Description):

        def as_string(self) -> str:
            return f"viewed {self.model_desc()}"

    @dataclass
    class Created(Description):

        def as_string(self) -> str:
            return f"created {self.model_desc()}"

    @dataclass
    class Edited(Description):

        before_dict: Dict[str, Any]
        after_dict: Dict[str, Any]

        def as_string(self) -> str:
            if isinstance(self.model, Model):
                # Show specific changes if model allows
                return f"edited {self.model_desc()} -- {str(DeepDiff(self.before_dict, self.after_dict))}"
            # Otherwise show simple "edited + model description"
            return f"edited {self.model_desc()}"

    @dataclass
    class Deleted(Description):

        def as_string(self) -> str:
            return f"deleted {self.model_desc()}"

    @dataclass
    class Activity:

        user: AbstractUser | AnonymousUser
        description: LogChangesAdminBase.Description

        def log(self) -> None:
            if isinstance(self.user, AnonymousUser):
                # All of these actions should be performed by authenticated users. It would
                # be concerning if an AnonymousUser was able to perform edits / deletions, etc.
                return logger.error(
                    "AnonymousUser {}. This should not be possible!".format(
                        self.description.as_string(),
                    )
                )
            logger.info(
                "<User {}|{}> {}.".format(
                    str(self.user),
                    self.user.email,
                    self.description.as_string(),
                )
            )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if isinstance(obj, Model):
            self.Activity(request.user, self.ViewedModel(obj)).log()
        else:
            logger.error(f"Changeview object {self.model} for {request} is not a model!")
        return super().change_view(request, object_id, form_url, extra_context)

    def changelist_view(self, request, extra_context=None):
        if isinstance(self.model, type):
            self.Activity(request.user, self.ViewedList(self.model)).log()
        else:
            logger.error(f"Changeview object {self.model} for {request} is not a model class!")
        return super().changelist_view(request, extra_context)

    def save_model(self, request, obj, form, change):

        if not isinstance(obj, Model):
            logger.error(f"Changeview object {self.model} for {request} is not a model!")
            return super().save_model(request, obj, form, change)

        elif change:
            # Editing existing model
            before = obj.__class__.objects.get(pk=obj.pk)  # Get different instance (before saving)

            super().save_model(request, obj, form, change)
            after = obj.__class__.objects.get(pk=obj.pk)
            try:
                self.Activity(
                    request.user,
                    self.Edited(
                        model=obj,
                        before_dict=before.log_changes_dict(),  # type: ignore
                        after_dict=after.log_changes_dict(),  # type: ignore
                    ),
                ).log()
            except Exception as e:
                logger.error(
                    "No 'log_changes_dict' function for specific editing comparison on {}.".format(
                        self.model.__class__.__name__,
                    ),
                    exc_info=e,
                )

        else:
            # Creating new model
            self.Activity(request.user, self.Created(self.model)).log()

    # def delete_model(self, request, obj):
    #     LogEntry.objects.log_action(
    #         user_id=request.user.pk,
    #         content_type_id=ContentType.objects.get_for_model(obj).pk,
    #         object_id=obj.pk,
    #         object_repr=str(obj),
    #         action_flag=DELETION,
    #         change_message=f"IP: {get_client_ip(request)}",
    #     )
    #     super().delete_model(request, obj)
