from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, TemplateView

from .models import Employee


class IndexView(TemplateView):
    """Главная страница — описание проекта + карточки сотрудников."""

    template_name = "employees/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employees"] = Employee.objects.prefetch_related(
            "skills__skill"
        ).filter(is_active=True)
        return context


class EmployeeListView(ListView):
    """Список всех сотрудников."""

    model = Employee
    template_name = "employees/list.html"
    context_object_name = "employees"
    queryset = Employee.objects.prefetch_related("skills__skill").filter(is_active=True)


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Подробная карточка сотрудника — только для авторизованных."""

    model = Employee
    template_name = "employees/detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        return Employee.objects.prefetch_related("skills__skill", "photos").filter(
            is_active=True
        )
