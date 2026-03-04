from django.contrib.auth import get_user_model
from rest_framework import mixins, permissions, viewsets
from rest_framework.parsers import FormParser, MultiPartParser

from .models import Collect, Payment
from .serializers import (CollectDetailSerializer, CollectListSerializer,
                          PaymentSerializer, UserCreateSerializer,
                          UserSerializer)

User = get_user_model()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешить изменение только автору объекта."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        author = getattr(obj, "author", None) or getattr(obj, "user", None)
        return author == request.user


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """CRUD для пользователей (создание открытое, остальное — авторизованным)."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class CollectViewSet(viewsets.ModelViewSet):
    """CRUD для сборов."""

    queryset = (
        Collect.objects.select_related("author")
        .prefetch_related("payments__user")
        .order_by("-created_at")
    )
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CollectDetailSerializer
        return CollectListSerializer


class PaymentViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Создание и просмотр платежей (без редактирования и удаления)."""

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Payment.objects.select_related("user", "collect")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )
