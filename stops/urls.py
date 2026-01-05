from django.urls import path
from .views import StopListCreateView, update_stop

urlpatterns = [
    path('', StopListCreateView.as_view()),           # /api/stops/ (GET, POST)
    path('<int:stop_id>/', update_stop),              # /api/stops/{id}/ (PUT, PATCH)
]
