from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import OuterRef, Prefetch, Subquery
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView

from .models import Employee, EmployeePhoto


def _employee_qs_with_photo():
    """Базовый queryset: активные сотрудники + навыки + первое фото (subquery)."""
    first_photo = EmployeePhoto.objects.filter(employee=OuterRef("pk")).order_by(
        "order", "pk"
    )
    return (
        Employee.objects.filter(is_active=True)
        .select_related("workplace")
        .prefetch_related("skills__skill")
        .annotate(first_photo_url=Subquery(first_photo.values("image")[:1]))
    )


class IndexView(TemplateView):
    """Главная страница — описание проекта + 4 последних нанятых сотрудника."""

    template_name = "employees/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = _employee_qs_with_photo()
        context["total_employees"] = qs.count()
        context["employees"] = qs.order_by("-hired_at", "-date_joined")[:4]
        context["today"] = timezone.now().date()
        return context


class EmployeeListView(ListView):
    """Список всех сотрудников с пагинацией по 10 на странице."""

    template_name = "employees/list.html"
    context_object_name = "employees"
    paginate_by = 10

    def get_queryset(self):
        return _employee_qs_with_photo().order_by("last_name", "first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.now().date()
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """Подробная карточка сотрудника — только для авторизованных."""

    template_name = "employees/detail.html"
    context_object_name = "employee"

    def get_queryset(self):
        return (
            Employee.objects.filter(is_active=True)
            .select_related("workplace")
            .prefetch_related(
                "skills__skill",
                Prefetch(
                    "photos",
                    queryset=EmployeePhoto.objects.order_by("order", "pk"),
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photos = list(self.object.photos.all())
        context["cover_photo"] = photos[0] if photos else None
        context["gallery_photos"] = photos[1:]
        context["today"] = timezone.now().date()
        return context
