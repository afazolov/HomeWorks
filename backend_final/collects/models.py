import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver


class User(AbstractUser):
    """Стандартная модель пользователя."""

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.get_full_name() or self.username


class Collect(models.Model):
    """Групповой денежный сбор."""

    class Occasion(models.TextChoices):
        BIRTHDAY = "birthday", "День рождения"
        WEDDING = "wedding", "Свадьба"
        OTHER = "other", "Другое"

    author = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="collects",
        verbose_name="Автор",
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    occasion = models.CharField(
        max_length=20,
        choices=Occasion.choices,
        default=Occasion.OTHER,
        verbose_name="Повод",
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Целевая сумма",
    )
    current_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="Собрано",
    )
    contributors_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Число участников",
    )
    cover = models.ImageField(
        upload_to="collects/covers/",
        null=True,
        blank=True,
        verbose_name="Обложка",
    )
    end_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата завершения",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Сбор"
        verbose_name_plural = "Сборы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Payment(models.Model):
    """Платёж в рамках сбора."""

    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    collect = models.ForeignKey(
        Collect,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Сбор",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата платежа")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} → {self.collect}: {self.amount}"


@receiver(models.signals.post_delete, sender=Collect)
def delete_cover_on_collect_delete(sender, instance, **kwargs):
    if instance.cover and os.path.isfile(instance.cover.path):
        os.remove(instance.cover.path)


@receiver(models.signals.pre_save, sender=Collect)
def delete_old_cover_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Collect.objects.get(pk=instance.pk)
    except Collect.DoesNotExist:
        return
    if old.cover and old.cover != instance.cover:
        if os.path.isfile(old.cover.path):
            os.remove(old.cover.path)
