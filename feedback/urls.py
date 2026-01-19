from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet, ContactMessageViewSet

router = DefaultRouter()
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'contact', ContactMessageViewSet, basename='contact')

urlpatterns = [
    path('', include(router.urls)),
]
