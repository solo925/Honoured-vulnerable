from django.contrib import admin
from .models import Customer, AuditLog
admin.site.register(Customer)
admin.site.register(AuditLog)
