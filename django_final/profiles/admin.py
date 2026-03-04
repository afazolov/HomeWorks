from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import DateInvite, Like, Photo, User, ViewHistory


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    readonly_fields = ["uploaded_at"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
        "first_name",
        "last_name",
        "gender",
        "age",
        "city",
        "status",
        "likes_count",
    ]
    list_filter = ["gender", "status", "is_profile_public"]
    search_fields = ["email", "first_name", "last_name", "city"]
    inlines = [PhotoInline]
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Профиль",
            {
                "fields": (
                    "patronymic",
                    "gender",
                    "age",
                    "city",
                    "interests",
                    "status",
                    "likes_count",
                    "is_profile_public",
                    "show_age",
                    "show_city",
                )
            },
        ),
    )


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ["from_user", "to_user", "action", "created_at"]
    list_filter = ["action"]
    search_fields = ["from_user__email", "to_user__email"]


@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ["viewer", "viewed", "viewed_at"]
    search_fields = ["viewer__email", "viewed__email"]


@admin.register(DateInvite)
class DateInviteAdmin(admin.ModelAdmin):
    list_display = ["from_user", "to_user", "status", "created_at"]
    list_filter = ["status"]
