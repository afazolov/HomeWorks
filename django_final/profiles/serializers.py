from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import DateInvite, Like, Photo, ViewHistory

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "password",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже зарегистрирован.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["id", "image", "is_main", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class UserPublicSerializer(serializers.ModelSerializer):
    """Публичный профиль — учитывает настройки приватности."""

    main_photo = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "gender",
            "age",
            "city",
            "interests",
            "status",
            "likes_count",
            "main_photo",
        ]

    def get_main_photo(self, obj):
        photo = obj.photos.filter(is_main=True).first() or obj.photos.first()
        if photo:
            request = self.context.get("request")
            return (
                request.build_absolute_uri(photo.image.url)
                if request
                else photo.image.url
            )
        return None

    def get_age(self, obj):
        return obj.age if obj.show_age else None

    def get_city(self, obj):
        return obj.city if obj.show_city else None


class UserProfileSerializer(serializers.ModelSerializer):
    """Полный профиль (для владельца)."""

    photos = PhotoSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "patronymic",
            "gender",
            "age",
            "city",
            "interests",
            "status",
            "likes_count",
            "is_profile_public",
            "show_age",
            "show_city",
            "photos",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "likes_count", "date_joined"]

    def validate_age(self, value):
        if value is not None and value < 18:
            raise serializers.ValidationError("Возраст должен быть не менее 18 лет.")
        return value


class LikeSerializer(serializers.ModelSerializer):
    from_user = UserPublicSerializer(read_only=True)
    to_user = UserPublicSerializer(read_only=True)
    to_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="to_user", write_only=True
    )

    class Meta:
        model = Like
        fields = ["id", "from_user", "to_user", "to_user_id", "action", "created_at"]
        read_only_fields = ["id", "from_user", "created_at"]

    def validate(self, attrs):
        request = self.context["request"]
        to_user = attrs["to_user"]
        if to_user == request.user:
            raise serializers.ValidationError("Нельзя лайкать самого себя.")
        return attrs

    def create(self, validated_data):
        validated_data["from_user"] = self.context["request"].user
        # Обновить или создать (upsert)
        like, created = Like.objects.update_or_create(
            from_user=validated_data["from_user"],
            to_user=validated_data["to_user"],
            defaults={"action": validated_data["action"]},
        )
        # Обновить счётчик лайков у получателя
        to_user = validated_data["to_user"]
        to_user.likes_count = to_user.received_likes.filter(
            action=Like.Action.LIKE
        ).count()
        to_user.save(update_fields=["likes_count"])
        return like


class ViewHistorySerializer(serializers.ModelSerializer):
    viewed = UserPublicSerializer(read_only=True)

    class Meta:
        model = ViewHistory
        fields = ["id", "viewed", "viewed_at"]
        read_only_fields = ["id", "viewed", "viewed_at"]


class DateInviteSerializer(serializers.ModelSerializer):
    from_user = UserPublicSerializer(read_only=True)
    to_user = UserPublicSerializer(read_only=True)
    to_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="to_user", write_only=True
    )

    class Meta:
        model = DateInvite
        fields = [
            "id",
            "from_user",
            "to_user",
            "to_user_id",
            "message",
            "contact_info",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "from_user", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context["request"]
        to_user = attrs["to_user"]
        if to_user == request.user:
            raise serializers.ValidationError(
                "Нельзя отправить приглашение самому себе."
            )
        # Проверить взаимный лайк
        from_user = request.user
        mutual = (
            Like.objects.filter(
                from_user=from_user, to_user=to_user, action=Like.Action.LIKE
            ).exists()
            and Like.objects.filter(
                from_user=to_user, to_user=from_user, action=Like.Action.LIKE
            ).exists()
        )
        if not mutual:
            raise serializers.ValidationError(
                "Приглашение можно отправить только при взаимном лайке."
            )
        return attrs

    def create(self, validated_data):
        validated_data["from_user"] = self.context["request"].user
        return super().create(validated_data)
