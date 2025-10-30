import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from rush.models import utils
from rush.models.validators import validate_image_svg_webp


class Question(models.Model):
    """
    A question that ties together one or more map layers into a data-driven narrative.
    """

    class Meta:
        ordering = ["display_order"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, null=False)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to="question_images/",
        null=True,
        blank=True,
        validators=[validate_image_svg_webp],
    )
    is_image_compressed = models.BooleanField(default=False)
    initiatives = models.ManyToManyField(to="Initiative", blank=True)
    questions = models.ManyToManyField(to="Layer", related_name="questions")
    slug = models.SlugField(max_length=255, unique=True)
    display_order = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True, editable=True)

    def __str__(self):
        return self.title


@receiver(pre_save, sender=Question)
def compress_image(sender, instance: Question, **kwargs):
    if db_instance := Question.objects.filter(pk=instance.id).first():
        if instance.image != db_instance.image:
            # Mark file as needing compression if it has changed at all
            instance.is_image_compressed = False
    if instance.is_image_compressed:
        # Skip compression if image is already compressed.
        return
    if image := instance.image:
        try:
            compressed = utils.compress_image(image, pixel_width=512)
            # save = False avoids double-saving for efficiency and just
            # assigns the compressed image value to the marker_icon field
            image.save(compressed.name, compressed, save=False)
            instance.is_image_compressed = True
        except utils.CompressionFailed:
            pass
