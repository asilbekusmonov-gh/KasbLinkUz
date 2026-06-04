from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.views import (
    UserViewSet, WorkerProfileViewSet, PortfolioViewSet,
    CategoryListApi, ServiceViewSet, ConversationViewSet,
    MessageViewSet, OrderViewSet, OrderImageViewSet,
    ReviewViewSet, ReviewImageViewSet, FavouriteViewSet, RegisterView
)

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'worker-profiles', WorkerProfileViewSet, basename='worker-profile')
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-images', OrderImageViewSet, basename='order-image')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'review-images', ReviewImageViewSet, basename='review-image')
router.register(r'favourites', FavouriteViewSet, basename='favourite')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryListApi.as_view()),
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
