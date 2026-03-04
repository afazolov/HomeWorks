from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Collect, Payment

User = get_user_model()


class UserAPITests(APITestCase):
    def test_create_user(self):
        url = reverse("user-list")
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_list_users_requires_auth(self):
        url = reverse("user-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CollectAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="author", password="pass123")
        self.other = User.objects.create_user(username="other", password="pass123")
        self.client.force_authenticate(user=self.user)

    def _create_collect(self, **kwargs):
        defaults = {
            "title": "Тест сбор",
            "occasion": "birthday",
            "target_amount": "10000.00",
        }
        defaults.update(kwargs)
        url = reverse("collect-list")
        return self.client.post(url, defaults)

    def test_create_collect(self):
        response = self._create_collect()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collect.objects.count(), 1)
        collect = Collect.objects.first()
        self.assertEqual(collect.author, self.user)

    def test_list_collects_anonymous(self):
        self.client.logout()
        Collect.objects.create(author=self.user, title="Сбор 1", occasion="other")
        url = reverse("collect-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_collect_only_author(self):
        collect = Collect.objects.create(
            author=self.user, title="Мой сбор", occasion="other"
        )
        self.client.force_authenticate(user=self.other)
        url = reverse("collect-detail", args=[collect.pk])
        response = self.client.patch(url, {"title": "Чужой сбор"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_collect_by_author(self):
        collect = Collect.objects.create(
            author=self.user, title="Удаляемый", occasion="other"
        )
        url = reverse("collect-detail", args=[collect.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Collect.objects.count(), 0)

    def test_invalid_target_amount(self):
        response = self._create_collect(target_amount="-100")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PaymentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="payer", password="pass123")
        self.author = User.objects.create_user(username="author", password="pass123")
        self.collect = Collect.objects.create(
            author=self.author,
            title="Сбор для платежей",
            occasion="other",
            target_amount=Decimal("5000.00"),
        )
        self.client.force_authenticate(user=self.user)

    def test_create_payment_updates_collect(self):
        url = reverse("payment-list")
        data = {"collect": self.collect.pk, "amount": "500.00"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.collect.refresh_from_db()
        self.assertEqual(self.collect.current_amount, Decimal("500.00"))
        self.assertEqual(self.collect.contributors_count, 1)

    def test_payment_zero_amount_rejected(self):
        url = reverse("payment-list")
        data = {"collect": self.collect.pk, "amount": "0"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_negative_amount_rejected(self):
        url = reverse("payment-list")
        data = {"collect": self.collect.pk, "amount": "-100"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_requires_auth(self):
        self.client.logout()
        url = reverse("payment-list")
        data = {"collect": self.collect.pk, "amount": "100.00"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
