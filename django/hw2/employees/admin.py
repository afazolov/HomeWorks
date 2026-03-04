from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Employee, EmployeeSkill, Skill


class EmployeeSkillInline(admin.TabularInline):
    """Навыки сотрудника — вложенная таблица на странице сотрудника."""

    model = EmployeeSkill
    extra = 1
    min_num = 0


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    inlines = [EmployeeSkillInline]

    # Добавляем новые поля к стандартным fieldsets UserAdmin
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительно",
            {
                "fields": (
                    "patronymic",
                    "gender",
                    "description",
                    "workplace",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Дополнительно",
            {
                "fields": (
                    "patronymic",
                    "gender",
                    "description",
                    "workplace",
                )
            },
        ),
    )

    list_display = ("username", "last_name", "first_name", "gender", "workplace")
    list_filter = ("gender", "is_staff", "is_active")
    search_fields = ("username", "last_name", "first_name", "patronymic")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(EmployeeSkill)
class EmployeeSkillAdmin(admin.ModelAdmin):
    list_display = ("employee", "skill", "level")
    list_filter = ("skill",)
    search_fields = ("employee__username", "employee__last_name", "skill__name")
