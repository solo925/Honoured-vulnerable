"""dashboard/models.py"""
from django.db import models


class Customer(models.Model):
    """Target model for the XXE XML import exercise."""
    name  = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


class AuditLog(models.Model):
    """
    Stores audit entries for dashboard actions.
    Written by the ping view – useful for observing command-injection results.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    user      = models.CharField(max_length=150)
    action    = models.TextField()
    result    = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} @ {self.timestamp:%Y-%m-%d %H:%M}"
