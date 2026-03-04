import os

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.dispatch import receiver


class User(AbstractUser):
    """Профиль пользователя платформы знакомств."""

    class Gender(models.TextChoices):
        MALE = "male", "Мужской"
        FEMALE = "female", "Женский"
        OTHER = "other", "Другой"

    class Status(models.TextChoices):
        SEARCHING = "searching", "В поиске"
        BUSY = "busy", "Занят(а)"
        PAUSED = "paused", "Пауза"

    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    patronymic = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        blank=True,
        verbose_name="Пол",
    )
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(18), MaxValueValidator(100)],
        verbose_name="Возраст",
    )
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    interests = models.TextField(blank=True, verbose_name="Увлечения")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.SEARCHING,
        verbose_name="Статус",
    )
    likes_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество лайков"
    )

    # Настройки приватности
    is_profile_public = models.BooleanField(
        default=True, verbose_name="Профиль публичный"
    )
    show_age = models.BooleanField(default=True, verbose_name="Показывать возраст")
    show_city = models.BooleanField(default=True, verbose_name="Показывать город")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Photo(models.Model):
    """Фотография профиля (галерея)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="photos",
        verbose_name="Пользователь",
    )
    image = models.ImageField(
        upload_to="profiles/photos/",
        verbose_name="Изображение",
    )
    is_main = models.BooleanField(default=False, verbose_name="Заглавная фотография")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Загружено")

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"
        ordering = ["-is_main", "-uploaded_at"]

    def __str__(self):
        return f"Фото {self.user} (main={self.is_main})"

    def save(self, *args, **kwargs):
        # Если это фото устанавливается как главное — снять флаг у остальных
        if self.is_main:
            Photo.objects.filter(user=self.user, is_main=True).exclude(
                pk=self.pk
            ).update(is_main=False)
        super().save(*args, **kwargs)


class Like(models.Model):
    """Лайк или дизлайк от одного пользователя другому."""

    class Action(models.TextChoices):
        LIKE = "like", "Лайк"
        DISLIKE = "dislike", "Дизлайк"

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_likes",
        verbose_name="От кого",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_likes",
        verbose_name="Кому",
    )
    action = models.CharField(
        max_length=10,
        choices=Action.choices,
        verbose_name="Действие",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Лайк/Дизлайк"
        verbose_name_plural = "Лайки/Дизлайки"
        unique_together = [("from_user", "to_user")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.from_user} → {self.to_user}: {self.action}"


class ViewHistory(models.Model):
    """История просмотренных профилей."""

    viewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="viewed_profiles",
        verbose_name="Смотрел(а)",
    )
    viewed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="profile_views",
        verbose_name="Чей профиль",
    )
    viewed_at = models.DateTimeField(auto_now=True, verbose_name="Дата просмотра")

    class Meta:
        verbose_name = "Просмотр профиля"
        verbose_name_plural = "История просмотров"
        unique_together = [("viewer", "viewed")]
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.viewer} просмотрел {self.viewed}"


class DateInvite(models.Model):
    """Приглашение на свидание / обмен контактами (только для взаимных лайков)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        ACCEPTED = "accepted", "Принято"
        DECLINED = "declined", "Отклонено"

    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_invites",
        verbose_name="Отправитель",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_invites",
        verbose_name="Получатель",
    )
    message = models.TextField(blank=True, verbose_name="Сообщение")
    contact_info = models.CharField(
        max_length=255, blank=True, verbose_name="Контактные данные"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Отправлено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Приглашение на свидание"
        verbose_name_plural = "Приглашения на свидание"
        unique_together = [("from_user", "to_user")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Приглашение от {self.from_user} к {self.to_user} ({self.status})"


# ─── Сигналы удаления файлов ────────────────────────────────────────────────


@receiver(models.signals.post_delete, sender=Photo)
def delete_photo_file(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=Photo)
def delete_old_photo_file(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Photo.objects.get(pk=instance.pk)
    except Photo.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        if os.path.isfile(old.image.path):
            os.remove(old.image.path)
