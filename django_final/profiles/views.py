from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import DateInvite, Like, Photo, ViewHistory
from .serializers import (DateInviteSerializer, LikeSerializer,
                          PhotoSerializer, RegisterSerializer,
                          UserProfileSerializer, UserPublicSerializer,
                          ViewHistorySerializer)

User = get_user_model()


class RegisterView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Регистрация нового пользователя."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.GenericViewSet):
    """Профиль текущего пользователя и просмотр чужих профилей."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            User.objects.filter(is_active=True, is_profile_public=True)
            .prefetch_related("photos")
            .exclude(pk=self.request.user.pk)
        )

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        """Получить или обновить свой профиль."""
        if request.method == "GET":
            serializer = UserProfileSerializer(
                request.user, context={"request": request}
            )
            return Response(serializer.data)
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="random")
    def random_profile(self, request):
        """Случайный профиль с фильтрацией по полу, возрасту, городу, статусу."""
        qs = self.get_queryset()

        gender = request.query_params.get("gender")
        city = request.query_params.get("city")
        status_filter = request.query_params.get("status")
        age_min = request.query_params.get("age_min", type=int)
        age_max = request.query_params.get("age_max", type=int)

        if gender:
            qs = qs.filter(gender=gender)
        if city:
            qs = qs.filter(city__icontains=city)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if age_min is not None:
            qs = qs.filter(age__gte=age_min)
        if age_max is not None:
            qs = qs.filter(age__lte=age_max)

        # Исключить уже просмотренных и лайкнутых/дизлайкнутых
        seen_ids = ViewHistory.objects.filter(viewer=request.user).values_list(
            "viewed_id", flat=True
        )
        rated_ids = Like.objects.filter(from_user=request.user).values_list(
            "to_user_id", flat=True
        )
        qs = qs.exclude(pk__in=seen_ids).exclude(pk__in=rated_ids)

        profile = qs.order_by("?").first()
        if not profile:
            return Response(
                {"detail": "Нет подходящих профилей."},
                status=status.HTTP_204_NO_CONTENT,
            )

        # Записать в историю просмотров
        ViewHistory.objects.update_or_create(viewer=request.user, viewed=profile)

        serializer = UserPublicSerializer(profile, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="profile")
    def view_profile(self, request, pk=None):
        """Просмотр конкретного профиля (с записью в историю)."""
        profile = self.get_queryset().filter(pk=pk).first()
        if not profile:
            return Response(
                {"detail": "Профиль не найден."}, status=status.HTTP_404_NOT_FOUND
            )
        ViewHistory.objects.update_or_create(viewer=request.user, viewed=profile)
        serializer = UserPublicSerializer(profile, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="liked")
    def liked_users(self, request):
        """Список понравившихся (которым поставил лайк)."""
        user_ids = Like.objects.filter(
            from_user=request.user, action=Like.Action.LIKE
        ).values_list("to_user_id", flat=True)
        qs = User.objects.filter(pk__in=user_ids).prefetch_related("photos")
        serializer = UserPublicSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="disliked")
    def disliked_users(self, request):
        """Список непонравившихся (которым поставил дизлайк)."""
        user_ids = Like.objects.filter(
            from_user=request.user, action=Like.Action.DISLIKE
        ).values_list("to_user_id", flat=True)
        qs = User.objects.filter(pk__in=user_ids).prefetch_related("photos")
        serializer = UserPublicSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="like-history")
    def like_history(self, request):
        """История лайков профиля — кто лайкнул меня."""
        likes = (
            Like.objects.filter(to_user=request.user, action=Like.Action.LIKE)
            .select_related("from_user")
            .order_by("-created_at")
        )
        serializer = LikeSerializer(likes, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="view-history")
    def view_history(self, request):
        """История просмотренных профилей."""
        history = (
            ViewHistory.objects.filter(viewer=request.user)
            .select_related("viewed")
            .prefetch_related("viewed__photos")
            .order_by("-viewed_at")
        )
        serializer = ViewHistorySerializer(
            history, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="mutual-likes")
    def mutual_likes(self, request):
        """Список взаимных лайков (потенциальные пары)."""
        i_liked = set(
            Like.objects.filter(
                from_user=request.user, action=Like.Action.LIKE
            ).values_list("to_user_id", flat=True)
        )
        liked_me = set(
            Like.objects.filter(
                to_user=request.user, action=Like.Action.LIKE
            ).values_list("from_user_id", flat=True)
        )
        mutual_ids = i_liked & liked_me
        qs = User.objects.filter(pk__in=mutual_ids).prefetch_related("photos")
        serializer = UserPublicSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)


class PhotoViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Управление фотогалереей пользователя."""

    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return Photo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="set-main")
    def set_main(self, request, pk=None):
        """Установить фото как заглавное."""
        photo = self.get_object()
        Photo.objects.filter(user=request.user, is_main=True).update(is_main=False)
        photo.is_main = True
        photo.save(update_fields=["is_main"])
        return Response({"detail": "Заглавная фотография обновлена."})


class LikeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Лайки и дизлайки."""

    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Like.objects.filter(from_user=self.request.user)
            .select_related("from_user", "to_user")
            .order_by("-created_at")
        )


class DateInviteViewSet(viewsets.ModelViewSet):
    """Приглашения на свидание."""

    serializer_class = DateInviteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            (
                DateInvite.objects.filter(from_user=self.request.user)
                | DateInvite.objects.filter(to_user=self.request.user)
            )
            .select_related("from_user", "to_user")
            .order_by("-created_at")
        )

    @action(detail=True, methods=["post"], url_path="respond")
    def respond(self, request, pk=None):
        """Принять или отклонить приглашение."""
        invite = self.get_object()
        if invite.to_user != request.user:
            return Response(
                {"detail": "Вы не являетесь получателем этого приглашения."},
                status=status.HTTP_403_FORBIDDEN,
            )
        new_status = request.data.get("status")
        if new_status not in (DateInvite.Status.ACCEPTED, DateInvite.Status.DECLINED):
            return Response(
                {"detail": "Статус должен быть 'accepted' или 'declined'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        invite.status = new_status
        invite.save(update_fields=["status", "updated_at"])
        serializer = self.get_serializer(invite)
        return Response(serializer.data)
