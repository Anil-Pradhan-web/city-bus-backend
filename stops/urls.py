from django.urls import path
from .views import StopListCreateView

urlpatterns = [
    path('', StopListCreateView.as_view()),
]
