from django.contrib import admin
from .models import Feedback
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    # ❌ VULNERABLE: message rendered raw in admin change view (Stored XSS V-16)
