from django.contrib import admin

from .models import Workplace


@admin.register(Workplace)
class WorkplaceAdmin(admin.ModelAdmin):
    list_display = ("desk_number", "room", "has_monitor")
    list_filter = ("has_monitor",)
    search_fields = ("desk_number", "room")
