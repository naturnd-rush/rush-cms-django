"""
This module contains signals that perform "sync" operations on layer-groups when
they are set-up to have the ALL_LAYERS behaviour. See the requirements below:
    1.  When a layer-group is created or updated to have the ALL_LAYERS behaviour,
        all existing layers are added (not active by default) to the group.
    2.  When a new layer is created, it is automatically added to any layer-groups
        that have the ALL_LAYERS behaviour.
    3.  We don't need a signal for when layers get deleted, because layer-on-layer-groups
        will automatically get deleted via CASCADE on their layer foreign-keys.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from rush.models.layer import Layer, LayerGroupOnQuestion, LayerOnLayerGroup


@receiver(post_save, sender=LayerGroupOnQuestion)
def add_all_layers_when_all_layers_behaviour_enabled(sender, instance, created, **kwargs):
    if not isinstance(instance, LayerGroupOnQuestion):
        raise ValueError(f"Expected {instance} to be a {LayerGroupOnQuestion.__class__}.")
    if instance.behaviour != LayerGroupOnQuestion.Behaviour.ALL_LAYERS:
        return None
    for display_order, layer in enumerate(Layer.objects.all()):
        if instance.layers.filter(layer=layer).exists():  # type: ignore
            # skip if layer already in group
            continue
        LayerOnLayerGroup.objects.create(
            layer=layer,
            layer_group_on_question=instance,
            display_order=display_order,
        )


@receiver(post_save, sender=Layer)
def add_layer_when_layer_created(sender, instance, created, **kwargs):
    if not isinstance(instance, Layer):
        raise ValueError(f"Expected {instance} to be a {Layer.__class__}.")
    if not created:
        # Skip if layer is being updated rather than created
        return None
    groups = LayerGroupOnQuestion.objects.filter(behaviour=LayerGroupOnQuestion.Behaviour.ALL_LAYERS)
    for group in groups:
        if group.layers.filter(layer=instance).exists():  # type: ignore
            # skip if layer already in group
            continue
        LayerOnLayerGroup.objects.create(
            layer=instance,
            layer_group_on_question=group,
            display_order=group.max_display_order() + 1,
        )
