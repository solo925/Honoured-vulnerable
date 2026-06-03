"""documents/models.py"""

from django.db import models
from django.conf import settings


class Document(models.Model):
    """
    User-uploaded documents.

    Security issues demonstrated here:
      [V-20] No file-type validation (extension or MIME)
      [V-21] Original filename stored and used in download Content-Disposition
      [V-22] Access control based only on a guessable integer PK (IDOR)
    """
    owner       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    title       = models.CharField(max_length=255)
    file        = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Original filename kept for the Content-Disposition header (V-21)
    original_filename = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title
