import os

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone

# Ключевые слова в названии навыка, обозначающие разработчиков и тестировщиков.
_DEV_KEYWORDS = ("backend", "бэкенд", "frontend", "фронтенд", "developer", "разработч")
_QA_KEYWORDS = ("test", "тест", "qa", "тестиров")


def _is_dev(skill_name: str) -> bool:
    low = skill_name.lower()
    return any(kw in low for kw in _DEV_KEYWORDS)


def _is_qa(skill_name: str) -> bool:
    low = skill_name.lower()
    return any(kw in low for kw in _QA_KEYWORDS)


class Employee(AbstractUser):
    """Пользовательская модель сотрудника — расширяет стандартного User.

    Связь «один к одному» с рабочим местом задаётся здесь через
    OneToOneField на модель Workplace (nullable — стол может быть не назначен).
    """

    class Gender(models.TextChoices):
        MALE = "M", "Мужской"
        FEMALE = "F", "Женский"
        OTHER = "O", "Другой"

    patronymic = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Отчество",
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        blank=True,
        verbose_name="Пол",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    workplace = models.OneToOneField(
        "workplaces.Workplace",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee",
        verbose_name="Рабочее место",
    )
    hired_at = models.DateField(
        null=True,
        blank=True,
        default=timezone.now,
        verbose_name="Дата приёма на работу",
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        full_name = " ".join(
            part for part in [self.last_name, self.first_name, self.patronymic] if part
        )
        return full_name or self.username

    def _get_role(self):
        """Вернуть 'dev', 'qa' или None в зависимости от навыков сотрудника."""
        skill_names = list(
            self.skills.select_related("skill").values_list("skill__name", flat=True)
        )
        if any(_is_dev(n) for n in skill_names):
            return "dev"
        if any(_is_qa(n) for n in skill_names):
            return "qa"
        return None

    def clean(self):
        super().clean()
        if not self.workplace_id:
            return
        self._validate_desk_adjacency()

    def _validate_desk_adjacency(self):
        """Тестировщики и разработчики не могут сидеть за соседними столами."""
        my_role = self._get_role()
        if my_role is None:
            return

        opposite = "qa" if my_role == "dev" else "dev"
        my_desk = self.workplace.desk_number
        adjacent = [my_desk - 1, my_desk + 1]

        # Ищем сотрудников на соседних столах с противоположной ролью.
        neighbors = (
            Employee.objects.exclude(pk=self.pk)
            .filter(
                is_active=True,
                workplace__desk_number__in=adjacent,
            )
            .prefetch_related("skills__skill")
        )

        for neighbor in neighbors:
            neighbor_role = neighbor._get_role()
            if neighbor_role == opposite:
                raise ValidationError(
                    f"Нельзя посадить {self._role_display(my_role)} за стол №{my_desk}: "
                    f"рядом (стол №{neighbor.workplace.desk_number}) сидит "
                    f"{self._role_display(opposite)} — {neighbor}."
                )

    @staticmethod
    def _role_display(role: str) -> str:
        return "разработчика" if role == "dev" else "тестировщика"


class Skill(models.Model):
    """Навык (тип): фронтенд, бэкенд, тестирование и т.д."""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название навыка",
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EmployeeSkill(models.Model):
    """Связь сотрудника с навыком и уровнем его освоения (1–10)."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="Сотрудник",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="employee_skills",
        verbose_name="Навык",
    )
    level = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="Уровень (1–10)",
    )

    class Meta:
        verbose_name = "Навык сотрудника"
        verbose_name_plural = "Навыки сотрудников"
        unique_together = [("employee", "skill")]
        ordering = ["-level"]

    def __str__(self):
        return f"{self.employee} — {self.skill} ({self.level}/10)"


class EmployeePhoto(models.Model):
    """Фотография сотрудника (галерея — у одного может быть много)."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Сотрудник",
    )
    image = models.ImageField(
        upload_to="employees/photos/",
        verbose_name="Изображение",
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядковый номер",
        help_text="Меньшее число — выше в галерее.",
    )

    class Meta:
        verbose_name = "Фото сотрудника"
        verbose_name_plural = "Фото сотрудников"
        ordering = ["order", "pk"]

    def __str__(self):
        return f"Фото {self.order} — {self.employee}"


@receiver(post_delete, sender=EmployeePhoto)
def delete_photo_file(sender, instance, **kwargs):
    """Удалить файл изображения с диска при удалении записи из БД."""
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)
