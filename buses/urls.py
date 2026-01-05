from django.urls import path
from .views import BusListCreateView, update_bus

urlpatterns = [
    path('', BusListCreateView.as_view()),          # /api/buses/ (GET, POST)
    path('<int:bus_id>/', update_bus),              # /api/buses/{id}/ (PUT, PATCH)
]
