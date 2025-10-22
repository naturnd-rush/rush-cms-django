from django.core.exceptions import ValidationError


class DuplicateSlug(ValidationError):
    """
    The slug on this instance is duplicated by another Question in the database.
    """

    ...
