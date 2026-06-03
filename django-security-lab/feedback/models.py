"""feedback/models.py"""

from django.db import models


class Feedback(models.Model):
    """
    Public feedback / contact form.
    The message field stores raw user input – rendered unescaped in the admin
    list view and in the feedback wall (stored XSS, V-16).
    """
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    message    = models.TextField()      # ← raw HTML stored here
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} – {self.created_at:%Y-%m-%d}"
