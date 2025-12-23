from django.urls import path
from .views import BusListCreateView

urlpatterns = [
    path('', BusListCreateView.as_view()),
]
