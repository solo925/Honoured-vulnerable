"""accounts/models.py"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Minimal custom user model.
    Extend here if you need extra fields.
    """
    pass
