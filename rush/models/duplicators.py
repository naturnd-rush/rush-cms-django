from abc import ABC, abstractmethod
from typing import Type

from django.db.models import Model

from rush.models import (
    BasemapSourceOnQuestion,
    Layer,
    LayerGroupOnQuestion,
    LayerOnLayerGroup,
    Question,
    QuestionTab,
)

"""
This file contains logic for duplicating RUSH models in the database.
"""


class DuplicatorBase(ABC):
    """
    A duplicator defines how a Django model type should be successfully "duplicated" in the database.
    It should also duplicate any related objects, and change any field values that would violate a
    unique constraint in the database.
    """

    def __init__(self, instance: Model):
        self.instance = instance
        if instance is None:
            raise DuplicationFail(self, "duplication instance cannot be none")
        if not isinstance(instance, self.duplication_cls()):
            raise DuplicationFail(self, "wrong instance type")

    @abstractmethod
    def duplication_cls(self) -> Type[Model]:
        """
        The type of Django model this duplicator works on.
        """
        ...

    @abstractmethod
    def duplicate(self) -> Model:
        """
        Duplicate a Django in the database. Return the duplicated model.
        """
        ...


class DuplicationFail(Exception):
    """
    Something went wrong while trying to duplicate an object.
    """

    def __init__(self, duplicator: DuplicatorBase, message: str):
        super().__init__(
            "{message} for <{classname}> with instance '{instance}'.".format(
                message=message.capitalize(),
                classname=duplicator.__class__.__name__,
                instance=str(duplicator.instance),
            )
        )


class QuestionDuplicator(DuplicatorBase):

    def duplicate(self) -> Question:
        """
        Create and return a duplicate Question.
        """

        assert isinstance(self.instance, Question)
        for question in Question.objects.all():
            # move all questions up in the order to make room for the duplicate
            question.display_order += 1
            question.full_clean()
            question.save()

        duplicate = Question.objects.create(
            title=self.instance.title,
            subtitle=self.instance.subtitle,
            image=self.instance.image,
            is_image_compressed=self.instance.is_image_compressed,
            slug=f"{self.instance.slug}-copy",
            sash=self.instance.sash,
            region=self.instance.region,
            display_order=0,
            published_state=self.instance.published_state,
        )

        # Copy initiatives by reference
        duplicate.initiatives.set(self.instance.initiatives.all())

        # Copy tabs by value
        for tab in self.instance.tabs.all():  # type: ignore
            QuestionTab.objects.create(
                question=duplicate,
                icon=tab.icon,
                title=tab.title,
                content=tab.content,
                slug=tab.slug,
                display_order=tab.display_order,
            )

        # Copy basemap-sources by reference (through the basemap-source-on-question model
        # which is copied by value).
        for basemap_source_on_question in BasemapSourceOnQuestion.objects.filter(question=self.instance):  # type: ignore
            BasemapSourceOnQuestion.objects.create(
                question=duplicate,
                basemap_source=basemap_source_on_question.basemap_source,
                is_default_for_question=basemap_source_on_question.is_default_for_question,
            )

        group_map = {}  # id --> Layer-group-on-question
        for layer_on_layer_group in LayerOnLayerGroup.objects.filter(
            layer_group_on_question__question=self.instance
        ):
            instance_group = layer_on_layer_group.layer_group_on_question
            if instance_group.id not in group_map:
                # create duplicate layer-group-on-questions "on the fly"
                duplicate_group = LayerGroupOnQuestion.objects.create(
                    group_name=instance_group.group_name,
                    group_description=instance_group.group_description,
                    question=duplicate,
                    behaviour=instance_group.behaviour,
                    display_order=instance_group.display_order,
                )
                group_map[instance_group.id] = duplicate_group

            # now, create layer-on-layer-group poinging to correct (duplicated) group and
            # original layer reference.
            LayerOnLayerGroup.objects.create(
                layer=layer_on_layer_group.layer,
                layer_group_on_question=group_map[instance_group.id],
                active_by_default=layer_on_layer_group.active_by_default,
                display_order=layer_on_layer_group.display_order,
            )

        duplicate.full_clean()
        duplicate.save()
        return duplicate

    def duplication_cls(self) -> Type[Model]:
        return Question

        duplicate.full_clean()
        duplicate.save()
        return duplicate

    def duplication_cls(self) -> Type[Model]:
        return Question
