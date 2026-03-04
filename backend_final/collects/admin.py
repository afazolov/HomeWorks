from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Collect, Payment, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Collect)
class CollectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "occasion",
        "current_amount",
        "target_amount",
        "created_at",
    ]
    list_filter = ["occasion"]
    search_fields = ["title", "author__username"]
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "collect", "amount", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "collect__title"]
