from django.urls import path
from .views import BusListCreateView, update_bus, get_bus_schedule

urlpatterns = [
    path('', BusListCreateView.as_view()),          # /api/buses/ (GET, POST)
    path('<int:bus_id>/', update_bus),              # /api/buses/{id}/ (PUT, PATCH)
    path('<str:bus_no>/schedule/', get_bus_schedule), # /api/buses/100/schedule/
]
