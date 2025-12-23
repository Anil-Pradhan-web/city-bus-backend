from django.urls import path
from .views import RouteListCreateView

urlpatterns = [
    path('', RouteListCreateView.as_view()),
]
