from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


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

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        full_name = " ".join(
            part for part in [self.last_name, self.first_name, self.patronymic] if part
        )
        return full_name or self.username


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
