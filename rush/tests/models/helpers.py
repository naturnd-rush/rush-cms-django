import tempfile
from contextlib import ExitStack
from functools import wraps
from unittest.mock import Mock

from django.test import override_settings


class FakeFile(Mock):

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self) -> str:
        return f'<FakeFile: "{self.name}">'


def use_tmp_media_dir(func):
    """
    Tell Django to use a temporary MEDIA_ROOT directory which is cleaned up
    after the decorated function finishes executing.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        with ExitStack() as stack:
            cm1 = tempfile.TemporaryDirectory()
            dirname = stack.enter_context(cm1)
            cm2 = override_settings(MEDIA_ROOT=dirname)
            # Pylance doesn't like override_settings because of BaseException in __exit__
            stack.enter_context(cm2)  # type: ignore[arg-type]
            return func(*args, **kwargs)

    return wrapper
