from django.db import models


class Workplace(models.Model):
    """Рабочее место сотрудника."""

    desk_number = models.PositiveIntegerField(
        unique=True,
        verbose_name="Номер стола",
    )
    room = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Кабинет / комната",
    )
    has_monitor = models.BooleanField(
        default=True,
        verbose_name="Монитор",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Дополнительная информация",
    )

    class Meta:
        verbose_name = "Рабочее место"
        verbose_name_plural = "Рабочие места"
        ordering = ["desk_number"]

    def __str__(self):
        return f"Стол №{self.desk_number}"
