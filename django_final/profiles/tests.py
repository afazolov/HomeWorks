from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DateInvite, Like, ViewHistory

User = get_user_model()


def make_user(email, username, **kwargs):
    return User.objects.create_user(
        email=email,
        username=username,
        password="testpass123",
        first_name="Тест",
        last_name="Тестов",
        **kwargs,
    )


class LikeDislikeTests(APITestCase):
    def setUp(self):
        self.alice = make_user("alice@test.com", "alice")
        self.bob = make_user("bob@test.com", "bob")
        self.client.force_authenticate(user=self.alice)

    def _like(self, to_user, action="like"):
        url = reverse("like-list")
        return self.client.post(url, {"to_user_id": to_user.pk, "action": action})

    # ── Базовые тесты лайка ─────────────────────────────────────────────

    def test_like_creates_record(self):
        response = self._like(self.bob, "like")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Like.objects.filter(
                from_user=self.alice, to_user=self.bob, action="like"
            ).exists()
        )

    def test_dislike_creates_record(self):
        response = self._like(self.bob, "dislike")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Like.objects.filter(
                from_user=self.alice, to_user=self.bob, action="dislike"
            ).exists()
        )

    def test_cannot_like_self(self):
        response = self._like(self.alice)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_like_updates_likes_count(self):
        self._like(self.bob, "like")
        self.bob.refresh_from_db()
        self.assertEqual(self.bob.likes_count, 1)

    def test_dislike_does_not_increment_likes_count(self):
        self._like(self.bob, "dislike")
        self.bob.refresh_from_db()
        self.assertEqual(self.bob.likes_count, 0)

    def test_change_like_to_dislike(self):
        self._like(self.bob, "like")
        self._like(self.bob, "dislike")
        self.assertEqual(
            Like.objects.filter(from_user=self.alice, to_user=self.bob).count(), 1
        )
        like = Like.objects.get(from_user=self.alice, to_user=self.bob)
        self.assertEqual(like.action, "dislike")

    def test_liked_users_list(self):
        self._like(self.bob, "like")
        url = reverse("user-liked-users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_disliked_users_list(self):
        self._like(self.bob, "dislike")
        url = reverse("user-disliked-users")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_like_history(self):
        # Bob лайкает alice
        self.client.force_authenticate(user=self.bob)
        self._like(self.alice, "like")
        self.client.force_authenticate(user=self.alice)
        url = reverse("user-like-history")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_mutual_likes(self):
        # Alice лайкает Bob
        self._like(self.bob, "like")
        # Bob лайкает Alice
        self.client.force_authenticate(user=self.bob)
        self._like(self.alice, "like")
        # Alice проверяет взаимные лайки
        self.client.force_authenticate(user=self.alice)
        url = reverse("user-mutual-likes")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class DateInviteTests(APITestCase):
    def setUp(self):
        self.alice = make_user("alice2@test.com", "alice2")
        self.bob = make_user("bob2@test.com", "bob2")
        # Создать взаимный лайк
        Like.objects.create(from_user=self.alice, to_user=self.bob, action="like")
        Like.objects.create(from_user=self.bob, to_user=self.alice, action="like")
        self.client.force_authenticate(user=self.alice)

    def test_invite_requires_mutual_like(self):
        charlie = make_user("charlie@test.com", "charlie")
        url = reverse("invite-list")
        response = self.client.post(url, {"to_user_id": charlie.pk, "message": "Hi"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invite_with_mutual_like_succeeds(self):
        url = reverse("invite-list")
        response = self.client.post(
            url, {"to_user_id": self.bob.pk, "message": "Привет!"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_respond_to_invite_accept(self):
        invite = DateInvite.objects.create(
            from_user=self.alice, to_user=self.bob, message="Привет"
        )
        self.client.force_authenticate(user=self.bob)
        url = reverse("invite-respond", args=[invite.pk])
        response = self.client.post(url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.status, "accepted")

    def test_respond_to_invite_decline(self):
        invite = DateInvite.objects.create(
            from_user=self.alice, to_user=self.bob, message="Привет"
        )
        self.client.force_authenticate(user=self.bob)
        url = reverse("invite-respond", args=[invite.pk])
        response = self.client.post(url, {"status": "declined"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.refresh_from_db()
        self.assertEqual(invite.status, "declined")

    def test_only_recipient_can_respond(self):
        invite = DateInvite.objects.create(
            from_user=self.alice, to_user=self.bob, message="Привет"
        )
        # alice пытается ответить на своё же приглашение
        url = reverse("invite-respond", args=[invite.pk])
        response = self.client.post(url, {"status": "accepted"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ViewHistoryTests(APITestCase):
    def setUp(self):
        self.alice = make_user("alice3@test.com", "alice3")
        self.bob = make_user("bob3@test.com", "bob3", is_profile_public=True)
        self.client.force_authenticate(user=self.alice)

    def test_view_history_recorded(self):
        ViewHistory.objects.create(viewer=self.alice, viewed=self.bob)
        url = reverse("user-view-history")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class RegistrationTests(APITestCase):
    def test_register_new_user(self):
        url = reverse("register-list")
        data = {
            "email": "new@test.com",
            "username": "newuser",
            "first_name": "Новый",
            "last_name": "Пользователь",
            "password": "strongpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@test.com").exists())

    def test_duplicate_email_rejected(self):
        make_user("dup@test.com", "dupuser")
        url = reverse("register-list")
        data = {
            "email": "dup@test.com",
            "username": "another",
            "first_name": "Дубль",
            "last_name": "Дублев",
            "password": "strongpass123",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
