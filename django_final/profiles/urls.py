from rest_framework.routers import DefaultRouter

from .views import (DateInviteViewSet, LikeViewSet, PhotoViewSet, RegisterView,
                    UserViewSet)

router = DefaultRouter()
router.register("register", RegisterView, basename="register")
router.register("users", UserViewSet, basename="user")
router.register("photos", PhotoViewSet, basename="photo")
router.register("likes", LikeViewSet, basename="like")
router.register("invites", DateInviteViewSet, basename="invite")

urlpatterns = router.urls
