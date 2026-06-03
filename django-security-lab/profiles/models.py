"""profiles/models.py"""

from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    # ── [V-13] Stored XSS: bio is rendered unescaped in the template ──────────
    bio     = models.TextField(blank=True)
    website = models.URLField(blank=True)
    avatar  = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
