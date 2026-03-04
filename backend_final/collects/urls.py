from rest_framework.routers import DefaultRouter

from .views import CollectViewSet, PaymentViewSet, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("collects", CollectViewSet, basename="collect")
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = router.urls
