from typing import Any, Dict

import django
from django.db.models import (
    ForeignKey,
    ManyToManyField,
    ManyToManyRel,
    ManyToOneRel,
    Model,
)

from rush.logger import get_logger

logger = get_logger()


class BaseModel(Model):
    """
    Base model for RUSH that adds:
        1. Serialization support for logging model changes.
    """

    class Meta:
        abstract = True

    def log_changes_dict(self) -> Dict[str, Any]:
        """
        Dict of primitive Django fieldnames --> values for the model. Anything more
        complicated for logs (e.g., foreign keys) needs to be specified by overriding
        this function.
        """
        self.refresh_from_db()
        data = {}
        for field in self._meta.get_fields():
            if not isinstance(field, (ManyToManyRel, ManyToManyField, ManyToOneRel, ForeignKey)):
                # Handle primitive field types and FileField / ImageField
                if hasattr(self, field.name):
                    value = getattr(self, field.name)
                    if hasattr(value, "url"):
                        # Use url string for FileField / ImageField.
                        value = value.url if value else None
                    data[field.name] = value
        return data
