from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Collect, Payment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]
        read_only_fields = ["id"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "user", "collect", "amount", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма платежа должна быть больше нуля.")
        return value

    def validate_collect(self, collect):
        if collect.end_datetime and collect.end_datetime < timezone.now():
            raise serializers.ValidationError("Срок сбора истёк.")
        return collect

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        payment = super().create(validated_data)

        collect = payment.collect
        if (
            not collect.payments.filter(user=payment.user)
            .exclude(pk=payment.pk)
            .exists()
        ):
            collect.contributors_count += 1
        collect.current_amount += payment.amount
        collect.save(update_fields=["current_amount", "contributors_count"])

        return payment


class CollectListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Collect
        fields = [
            "id",
            "author",
            "title",
            "occasion",
            "description",
            "target_amount",
            "current_amount",
            "contributors_count",
            "cover",
            "end_datetime",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "current_amount",
            "contributors_count",
            "created_at",
        ]

    def validate_target_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Целевая сумма должна быть больше нуля.")
        return value

    def validate_end_datetime(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError(
                "Дата завершения не может быть в прошлом."
            )
        return value

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CollectDetailSerializer(CollectListSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta(CollectListSerializer.Meta):
        fields = CollectListSerializer.Meta.fields + ["payments", "updated_at"]
